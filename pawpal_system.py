"""
PawPal+ — class skeletons
Attributes and method stubs only; logic comes next.
"""

from __future__ import annotations
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    special_needs: list[str] = field(default_factory=list)

    def summary(self) -> str:
        pass


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str = "medium"      # "high" | "medium" | "low"
    category: str = "other"       # "feeding" | "walk" | "medication" | "appointment" | "grooming" | "other"
    preferred_time: str = "any"   # "morning" | "afternoon" | "evening" | "any"

    @property
    def priority_value(self) -> int:
        pass

    @property
    def category_weight(self) -> int:
        pass

    def sort_key(self) -> tuple:
        pass


# ---------------------------------------------------------------------------
# Regular classes
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, available_minutes: int = 480) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def summary(self) -> str:
        pass


class ScheduledTask:
    def __init__(self, task: Task, start_minute: int, reasoning: str = "") -> None:
        self.task = task
        self.start_minute = start_minute
        self.reasoning = reasoning

    @property
    def end_minute(self) -> int:
        pass

    def start_time_str(self) -> str:
        pass

    def end_time_str(self) -> str:
        pass


class DailySchedule:
    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet
        self.scheduled: list[ScheduledTask] = []
        self.deferred: list[Task] = []

    def total_minutes_used(self) -> int:
        pass

    def summary(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]) -> None:
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate(self) -> DailySchedule:
        pass

    def _build_reasoning(self, task: Task, slot_start: int, window_note: str) -> str:
        pass
