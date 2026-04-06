import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Smart daily scheduling for your pets — sorted, filtered, and conflict-checked automatically.")

# ---------------------------------------------------------------------------
# Session state — initialised once; survives re-runs
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Step 1: Owner & pet setup
# ---------------------------------------------------------------------------
st.header("1. Owner & Pets")

with st.form("owner_form"):
    owner_name = st.text_input("Your name", value="Jordan")
    available_hours = st.slider("Hours available for pet care today", 1, 12, 3)
    submitted = st.form_submit_button("Save owner")
    if submitted:
        st.session_state.owner = Owner(
            name=owner_name,
            available_minutes=available_hours * 60,
        )
        st.success(f"Owner saved: {st.session_state.owner.summary()}")

if st.session_state.owner is None:
    st.info("Fill in your name above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# Add a pet
st.subheader("Add a pet")
with st.form("pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    special_needs = st.text_input("Special needs (comma-separated, optional)", value="")
    add_pet = st.form_submit_button("Add pet")
    if add_pet:
        needs = [s.strip() for s in special_needs.split(",") if s.strip()]
        pet = Pet(name=pet_name, species=species, special_needs=needs)
        owner.add_pet(pet)
        st.success(f"Added {pet.summary()}")

if owner.pets:
    st.write("**Pets registered:**", ", ".join(p.name for p in owner.pets))
else:
    st.info("No pets yet — add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Step 2: Add tasks
# ---------------------------------------------------------------------------
st.header("2. Add Tasks")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    with st.form("task_form"):
        pet_choice = st.selectbox("Assign to pet", [p.name for p in owner.pets])
        task_title = st.text_input("Task title", value="Morning walk")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["high", "medium", "low"])
        category = st.selectbox("Category", ["walk", "feeding", "medication", "appointment", "grooming", "other"])
        preferred_time = st.selectbox("Preferred time", ["morning", "afternoon", "evening", "any"])
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as_needed"])
        add_task = st.form_submit_button("Add task")
        if add_task:
            target_pet = next(p for p in owner.pets if p.name == pet_choice)
            task = Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=priority,
                category=category,
                preferred_time=preferred_time,
                frequency=frequency,
            )
            target_pet.add_task(task)
            st.success(f"Added '{task_title}' to {pet_choice}.")

    # --- Pending tasks with filter controls ---
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.subheader("Pending tasks")

        col_filter, col_sort = st.columns(2)
        with col_filter:
            pet_filter = st.selectbox(
                "Filter by pet",
                ["All pets"] + [p.name for p in owner.pets],
                key="pet_filter",
            )
        with col_sort:
            sort_mode = st.selectbox(
                "Sort by",
                ["Time of day (morning first)", "Priority (high first)"],
                key="sort_mode",
            )

        # Apply filter
        if pet_filter != "All pets":
            display_tasks = [t for t in all_tasks if t.pet_name == pet_filter]
        else:
            display_tasks = list(all_tasks)

        # Apply sort
        if sort_mode == "Time of day (morning first)":
            display_tasks = Scheduler.sort_tasks_by_time(display_tasks)
        else:
            display_tasks = sorted(
                display_tasks,
                key=lambda t: t.priority_value,
                reverse=True,
            )

        PRIORITY_COLOR = {"high": "🔴", "medium": "🟡", "low": "🟢"}

        st.table([
            {
                "Pet": t.pet_name,
                "Task": t.title,
                "Duration": f"{t.duration_minutes} min",
                "Priority": f"{PRIORITY_COLOR.get(t.priority, '')} {t.priority}",
                "Category": t.category,
                "Time": t.preferred_time,
                "Recurs": t.frequency,
            }
            for t in display_tasks
        ])
    else:
        st.info("No tasks yet — add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Step 3: Generate schedule
# ---------------------------------------------------------------------------
st.header("3. Today's Schedule")

if st.button("Generate schedule"):
    tasks = owner.get_all_tasks()
    if not tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner=owner)
        schedule = scheduler.generate()

        # --- Conflict warnings (shown first so owner can't miss them) ---
        if schedule.conflicts:
            st.error(
                f"**{len(schedule.conflicts)} scheduling conflict(s) detected — "
                "please review before following this plan.**"
            )
            for conflict_msg in schedule.conflicts:
                st.warning(conflict_msg)
        else:
            st.success("No conflicts — your schedule looks clean!")

        st.subheader(f"Plan for {owner.name}'s pets")

        # Progress bar: time used vs available
        pct = min(schedule.total_minutes_used / owner.available_minutes, 1.0)
        st.progress(pct, text=f"Time used: {schedule.total_minutes_used} / {owner.available_minutes} min")

        if schedule.scheduled:
            PRIORITY_BADGE = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}
            CATEGORY_ICON = {
                "medication": "💊", "appointment": "📅", "feeding": "🍽️",
                "walk": "🦮", "grooming": "✂️", "other": "📋",
            }
            for st_task in schedule.scheduled:
                icon = CATEGORY_ICON.get(st_task.task.category, "📋")
                badge = PRIORITY_BADGE.get(st_task.task.priority, st_task.task.priority)
                with st.expander(
                    f"{icon} {st_task.start_time_str} – {st_task.end_time_str}  |  "
                    f"**{st_task.task.title}** [{st_task.task.pet_name}]  —  {badge}"
                ):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Duration", f"{st_task.task.duration_minutes} min")
                    col2.metric("Category", st_task.task.category)
                    col3.metric("Recurs", st_task.task.frequency)
                    st.info(f"**Why this slot:** {st_task.reasoning}")
        else:
            st.warning("No tasks could be scheduled within the available time.")

        # --- Deferred tasks ---
        if schedule.deferred:
            st.subheader("⏭ Deferred (didn't fit today)")
            st.caption("These tasks were skipped because the available time ran out.")
            for t in schedule.deferred:
                st.write(
                    f"- **{t.title}** [{t.pet_name}] — "
                    f"{t.duration_minutes} min, {t.priority} priority"
                )
