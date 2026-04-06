# PawPal+ (Module 2 Project)

> A smart daily scheduler for pet owners — sort, filter, detect conflicts, and track recurring care tasks, all in one Streamlit app.

## Features

| Feature | How it works |
|---------|-------------|
| **Priority-based scheduling** | Tasks are ranked by priority (`high > medium > low`) and category weight (`medication > appointment > feeding > walk > grooming`). Higher-ranked tasks are placed first. |
| **Sorting by time of day** | `Scheduler.sort_tasks_by_time()` orders tasks morning → afternoon → evening → any using a stable numeric sort — alphabetical string quirks never affect the order. |
| **Live filtering** | The pending-tasks table can be filtered by pet name and sorted by time-of-day or priority directly in the UI. |
| **Conflict warnings** | `Scheduler.detect_conflicts()` scans the final schedule for overlapping time intervals. Any conflicts are shown as prominent `st.warning` banners at the top of the schedule so the owner can't miss them. |
| **Recurring tasks** | `Task.mark_complete()` automatically calculates the next occurrence: `+1 day` for daily tasks, `+7 days` for weekly tasks, `None` for as-needed tasks. |
| **Deferred tasks** | Tasks that exceed the owner's available time are listed separately so nothing is silently dropped. |
| **Reasoning display** | Every scheduled slot includes a plain-language explanation of why it was placed there. |

## 📸 Demo

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank"><img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

---

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

## Testing PawPal+

### Run the tests

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install pytest
python -m pytest
```

### What the tests cover

| Area | Tests |
|------|-------|
| **Task validation** | Invalid priority, preferred_time, zero/negative duration all raise `ValueError` |
| **Pet task management** | Adding tasks, pet-name stamping, empty-pet edge case, completed-task filtering |
| **Recurrence logic** | Daily → +1 day, weekly → +7 days, `as_needed` → `None`; title/duration preserved |
| **Sorting correctness** | `sort_tasks_by_time` orders morning → afternoon → evening → any; stable sort |
| **Conflict detection** | Overlapping slots flagged, back-to-back slots not flagged |
| **Owner filtering** | `filter_tasks(pet_name=…)` and `filter_tasks(completed=…)` slice correctly |
| **Scheduler constraints** | Tasks deferred when time runs out; no-pets produces empty schedule; high priority before low |

26 tests total.

### Confidence level

★★★★★ — All 26 tests pass. Core scheduling behaviors (sorting, recurrence, conflict detection) are verified with both happy-path and edge-case scenarios.

---

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
