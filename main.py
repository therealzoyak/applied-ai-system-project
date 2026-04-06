"""
main.py — CLI demo for PawPal+ algorithmic features.
Run with: python3 main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler, DailySchedule, ScheduledTask

SEP = "=" * 60


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

owner = Owner(name="Jordan", available_minutes=480)

mochi   = Pet(name="Mochi",   species="cat")
biscuit = Pet(name="Biscuit", species="dog")
owner.add_pet(mochi)
owner.add_pet(biscuit)

# Tasks added intentionally out of time-order to demo sorting
biscuit.add_task(Task(title="Evening walk",       duration_minutes=20,  priority="medium", category="walk",        preferred_time="evening",   frequency="daily"))
mochi.add_task  (Task(title="Give heartworm pill", duration_minutes=5,   priority="high",   category="medication",  preferred_time="morning",   frequency="daily"))
biscuit.add_task(Task(title="Vet appointment",     duration_minutes=60,  priority="high",   category="appointment", preferred_time="afternoon", frequency="as_needed"))
mochi.add_task  (Task(title="Brush coat",          duration_minutes=15,  priority="low",    category="grooming",    preferred_time="evening",   frequency="weekly"))
mochi.add_task  (Task(title="Breakfast feeding",   duration_minutes=10,  priority="high",   category="feeding",     preferred_time="morning",   frequency="daily"))
biscuit.add_task(Task(title="Morning walk",        duration_minutes=30,  priority="high",   category="walk",        preferred_time="morning",   frequency="daily"))


# ---------------------------------------------------------------------------
# 1. Sorting tasks by preferred time-of-day
# ---------------------------------------------------------------------------

print(f"\n{SEP}")
print("1. TASKS SORTED BY PREFERRED TIME (morning → afternoon → evening → any)")
print(SEP)
all_tasks = owner.get_all_tasks()
sorted_by_time = Scheduler.sort_tasks_by_time(all_tasks)
for t in sorted_by_time:
    print(f"  [{t.preferred_time:10}]  {t.title} ({t.pet_name})")


# ---------------------------------------------------------------------------
# 2. Filtering tasks
# ---------------------------------------------------------------------------

print(f"\n{SEP}")
print("2. FILTERING")
print(SEP)

# Mark one task complete to make the filter interesting
mochi.tasks[0].mark_complete()   # heartworm pill → done

print("  Pending tasks for Mochi only:")
for t in owner.filter_tasks(pet_name="Mochi", completed=False):
    print(f"    • {t.summary()}")

print("  Completed tasks (all pets):")
for t in owner.filter_tasks(completed=True):
    print(f"    • {t.summary()}")


# ---------------------------------------------------------------------------
# 3. Recurring tasks
# ---------------------------------------------------------------------------

print(f"\n{SEP}")
print("3. RECURRING TASKS")
print(SEP)

daily_task = Task(title="Evening walk", duration_minutes=20, priority="medium",
                  category="walk", preferred_time="evening", frequency="daily")
print(f"  Original:  {daily_task.summary()}")

next_task = daily_task.mark_complete()
print(f"  After mark_complete(): original is now → {daily_task.summary()}")
if next_task:
    print(f"  Next occurrence created → {next_task.summary()}")

weekly_task = Task(title="Bath time", duration_minutes=30, priority="low",
                   category="grooming", preferred_time="afternoon", frequency="weekly")
next_weekly = weekly_task.mark_complete()
print(f"  Weekly task next occurrence → due {next_weekly.due_date if next_weekly else 'n/a'}")

as_needed = Task(title="Emergency vet", duration_minutes=90, priority="high",
                 category="appointment", frequency="as_needed")
print(f"  as_needed task returns: {as_needed.mark_complete()}")


# ---------------------------------------------------------------------------
# 4. Normal schedule (no conflicts expected)
# ---------------------------------------------------------------------------

print(f"\n{SEP}")
print("4. TODAY'S SCHEDULE")
print(SEP)
scheduler = Scheduler(owner=owner)
schedule  = scheduler.generate()
print(schedule.summary())


# ---------------------------------------------------------------------------
# 5. Conflict detection demo
# ---------------------------------------------------------------------------

print(f"\n{SEP}")
print("5. CONFLICT DETECTION")
print(SEP)
print("  Manually overlapping two tasks to trigger the detector...")

fake_schedule = DailySchedule(owner=owner)
task_a = Task(title="Feed Mochi",   duration_minutes=10, priority="high", category="feeding")
task_b = Task(title="Morning walk", duration_minutes=30, priority="high", category="walk")
fake_schedule.scheduled = [
    ScheduledTask(task=task_a, start_minute=0,  reasoning="demo"),   # 8:00–8:10
    ScheduledTask(task=task_b, start_minute=5,  reasoning="demo"),   # 8:05–8:35 → overlaps
]
conflicts = scheduler.detect_conflicts(fake_schedule)
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No conflicts found.")

print()
