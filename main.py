"""
main.py — demo script to verify PawPal+ logic in the terminal.
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=180)  # 3 hours available today

mochi = Pet(name="Mochi", species="cat")
biscuit = Pet(name="Biscuit", species="dog")

owner.add_pet(mochi)
owner.add_pet(biscuit)

# --- Tasks for Mochi ---
mochi.add_task(Task(
    title="Give heartworm pill",
    duration_minutes=5,
    priority="high",
    category="medication",
    preferred_time="morning",
    frequency="daily",
))
mochi.add_task(Task(
    title="Breakfast feeding",
    duration_minutes=10,
    priority="high",
    category="feeding",
    preferred_time="morning",
    frequency="daily",
))
mochi.add_task(Task(
    title="Brush coat",
    duration_minutes=15,
    priority="low",
    category="grooming",
    preferred_time="evening",
    frequency="weekly",
))

# --- Tasks for Biscuit ---
biscuit.add_task(Task(
    title="Morning walk",
    duration_minutes=30,
    priority="high",
    category="walk",
    preferred_time="morning",
    frequency="daily",
))
biscuit.add_task(Task(
    title="Vet appointment",
    duration_minutes=60,
    priority="high",
    category="appointment",
    preferred_time="afternoon",
    frequency="as_needed",
))
biscuit.add_task(Task(
    title="Evening walk",
    duration_minutes=20,
    priority="medium",
    category="walk",
    preferred_time="evening",
    frequency="daily",
))

# --- Generate schedule ---
scheduler = Scheduler(owner=owner)
schedule = scheduler.generate()

# --- Print ---
print()
print(schedule.summary())
print()
