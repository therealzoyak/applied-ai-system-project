# PawPal+ UML Class Diagram

```mermaid
classDiagram
    class Task {
        +str title
        +int duration_minutes
        +str priority
        +str category
        +str preferred_time
        +str frequency
        +bool completed
        +str pet_name
        +date due_date
        +int priority_value
        +int category_weight
        +sort_key() tuple
        +mark_complete() Task
        +next_occurrence() Task
        +summary() str
    }

    class Pet {
        +str name
        +str species
        +list~str~ special_needs
        +list~Task~ tasks
        +add_task(task: Task) None
        +get_tasks(include_completed: bool) list~Task~
        +summary() str
    }

    class Owner {
        +str name
        +int available_minutes
        +list~Pet~ pets
        +add_pet(pet: Pet) None
        +get_all_tasks(include_completed: bool) list~Task~
        +filter_tasks(pet_name, completed) list~Task~
        +summary() str
    }

    class ScheduledTask {
        +Task task
        +int start_minute
        +str reasoning
        +int end_minute
        +str start_time_str
        +str end_time_str
    }

    class DailySchedule {
        +Owner owner
        +list~ScheduledTask~ scheduled
        +list~Task~ deferred
        +list~str~ conflicts
        +int total_minutes_used
        +summary() str
    }

    class Scheduler {
        +Owner owner
        +generate() DailySchedule
        +sort_tasks_by_time(tasks) list~Task~$
        +detect_conflicts(schedule) list~str~
        -_build_reasoning(task, window_note) str
    }

    Pet "1" o-- "0..*" Task : contains
    Owner "1" o-- "1..*" Pet : owns
    Owner ..> Scheduler : passed to
    Scheduler --> DailySchedule : generates
    DailySchedule o-- ScheduledTask : holds
    ScheduledTask --> Task : wraps
    DailySchedule --> Owner : references
```

## Relationship notes

| Arrow | Meaning |
|-------|---------|
| `o--` | Aggregation — Pet owns its Tasks; Owner owns its Pets |
| `-->` | Directed association — Scheduler produces DailySchedule; ScheduledTask wraps a Task |
| `..>` | Dependency — Scheduler receives an Owner but doesn't own it |

## Key changes from the Phase 1 draft

- Added `ScheduledTask` class (missing entirely from the original diagram).
- Expanded all classes with their full attributes and methods.
- Replaced the ambiguous `Pet --> Scheduler` / `Task --> Scheduler` arrows with the correct `Owner ..> Scheduler` dependency (Scheduler talks to Owner, not directly to Pet/Task).
- Added `DailySchedule.conflicts` list — populated by `detect_conflicts()`.
- Marked `sort_tasks_by_time` with `$` to indicate it is a static method.
