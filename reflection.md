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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
