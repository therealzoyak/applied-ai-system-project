# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
Main 3 problems: 
1. Register a pet and owner The user enters their name, their pet's name, species, and how many minutes per day they have available for pet care. 

2. Adding care tasks: The user creates individual tasks (e.g., morning walk, dinner feeding, heartworm medication) and gives each one a title, duration in minutes, priority level (high / medium / low), category (walk, feeding, medication, appointment, grooming), and an optional preferred time of day (morning, afternoon, evening, or any)

3. Generate/view todays schedule: The user asks the system to produce an ordered daily plan. 

The initial UML design includes six classes: Owner, Pet, Task, Scheduler, ScheduledTask, and DailySchedule. Owner holds the owner info and their pets, Pet holds the animal's details, Task stores what needs to be done and when, Scheduler takes all of that and produces a plan, ScheduledTask wraps a Task with an actual start time and a reasoning note, and DailySchedule is the final output with everything placed or deferred.

Key decisions: Owner owns 1 or more Pets. ScheduledTask wraps a Task rather than inheriting from it because a scheduled task *has* a task, it isn't a special type of task. Scheduler is stateless — it produces a schedule but doesn't store it.

**b. Design changes**

Three things changed after reviewing the skeleton:

1. `priority_value`, `category_weight`, and `end_minute` became `@property` instead of regular methods — they're just derived values with no arguments, so calling them like `task.priority_value` feels more natural than `task.priority_value()`.

2. Added `__post_init__` validation on Task — without it, a typo in priority or preferred_time would silently pass and crash deep inside the scheduler with a KeyError, which would be confusing to debug.

3. Scheduler ended up taking the Owner (not a single Pet directly) — the original design had it taking one Pet, but since Owner aggregates all pets, it made more sense to just pass Owner and let it call `get_all_tasks()`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler ranks tasks by priority first (high > medium > low), then breaks ties by category weight (medication > appointment > feeding > walk > grooming). After sorting, it tries to place each task in its preferred time window and falls back to the next open slot if that window has passed. The owner's available_minutes is a hard cap — anything that doesn't fit gets deferred, not squeezed in.

**b. Tradeoffs**

The conflict detector only flags exact time-range overlaps. It won't warn you that two morning tasks might run close together, just that they literally overlap. That's fine for this use case — the scheduler already prevents overlaps by advancing the clock after each placement, so the detector is really just a safety net. Keeping it simple avoids false positives and the logic stays easy to follow.

---

## 3. AI Collaboration

**a. How you used AI**

Mostly for design feedback and filling in logic I wasn't sure about — like asking whether ScheduledTask should inherit from Task or wrap it, and getting help drafting the conflict detection loop. The most useful prompts were specific ones, like "given this sort key, will high priority always beat low priority even if they share a category?" rather than broad ones like "help me build a scheduler."

**b. Judgment and verification**

At one point Copilot suggested making Scheduler store the last generated schedule as an instance variable so it could be re-accessed later. I didn't go with it because it adds state that isn't needed — the app just calls `generate()` fresh each time the button is clicked. I verified by thinking through whether any part of the app actually needed to look up a past schedule, and it didn't.

---

## 4. Testing and Verification

**a. What you tested**

Sorting order, recurrence logic (daily/weekly/as_needed), conflict detection (overlapping vs back-to-back), task validation errors, filtering by pet and completion status, and scheduler edge cases like no pets or not enough time. These mattered because they're the core behaviors — if any of them are wrong the whole schedule is wrong.

**b. Confidence**

Pretty confident in the happy paths. The edge cases I'd still want to cover are things like what happens if two pets have the same name, or if a task's due_date is in the past — those could cause subtle bugs that the current tests don't catch.

---

## 5. Reflection

**a. What went well**

The separation between the backend logic and the UI worked out cleanly. Because all the scheduling logic lived in `pawpal_system.py`, I could write and test it completely independently before touching Streamlit at all.

**b. What you would improve**

The scheduler is greedy — it just goes down the sorted list and places tasks one by one. That means it can miss combinations that would fit better. A smarter approach would try to optimize the full schedule rather than just picking tasks in order.

**c. Key takeaway**

Start with the data model before writing any logic. Getting the classes and relationships right early made every other step easier — the scheduler basically wrote itself once Owner, Pet, and Task were solid.
