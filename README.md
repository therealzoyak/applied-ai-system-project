# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

PawPal+ goes beyond a simple task list with four algorithmic features:

- **Sorting by time** — `Scheduler.sort_tasks_by_time()` orders any task list by preferred time-of-day window (morning → afternoon → evening → any) using a stable sort with a numeric key, so alphabetical string quirks never affect the order.
- **Filtering** — `Owner.filter_tasks(pet_name, completed)` lets you slice the task list by pet or completion status without touching the underlying data.
- **Recurring tasks** — `Task.mark_complete()` returns a fresh `Task` instance for the next occurrence using Python's `timedelta` (`+1 day` for daily, `+7 days` for weekly). `as_needed` tasks return `None`. The original task is marked done; the new one is ready to be added back to the pet.
- **Conflict detection** — `Scheduler.detect_conflicts()` scans the final schedule for overlapping time intervals and returns plain-language warning strings. Conflicts are also embedded in `DailySchedule.summary()`.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
