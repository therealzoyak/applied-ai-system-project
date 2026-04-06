"""
PawPal+ — full implementation
"""

from __future__ import annotations
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PRIORITY_VALUES = {"high": 3, "medium": 2, "low": 1}

CATEGORY_WEIGHTS = {
    "medication": 5,
    "appointment": 4,
    "feeding": 3,
    "walk": 2,
    "grooming": 1,
    "other": 0,
}

# Time-window boundaries in minutes from DAY_START_HOUR
TIME_WINDOWS = {
    "morning":   (0,   240),   # 08:00 – 12:00
    "afternoon": (240, 540),   # 12:00 – 17:00
    "evening":   (540, 720),   # 17:00 – 20:00
    "any":       (0,   720),
}

DAY_START_HOUR = 8  # schedule anchored to 8:00 AM


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet-care activity."""
    title: str
    duration_minutes: int
    priority: str = "medium"      # "high" | "medium" | "low"
    category: str = "other"       # "feeding" | "walk" | "medication" | "appointment" | "grooming" | "other"
    preferred_time: str = "any"   # "morning" | "afternoon" | "evening" | "any"
    frequency: str = "daily"      # "daily" | "weekly" | "as_needed"
    completed: bool = False
    pet_name: str = ""            # set automatically by Pet.add_task()

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
        """Higher value = scheduled earlier."""
        return (self.priority_value, self.category_weight)

    def mark_complete(self) -> None:
        self.completed = True

    def summary(self) -> str:
        status = "done" if self.completed else "pending"
        return f"{self.title} ({self.duration_minutes} min, {self.priority}, {self.category}, {status})"


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Stores pet details and owns a list of care tasks."""
    name: str
    species: str
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and record the pet's name on the task."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self, include_completed: bool = False) -> list[Task]:
        """Return tasks for this pet, optionally filtering out completed ones."""
        if include_completed:
            return list(self.tasks)
        return [t for t in self.tasks if not t.completed]

    def summary(self) -> str:
        needs = ", ".join(self.special_needs) if self.special_needs else "none"
        return f"{self.name} ({self.species}) | special needs: {needs} | tasks: {len(self.tasks)}"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    def __init__(self, name: str, available_minutes: int = 480) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def get_all_tasks(self, include_completed: bool = False) -> list[Task]:
        """
        Collect tasks across all owned pets.
        The Scheduler calls this to retrieve everything it needs to plan the day.
        """
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks(include_completed=include_completed))
        return all_tasks

    def summary(self) -> str:
        hours, mins = divmod(self.available_minutes, 60)
        pet_names = ", ".join(p.name for p in self.pets) if self.pets else "none"
        return f"{self.name} | {hours}h {mins:02d}m available | pets: {pet_names}"


# ---------------------------------------------------------------------------
# ScheduledTask  (output wrapper — not a user-facing input class)
# ---------------------------------------------------------------------------

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
            f"[{self.start_time_str} – {self.end_time_str}]{pet_label}  "
            f"{self.task.title}  ({self.task.duration_minutes} min, {self.task.priority})\n"
            f"    → {self.reasoning}"
        )


# ---------------------------------------------------------------------------
# DailySchedule  (output container)
# ---------------------------------------------------------------------------

class DailySchedule:
    """The result produced by Scheduler.generate()."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.scheduled: list[ScheduledTask] = []
        self.deferred: list[Task] = []

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

        if self.deferred:
            lines.append("-" * 60)
            lines.append("Deferred (not enough time today):")
            for t in self.deferred:
                pet_label = f" [{t.pet_name}]" if t.pet_name else ""
                lines.append(f"  • {t.title}{pet_label}  ({t.duration_minutes} min, {t.priority})")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler  (the "brain")
# ---------------------------------------------------------------------------

class Scheduler:
    """
    Retrieves tasks from the Owner's pets, sorts them by priority and
    category importance, and fits them into the owner's available time.

    How the Scheduler talks to Owner:
        tasks = owner.get_all_tasks()
    This single call aggregates tasks across all pets without the Scheduler
    needing to know how many pets exist or how they're stored.

    Algorithm:
        1. Call owner.get_all_tasks() — skips already-completed tasks.
        2. Sort descending by (priority_value, category_weight).
        3. For each task, find the earliest valid slot respecting preferred_time.
        4. Place task if it fits within remaining available minutes; otherwise defer.
        5. Return a DailySchedule sorted chronologically.
    """

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def generate(self) -> DailySchedule:
        schedule = DailySchedule(owner=self.owner)
        tasks = self.owner.get_all_tasks(include_completed=False)
        sorted_tasks = sorted(tasks, key=lambda t: t.sort_key(), reverse=True)

        current_minute = 0
        minutes_remaining = self.owner.available_minutes

        for task in sorted_tasks:
            # Bail early if the task alone exceeds what's left
            if task.duration_minutes > minutes_remaining:
                schedule.deferred.append(task)
                continue

            win_start, win_end = TIME_WINDOWS[task.preferred_time]
            slot_start = current_minute
            window_note = ""

            if task.preferred_time != "any":
                if current_minute < win_start:
                    # Advance clock to the preferred window
                    slot_start = win_start
                    window_note = (
                        f"Scheduled at the start of the preferred "
                        f"{task.preferred_time} window."
                    )
                elif current_minute > win_end:
                    # Window already passed — schedule at current position
                    slot_start = current_minute
                    window_note = (
                        f"Preferred {task.preferred_time} window already passed; "
                        f"placed at next available slot."
                    )
                else:
                    slot_start = current_minute
                    window_note = f"Fits within the preferred {task.preferred_time} window."
            else:
                window_note = "No time preference; placed at next available slot."

            # Account for any gap created by jumping to a window start
            gap = max(0, slot_start - current_minute)
            if task.duration_minutes > minutes_remaining - gap:
                schedule.deferred.append(task)
                continue

            reasoning = self._build_reasoning(task, window_note)
            schedule.scheduled.append(
                ScheduledTask(task=task, start_minute=slot_start, reasoning=reasoning)
            )
            current_minute = slot_start + task.duration_minutes
            minutes_remaining -= gap + task.duration_minutes

        schedule.scheduled.sort(key=lambda st: st.start_minute)
        return schedule

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
