"""
PawPal+ — full implementation
"""
from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import Optional

PRIORITY_VALUES = {"high": 3, "medium": 2, "low": 1}
CATEGORY_WEIGHTS = {
    "medication": 5,
    "appointment": 4,
    "feeding": 3,
    "walk": 2,
    "grooming": 1,
    "other": 0,
}

TIME_WINDOWS = {
    "morning":   (0,   240),
    "afternoon": (240, 540),
    "evening":   (540, 720),
    "any":       (0,   720),
}

TIME_WINDOW_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, "any": 3}
DAY_START_HOUR = 8


@dataclass
class Task:
    """A single pet-care activity."""
    title: str
    duration_minutes: int
    priority: str = "medium"
    category: str = "other"
    preferred_time: str = "any"
    frequency: str = "daily"
    completed: bool = False
    pet_name: str = ""
    due_date: Optional[date] = None

    def __post_init__(self) -> None:
        if self.priority not in PRIORITY_VALUES:
            raise ValueError(f"priority must be one of {list(PRIORITY_VALUES)}")
        if self.preferred_time not in TIME_WINDOWS:
            raise ValueError(f"preferred_time must be one of {list(TIME_WINDOWS)}")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be a positive integer")

    @property
    def priority_value(self) -> int:
        return PRIORITY_VALUES[self.priority]

    @property
    def category_weight(self) -> int:
        return CATEGORY_WEIGHTS.get(self.category, 0)

    def sort_key(self) -> tuple:
        return (self.priority_value, self.category_weight)

    def mark_complete(self) -> Optional[Task]:
        self.completed = True
        if self.frequency == "daily":
            next_date = (self.due_date or date.today()) + timedelta(days=1)
        elif self.frequency == "weekly":
            next_date = (self.due_date or date.today()) + timedelta(weeks=1)
        else:
            return None
        return replace(self, completed=False, due_date=next_date)

    def next_occurrence(self) -> Optional[Task]:
        if self.frequency == "daily":
            next_date = (self.due_date or date.today()) + timedelta(days=1)
        elif self.frequency == "weekly":
            next_date = (self.due_date or date.today()) + timedelta(weeks=1)
        else:
            return None
        return replace(self, completed=False, due_date=next_date)

    def summary(self) -> str:
        status = "done" if self.completed else "pending"
        due = f", due {self.due_date}" if self.due_date else ""
        return f"{self.title} ({self.duration_minutes} min, {self.priority}, {self.category}, {status}{due})"


@dataclass
class Pet:
    """Stores pet details and owns a list of care tasks."""
    name: str
    species: str
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self, include_completed: bool = False) -> list[Task]:
        if include_completed:
            return list(self.tasks)
        return [t for t in self.tasks if not t.completed]

    def summary(self) -> str:
        needs = ", ".join(self.special_needs) if self.special_needs else "none"
        return f"{self.name} ({self.species}) | special needs: {needs} | tasks: {len(self.tasks)}"


class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    def __init__(self, name: str, available_minutes: int = 480) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_all_tasks(self, include_completed: bool = False) -> list[Task]:
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks(include_completed=include_completed))
        return all_tasks

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[Task]:
        tasks = self.get_all_tasks(include_completed=True)
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def summary(self) -> str:
        hours, mins = divmod(self.available_minutes, 60)
        pet_names = ", ".join(p.name for p in self.pets) if self.pets else "none"
        return f"{self.name} | {hours}h {mins:02d}m available | pets: {pet_names}"


class ScheduledTask:
    """A Task that has been placed into a concrete time slot."""

    def __init__(self, task: Task, start_minute: int, reasoning: str = "") -> None:
        self.task = task
        self.start_minute = start_minute
        self.reasoning = reasoning

    @property
    def end_minute(self) -> int:
        return self.start_minute + self.task.duration_minutes

    def _minute_to_clock(self, minute: int) -> str:
        total = DAY_START_HOUR * 60 + minute
        h, m = divmod(total, 60)
        suffix = "AM" if h < 12 else "PM"
        h12 = h if 1 <= h <= 12 else (h - 12 if h > 12 else 12)
        return f"{h12}:{m:02d} {suffix}"

    @property
    def start_time_str(self) -> str:
        return self._minute_to_clock(self.start_minute)

    @property
    def end_time_str(self) -> str:
        return self._minute_to_clock(self.end_minute)

    def __str__(self) -> str:
        pet_label = f" [{self.task.pet_name}]" if self.task.pet_name else ""
        return (
            f"[{self.start_time_str} – {self.end_time_str}]{pet_label} "
            f"{self.task.title} ({self.task.duration_minutes} min, {self.task.priority})\n"
            f"  → {self.reasoning}"
        )


class DailySchedule:
    """The result produced by Scheduler.generate()."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.scheduled: list[ScheduledTask] = []
        self.deferred: list[Task] = []
        self.conflicts: list[str] = []

    @property
    def total_minutes_used(self) -> int:
        return sum(st.task.duration_minutes for st in self.scheduled)

    def summary(self) -> str:
        lines = [
            f"Daily Schedule — {self.owner.name}'s pets",
            f"Time used: {self.total_minutes_used} / {self.owner.available_minutes} min",
            "=" * 60,
        ]
        if self.scheduled:
            for st in self.scheduled:
                lines.append(str(st))
        else:
            lines.append("  (no tasks scheduled)")
        if self.conflicts:
            lines.append("-" * 60)
            lines.append("Conflicts detected:")
            for w in self.conflicts:
                lines.append(f"  {w}")
        if self.deferred:
            lines.append("-" * 60)
            lines.append("Deferred (not enough time today):")
            for t in self.deferred:
                pet_label = f" [{t.pet_name}]" if t.pet_name else ""
                lines.append(f"  • {t.title}{pet_label} ({t.duration_minutes} min, {t.priority})")
        return "\n".join(lines)


class Scheduler:
    """
    Retrieves tasks from the Owner's pets, sorts by priority and category
    importance, and fits them into the owner's available time.

    Algorithm:
    1. Call owner.get_all_tasks() — skips already-completed tasks.
    2. Sort descending by (priority_value, category_weight).
    3. For each task, find the earliest valid slot respecting preferred_time.
    4. Place task if task_duration + gap fits within remaining minutes; else defer.
    5. Run detect_conflicts() on the finished schedule.
    6. Return a DailySchedule sorted chronologically.
    """

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def generate(self) -> DailySchedule:
        """Generate a daily schedule and check it for conflicts."""
        schedule = DailySchedule(owner=self.owner)
        tasks = self.owner.get_all_tasks(include_completed=False)
        sorted_tasks = sorted(tasks, key=lambda t: t.sort_key(), reverse=True)

        current_minute = 0
        minutes_remaining = self.owner.available_minutes

        for task in sorted_tasks:
            win_start, win_end = TIME_WINDOWS[task.preferred_time]

            # Determine slot start
            if task.preferred_time != "any":
                if current_minute < win_start:
                    slot_start = win_start
                    window_note = (
                        f"Scheduled at the start of the preferred "
                        f"{task.preferred_time} window."
                    )
                elif current_minute > win_end:
                    slot_start = current_minute
                    window_note = (
                        f"Preferred {task.preferred_time} window already passed; "
                        f"placed at next available slot."
                    )
                else:
                    slot_start = current_minute
                    window_note = f"Fits within the preferred {task.preferred_time} window."
            else:
                slot_start = current_minute
                window_note = "No time preference; placed at next available slot."

            # Gap = idle time waiting for the window to open
            gap = max(0, slot_start - current_minute)

            # FIX: defer only if task + gap together exceed what's left
            if task.duration_minutes + gap > minutes_remaining:
                schedule.deferred.append(task)
                continue

            reasoning = self._build_reasoning(task, window_note)
            schedule.scheduled.append(
                ScheduledTask(task=task, start_minute=slot_start, reasoning=reasoning)
            )
            current_minute = slot_start + task.duration_minutes
            minutes_remaining -= gap + task.duration_minutes

        schedule.scheduled.sort(key=lambda st: st.start_minute)
        schedule.conflicts = self.detect_conflicts(schedule)
        return schedule

    @staticmethod
    def sort_tasks_by_time(tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda t: TIME_WINDOW_ORDER.get(t.preferred_time, 3))

    def detect_conflicts(self, schedule: DailySchedule) -> list[str]:
        warnings = []
        items = schedule.scheduled
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                if a.start_minute < b.end_minute and b.start_minute < a.end_minute:
                    warnings.append(
                        f"⚠ Conflict: '{a.task.title}' "
                        f"({a.start_time_str}–{a.end_time_str}) overlaps with "
                        f"'{b.task.title}' ({b.start_time_str}–{b.end_time_str})"
                    )
        return warnings

    def _build_reasoning(self, task: Task, window_note: str) -> str:
        priority_desc = {
            "high": "High priority — scheduled before lower-priority items.",
            "medium": "Medium priority — scheduled after high-priority items.",
            "low": "Low priority — scheduled last.",
        }[task.priority]
        category_desc = {
            "medication": "Medications are critical and take precedence.",
            "appointment": "Appointments have fixed time commitments.",
            "feeding": "Regular meals keep energy and health stable.",
            "walk": "Exercise supports physical and mental wellbeing.",
            "grooming": "Grooming maintains hygiene and comfort.",
            "other": "General care task.",
        }.get(task.category, "General care task.")
        pet_label = f"For {task.pet_name}. " if task.pet_name else ""
        return f"{pet_label}{priority_desc} {category_desc} {window_note}"
