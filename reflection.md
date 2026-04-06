# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Before writing any code, I identified three core actions a user should be able to perform:

1. **Register a pet and owner** — The user enters their name, their pet's name, species, and how many minutes per day they have available for pet care. This sets the constraints that every other part of the system works within. Without knowing who the owner is and how much time they have, the scheduler has nothing to optimize against.

2. **Add care tasks** — The user creates individual tasks (e.g., morning walk, dinner feeding, heartworm medication) and gives each one a title, duration in minutes, priority level (high / medium / low), category (walk, feeding, medication, appointment, grooming), and an optional preferred time of day (morning, afternoon, evening, or any). This models the real-world reality that not all pet care needs are equal — a medication is more urgent than a grooming session — and that some tasks belong at specific times of day.

3. **Generate and view today's schedule** — The user asks the system to produce an ordered daily plan. The scheduler takes all registered tasks, sorts them by priority and category importance, fits them into the owner's available time window, and returns a schedule with a plain-language explanation for why each task was placed at its particular time slot. Tasks that don't fit are surfaced as deferred so the owner knows what was left out and why.

These three actions map directly to the three responsibilities the system must handle: representing entities (owner, pet), representing work (tasks), and reasoning about how to organize that work (scheduler).

The initial UML design includes six classes:

- **Owner** — holds the owner's name and daily available minutes; can add pets and return a summary.
- **Pet** — holds name, species, and any special needs; can return a summary.
- **Task** — holds title, duration, priority, category, and preferred time of day; exposes a sort key used by the scheduler.
- **Scheduler** — takes an Owner, a Pet, and a list of Tasks; generates a DailySchedule using a priority-and-category sort algorithm.
- **ScheduledTask** — wraps a Task with a concrete start time and a plain-language reasoning string.
- **DailySchedule** — the output object; holds the list of placed ScheduledTasks and any deferred Tasks that didn't fit.

Key relationship decisions:
- Owner owns 1 or more Pets, but the Scheduler plans for one Pet at a time (simplification).
- ScheduledTask *wraps* a Task (composition) rather than inheriting from it, because a scheduled task has a task — it isn't a special kind of task.
- Scheduler is stateless — it produces a DailySchedule but doesn't store it, making it reusable.

This design may be simplified or adjusted if the current structure proves to be a problem during implementation.

**b. Design changes**

After reviewing the skeleton, three issues came up:

1. **`priority_value`, `category_weight`, and `end_minute` changed from methods to `@property`** — these originally had empty parentheses like regular methods, but they're purely derived values with no arguments or side effects. Making them properties means callers write `task.priority_value` instead of `task.priority_value()`, which is more natural in Python and matches how dataclass fields feel to use.

2. **`Task` input validation identified as a risk** — the `priority` and `preferred_time` fields accept any string with no guard. A typo would pass silently and cause a `KeyError` deep inside the scheduler. The fix (a `__post_init__` check) will be added during the implementation step.

3. **`Owner.pets` vs `Scheduler` taking a single `Pet` — kept as-is by choice** — `Owner` stores a list of pets and has `add_pet()`, but `Scheduler` accepts just one `Pet` directly. This inconsistency was flagged but left intentionally: the app plans one pet's day at a time, so the scheduler doesn't need to loop over all pets. This is a documented simplification, not an oversight.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints, in this order of importance:

1. **Priority level** (high / medium / low) — this is the primary sort key. A high-priority medication will always be considered before a low-priority grooming session, regardless of time preference.
2. **Category weight** (medication > appointment > feeding > walk > grooming > other) — used as a tiebreaker when two tasks share the same priority level. This reflects real-world urgency: missing a medication is more consequential than skipping a walk.
3. **Preferred time window** (morning / afternoon / evening / any) — the scheduler tries to place each task in its preferred window, but will fall back to the next available slot if the window has already passed. It won't displace a higher-priority task just to honour a time preference.

The owner's `available_minutes` acts as a hard cap: any task that doesn't fit is deferred rather than over-scheduled.

**b. Tradeoffs**

The conflict detector checks for *exact time-range overlaps* in the final schedule — two tasks conflict only if their `[start, end)` intervals literally intersect. It does not predict soft conflicts like "these two tasks are both in the morning window and one might push the other late." 

This is a reasonable tradeoff for a daily pet-care app: the greedy scheduler already prevents true overlaps by advancing the clock after each placement, so the detector's main value is as a safety net for manually constructed or externally imported schedules. Checking only exact overlaps keeps the logic simple (an O(n²) pair scan) and avoids false positives from overly cautious proximity warnings. A more sophisticated version could flag tasks within a configurable buffer window, but that would require exposing another setting to the user without much practical benefit at this scale.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
