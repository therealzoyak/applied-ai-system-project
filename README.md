# PawPal+ 🐾

A smart daily scheduler for pet owners — sort, filter, detect conflicts, and get AI-powered care advice, all in one Streamlit app.

---

## Where this came from

This project is an evolution of **PawPal (Modules 1–3)**, a rule-based pet care scheduler I built earlier in the course. The original goal was simple: help busy pet owners stay on top of their animals' routines by letting them add tasks, set priorities, and generate a conflict-free daily plan. It handled sorting by time of day, recurring tasks, conflict detection, and explained why each task got its slot. It worked well — but it had no real AI in it. Everything was hand-coded logic.

PawPal+ adds the AI layer: a RAG-powered care advisor that reads your actual schedule, retrieves relevant pet care tips from a knowledge base, and uses Claude to turn those tips into personalized daily advice.

---

## What it does

| Feature | How it works |
| --- | --- |
| **Priority-based scheduling** | Tasks are ranked by priority (`high > medium > low`) and category weight (`medication > appointment > feeding > walk > grooming`). Higher-ranked tasks are placed first. |
| **Sorting by time of day** | `Scheduler.sort_tasks_by_time()` orders tasks morning → afternoon → evening → any using a stable numeric sort. |
| **Live filtering** | The pending-tasks table can be filtered by pet name and sorted by time-of-day or priority in the UI. |
| **Conflict warnings** | `Scheduler.detect_conflicts()` scans the schedule for overlapping time intervals. Conflicts are shown as warning banners at the top so you can't miss them. |
| **Recurring tasks** | `Task.mark_complete()` automatically calculates the next occurrence: `+1 day` for daily, `+7 days` for weekly, `None` for as-needed. |
| **Deferred tasks** | Tasks that don't fit the available time are listed separately — nothing is silently dropped. |
| **Reasoning display** | Every scheduled slot includes a plain-language explanation of why it was placed there. |
| **AI care advisor (RAG)** | After generating your schedule, Claude retrieves relevant tips from a curated knowledge base and gives you personalized advice based on your actual tasks and pets. |

---

## System architecture

Here's the rough flow:

```
User input (owner, pets, tasks, hours available)
        ↓
   Scheduler — pawpal_system.py
   sorts by priority + category weight
   detects conflicts, defers tasks that do not fit
        ↓
   Daily schedule output
        ↓
   RAG Pipeline — ai_advisor.py + pet_care_kb.py
   retriever matches tips to scheduled task categories + pet species
   retrieved tips + schedule summary sent to Claude
   Claude generates grounded, specific advice
        ↓
   AI care advice shown in the app
        ↓
   You read it and decide what to do (human in the loop)
```

Every API call is logged to `pawpal_advisor.log` with timestamps, token counts, and any errors.

---

## Setup

**You'll need:** Python 3.9+, an Anthropic API key (free tier is fine — get one at [console.anthropic.com](https://console.anthropic.com))

```bash
# 1. Clone the repo
git clone https://github.com/therealzoyak/applied-ai-system-project.git
cd applied-ai-system-project

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
# Create a .env file in the project root and add this line:
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# 5. Run the app
python3 -m streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## Sample interactions

### Example 1 — Dog with medication and a walk

**Input:** Bella (dog) — Heartworm pill (5 min, high, morning), Morning walk (20 min, high, morning), Dinner (10 min, medium, evening)

**Generated schedule:**
- 8:00–8:05 AM — Heartworm pill
- 8:05–8:25 AM — Morning walk
- 5:00–5:10 PM — Dinner

**AI advice:**
> For Bella's heartworm pill this morning — a lot of dogs take medication more easily when it's tucked into a small piece of food right before the walk. Since the walk is immediately after, give it a few minutes between the pill and heading out. It's also worth logging the dose somewhere so you have a record for vet visits. For dinner in the evening, stick to a consistent time — dogs do better on a routine, and it makes appetite changes easier to notice.

---

### Example 2 — Cat with a vet appointment

**Input:** Mochi (cat) — Vet appointment (60 min, high, morning), Feeding (10 min, high, morning), Grooming (20 min, low, afternoon)

**Generated schedule:**
- 8:00–9:00 AM — Vet appointment
- 9:00–9:10 AM — Feeding
- 12:00–12:20 PM — Grooming

**AI advice:**
> Before Mochi's appointment this morning, leave the carrier out somewhere she can sniff around it — even 20 minutes helps. Cats who are surprised by the carrier stress out harder. Bring a short written list of anything you have noticed behavior-wise lately, because vet appointments go fast. For the grooming this afternoon, long-haired cats especially benefit from a regular brush — it catches mats before they get painful.

---

### Example 3 — Scheduling conflict

**Input:** Two tasks assigned to overlapping time windows for the same pet.

**Output:** Red conflict banner shown at the top of the schedule. The AI advisor acknowledges the conflict and suggests which task to prioritize based on category weight.

---

## Design decisions

**Why RAG instead of just prompting Claude directly?**

I could have skipped the retrieval step and just asked Claude for pet care advice. It would have given a decent answer. But the point of RAG is that the output is grounded — Claude can only work with what was retrieved, so the advice is tied to your actual schedule and your pets' species. It also makes the system easier to debug: if the advice is off, you can check whether retrieval pulled the wrong tips or whether Claude misused good tips. Without RAG, that distinction disappears.

**Why a local knowledge base instead of web search?**

Pet care advice on the internet varies a lot in quality. A hand-curated knowledge base is smaller but more reliable, and every entry can be updated deliberately. For a project at this scale it is the right call. A production version would probably use embeddings and a vector database to handle a much larger corpus.

**Why Streamlit?**

It was already in the original project and let me focus on the AI logic instead of building a frontend. Not the most scalable choice, but the right tool for this stage.

**Trade-offs:**
- The knowledge base is hand-curated, so it has gaps. Proper vector search would give better retrieval results at scale.
- The app does not persist data between sessions — refresh and everything resets. That is a Streamlit state limitation.
- Retrieval is category/species matching, not semantic similarity. It works for this use case but would not scale well.

---

## Testing and reliability

### Scheduler tests (automated)

```bash
source .venv/bin/activate
python -m pytest
```

| Area | Tests |
| --- | --- |
| **Task validation** | Invalid priority, preferred_time, zero/negative duration all raise `ValueError` |
| **Pet task management** | Adding tasks, pet-name stamping, empty-pet edge case, completed-task filtering |
| **Recurrence logic** | Daily +1 day, weekly +7 days, as_needed returns None; title/duration preserved |
| **Sorting correctness** | `sort_tasks_by_time` orders morning to afternoon to evening to any; stable sort |
| **Conflict detection** | Overlapping slots flagged, back-to-back slots not flagged |
| **Owner filtering** | `filter_tasks(pet_name)` and `filter_tasks(completed)` slice correctly |
| **Scheduler constraints** | Tasks deferred when time runs out; no-pets produces empty schedule; high priority before low |

**26/26 tests pass.**

### AI advisor reliability

The RAG pipeline was tested manually across several scenarios:

- **Retrieval accuracy** — scheduling a medication task for a cat correctly pulls cat-specific tips, not dog tips. 5 out of 6 category/species combinations retrieved the expected tip type.
- **Error handling** — invalid API keys, missing internet, and rate limit errors all surface as readable messages in the UI rather than crashing. Every failure is logged to `pawpal_advisor.log`.
- **Edge cases** — an empty schedule does not call the API at all. A pet with species "other" falls back to general tips without breaking.
- **Conflict passthrough** — scheduling conflicts detected by the scheduler get passed to Claude and show up addressed in the advice.

The one gap: Claude's outputs are not automatically evaluated for quality or consistency across runs. That would require either a scoring rubric or a second LLM evaluation pass — something to add in a future version.

---

## Reflection and ethics

**Limitations and bias**

The knowledge base is oriented mostly toward dogs and cats. If someone added a rabbit, bird, or reptile, the retrieval would fall back to generic tips that may not be accurate or safe for that animal — and the system has no way to flag that gap. It would just give advice anyway. That is a real problem for a production version of this.

Claude can also be confidently wrong. If a retrieved tip is outdated or the prompt is ambiguous, the model still generates fluent, confident-sounding output. There is no built-in fact-checking.

**Could this be misused?**

The most realistic misuse is someone treating the AI advice as a substitute for a vet, especially for medication-related tasks. The system does not add a disclaimer to every response — something like "this is general guidance, not medical advice" — which it probably should. That is an easy fix I would make before putting this in front of real users.

**What surprised me during testing**

I expected the retrieval step to be the least interesting part. It ended up being the most important. When the wrong tips got retrieved — like dog-specific advice for a cat — Claude would use them confidently without flagging the mismatch. Output quality depended almost entirely on whether retrieval was right. That was a useful lesson about where to focus debugging effort in RAG systems.

**Collaborating with AI on this project**

I used Claude as a coding partner throughout. One genuinely helpful moment: when structuring the RAG retrieval, Claude suggested scoring tips by species specificity — species-matched tips score higher than "all species" tips — before filtering by category. That made the retrieval noticeably more relevant and was the right call.

One moment where it steered me wrong: Claude suggested hardcoding the API key directly in `app.py` as a quick fix for a sidebar issue. That worked locally, but GitHub's secret scanning flagged it immediately when I pushed. I had to revoke the key and switch to a `.env` file — which was the correct approach all along. It was a good reminder that quick workaround suggestions from AI tools do not always account for real-world consequences like public repos and security tooling.
