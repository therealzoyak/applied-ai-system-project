"""
tests/test_pawpal.py — basic tests for PawPal+ core logic.
Run with: pytest
"""

from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    """mark_complete() should flip completed from False to True."""
    task = Task(title="Morning walk", duration_minutes=20, priority="medium")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(name="Mochi", species="cat")
    assert len(pet.tasks) == 0

    pet.add_task(Task(title="Breakfast", duration_minutes=10, priority="high", category="feeding"))
    assert len(pet.tasks) == 1

    pet.add_task(Task(title="Brush coat", duration_minutes=15, priority="low", category="grooming"))
    assert len(pet.tasks) == 2
