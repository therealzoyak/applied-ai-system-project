"""
tests/test_pawpal.py — automated test suite for PawPal+ core logic.
Run with: python -m pytest
"""

from datetime import date, timedelta
import pytest

from pawpal_system import Task, Pet, Owner, Scheduler, DailySchedule


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(title="Walk", duration=20, priority="medium", category="walk",
              preferred_time="any", frequency="daily", due_date=None):
    return Task(
        title=title,
        duration_minutes=duration,
        priority=priority,
        category=category,
        preferred_time=preferred_time,
        frequency=frequency,
        due_date=due_date,
    )


def make_owner_with_tasks(*tasks, available_minutes=480):
    owner = Owner(name="Alex", available_minutes=available_minutes)
    pet = Pet(name="Buddy", species="dog")
    for t in tasks:
        pet.add_task(t)
    owner.add_pet(pet)
    return owner


# ===========================================================================
# 1. Task validation
# ===========================================================================

def test_mark_complete_changes_status():
    """mark_complete() should flip completed from False to True."""
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_invalid_priority_raises():
    with pytest.raises(ValueError, match="priority"):
        Task(title="Bad", duration_minutes=10, priority="urgent")


def test_task_invalid_preferred_time_raises():
    with pytest.raises(ValueError, match="preferred_time"):
        Task(title="Bad", duration_minutes=10, preferred_time="night")


def test_task_zero_duration_raises():
    with pytest.raises(ValueError, match="duration_minutes"):
        Task(title="Bad", duration_minutes=0)


def test_task_negative_duration_raises():
    with pytest.raises(ValueError, match="duration_minutes"):
        Task(title="Bad", duration_minutes=-5)


# ===========================================================================
# 2. Pet task management
# ===========================================================================

def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(name="Mochi", species="cat")
    assert len(pet.tasks) == 0
    pet.add_task(make_task("Breakfast", duration=10, category="feeding"))
    assert len(pet.tasks) == 1
    pet.add_task(make_task("Brush coat", duration=15, category="grooming"))
    assert len(pet.tasks) == 2


def test_add_task_stamps_pet_name():
    """add_task() should set task.pet_name to the pet's name."""
    pet = Pet(name="Luna", species="cat")
    task = make_task("Evening meal")
    pet.add_task(task)
    assert task.pet_name == "Luna"


def test_pet_with_no_tasks_returns_empty_list():
    """A brand-new pet has no tasks."""
    pet = Pet(name="Ghost", species="rabbit")
    assert pet.get_tasks() == []


def test_get_tasks_excludes_completed_by_default():
    pet = Pet(name="Rex", species="dog")
    done_task = make_task("Morning run")
    pending_task = make_task("Evening walk")
    pet.add_task(done_task)
    pet.add_task(pending_task)
    done_task.mark_complete()

    active = pet.get_tasks()
    assert len(active) == 1
    assert active[0].title == "Evening walk"


def test_get_tasks_include_completed():
    pet = Pet(name="Rex", species="dog")
    done_task = make_task("Morning run")
    pet.add_task(done_task)
    done_task.mark_complete()

    all_tasks = pet.get_tasks(include_completed=True)
    assert len(all_tasks) == 1


# ===========================================================================
# 3. Recurrence logic
# ===========================================================================

def test_daily_task_creates_next_day_occurrence():
    """Completing a daily task returns a new task due tomorrow."""
    today = date(2025, 6, 1)
    task = make_task(frequency="daily", due_date=today)
    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False


def test_weekly_task_creates_next_week_occurrence():
    """Completing a weekly task returns a new task due in 7 days."""
    today = date(2025, 6, 1)
    task = make_task(frequency="weekly", due_date=today)
    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)
    assert next_task.completed is False


def test_as_needed_task_returns_none():
    """Completing an as_needed task returns None (no recurrence)."""
    task = make_task(frequency="as_needed")
    result = task.mark_complete()
    assert result is None


def test_recurring_task_preserves_title_and_duration():
    """The next occurrence should keep the same title and duration."""
    today = date(2025, 6, 1)
    task = make_task(title="Medication dose", duration=5, frequency="daily", due_date=today)
    next_task = task.mark_complete()

    assert next_task.title == "Medication dose"
    assert next_task.duration_minutes == 5


# ===========================================================================
# 4. Sorting correctness
# ===========================================================================

def test_sort_tasks_by_time_morning_first():
    """sort_tasks_by_time should order morning < afternoon < evening < any."""
    tasks = [
        make_task("Any task",       preferred_time="any"),
        make_task("Evening task",   preferred_time="evening"),
        make_task("Morning task",   preferred_time="morning"),
        make_task("Afternoon task", preferred_time="afternoon"),
    ]
    sorted_tasks = Scheduler.sort_tasks_by_time(tasks)
    order = [t.preferred_time for t in sorted_tasks]
    assert order == ["morning", "afternoon", "evening", "any"]


def test_sort_tasks_by_time_stable():
    """Two tasks with the same preferred_time keep their relative order."""
    t1 = make_task("First morning",  preferred_time="morning")
    t2 = make_task("Second morning", preferred_time="morning")
    sorted_tasks = Scheduler.sort_tasks_by_time([t1, t2])
    assert sorted_tasks[0].title == "First morning"
    assert sorted_tasks[1].title == "Second morning"


def test_scheduler_generates_chronological_order():
    """The generated schedule should be ordered by start_minute."""
    owner = make_owner_with_tasks(
        make_task("Morning feed", preferred_time="morning"),
        make_task("Evening walk", preferred_time="evening"),
        make_task("Afternoon med", preferred_time="afternoon"),
    )
    schedule = Scheduler(owner).generate()
    start_minutes = [st.start_minute for st in schedule.scheduled]
    assert start_minutes == sorted(start_minutes)


# ===========================================================================
# 5. Conflict detection
# ===========================================================================

def test_no_conflicts_for_non_overlapping_tasks():
    """Sequential tasks with no overlap produce zero conflicts."""
    owner = make_owner_with_tasks(
        make_task("Task A", duration=30),
        make_task("Task B", duration=30),
    )
    schedule = Scheduler(owner).generate()
    assert schedule.conflicts == []


def test_conflict_detected_for_same_start_time():
    """
    Manually place two tasks at the same start minute and confirm
    detect_conflicts flags them.
    """
    from pawpal_system import ScheduledTask

    owner = Owner(name="Test", available_minutes=480)
    task_a = make_task("Task A", duration=30)
    task_b = make_task("Task B", duration=30)

    schedule = DailySchedule(owner=owner)
    schedule.scheduled = [
        ScheduledTask(task=task_a, start_minute=0),
        ScheduledTask(task=task_b, start_minute=0),
    ]
    conflicts = Scheduler(owner).detect_conflicts(schedule)
    assert len(conflicts) == 1
    assert "Task A" in conflicts[0]
    assert "Task B" in conflicts[0]


def test_conflict_detected_for_overlapping_tasks():
    """Tasks that partially overlap (A: 0–30, B: 15–45) should conflict."""
    from pawpal_system import ScheduledTask

    owner = Owner(name="Test", available_minutes=480)
    task_a = make_task("Task A", duration=30)
    task_b = make_task("Task B", duration=30)

    schedule = DailySchedule(owner=owner)
    schedule.scheduled = [
        ScheduledTask(task=task_a, start_minute=0),
        ScheduledTask(task=task_b, start_minute=15),
    ]
    conflicts = Scheduler(owner).detect_conflicts(schedule)
    assert len(conflicts) == 1


def test_no_conflict_for_back_to_back_tasks():
    """Tasks that are back-to-back (A ends exactly when B starts) are fine."""
    from pawpal_system import ScheduledTask

    owner = Owner(name="Test", available_minutes=480)
    task_a = make_task("Task A", duration=30)
    task_b = make_task("Task B", duration=30)

    schedule = DailySchedule(owner=owner)
    schedule.scheduled = [
        ScheduledTask(task=task_a, start_minute=0),   # ends at 30
        ScheduledTask(task=task_b, start_minute=30),  # starts at 30
    ]
    conflicts = Scheduler(owner).detect_conflicts(schedule)
    assert conflicts == []


# ===========================================================================
# 6. Owner filtering
# ===========================================================================

def test_filter_tasks_by_pet_name():
    owner = Owner(name="Sam", available_minutes=480)
    dog = Pet(name="Rex", species="dog")
    cat = Pet(name="Luna", species="cat")
    dog.add_task(make_task("Dog walk"))
    cat.add_task(make_task("Cat feed"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog_tasks = owner.filter_tasks(pet_name="Rex")
    assert all(t.pet_name == "Rex" for t in dog_tasks)
    assert len(dog_tasks) == 1


def test_filter_tasks_by_completed_status():
    owner = Owner(name="Sam", available_minutes=480)
    pet = Pet(name="Rex", species="dog")
    done = make_task("Morning walk")
    pending = make_task("Evening walk")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(pending)
    owner.add_pet(pet)

    completed = owner.filter_tasks(completed=True)
    assert len(completed) == 1
    assert completed[0].title == "Morning walk"

    incomplete = owner.filter_tasks(completed=False)
    assert len(incomplete) == 1
    assert incomplete[0].title == "Evening walk"


# ===========================================================================
# 7. Scheduler — deferred tasks & time constraints
# ===========================================================================

def test_task_deferred_when_no_time_left():
    """A task longer than available time should land in deferred, not scheduled."""
    owner = Owner(name="Busy", available_minutes=10)
    pet = Pet(name="Pip", species="hamster")
    pet.add_task(make_task("Long walk", duration=60))
    owner.add_pet(pet)

    schedule = Scheduler(owner).generate()
    assert len(schedule.scheduled) == 0
    assert len(schedule.deferred) == 1


def test_owner_with_no_pets_produces_empty_schedule():
    """An owner with no pets should produce an empty schedule."""
    owner = Owner(name="Empty", available_minutes=480)
    schedule = Scheduler(owner).generate()
    assert schedule.scheduled == []
    assert schedule.deferred == []


def test_high_priority_task_scheduled_before_low():
    """High-priority tasks should appear before low-priority ones."""
    owner = Owner(name="Alex", available_minutes=480)
    pet = Pet(name="Max", species="dog")
    pet.add_task(make_task("Low task",  priority="low",  preferred_time="any"))
    pet.add_task(make_task("High task", priority="high", preferred_time="any"))
    owner.add_pet(pet)

    schedule = Scheduler(owner).generate()
    titles = [st.task.title for st in schedule.scheduled]
    assert titles.index("High task") < titles.index("Low task")
