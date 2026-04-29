"""
ai_advisor.py — PawPal+ RAG-Powered AI Care Advisor

Flow:
  1. retrieve_tips() pulls relevant entries from the knowledge base
     based on the actual scheduled tasks and pet species.
  2. Those entries are injected into the Claude prompt as grounding context.
  3. Claude generates personalized advice that must cite/use the retrieved tips —
     it cannot just give generic answers.

This satisfies the RAG requirement: the AI's output is meaningfully shaped
by retrieved data, not just a standalone LLM call.
"""

import logging
import anthropic
from pet_care_kb import retrieve_tips

# ---------------------------------------------------------------------------
# Logging — tracks every advisor call for debugging and auditing
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename="pawpal_advisor.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def build_schedule_summary(scheduled_tasks, pets) -> str:
    """Convert scheduled tasks and pets into a plain-text summary for the prompt."""
    lines = []

    pet_lines = [f"  - {p.name} ({p.species})" +
                 (f", special needs: {', '.join(p.special_needs)}" if p.special_needs else "")
                 for p in pets]
    lines.append("PETS:\n" + "\n".join(pet_lines))

    lines.append("\nSCHEDULED TASKS:")
    for st in scheduled_tasks:
        lines.append(
            f"  - [{st.task.pet_name}] {st.task.title} | "
            f"{st.start_time_str}–{st.end_time_str} | "
            f"category: {st.task.category} | priority: {st.task.priority}"
        )

    return "\n".join(lines)


def build_context_block(retrieved_tips: list[dict]) -> str:
    """Format retrieved knowledge base tips into a numbered context block."""
    if not retrieved_tips:
        return "No specific tips retrieved."

    lines = []
    for i, entry in enumerate(retrieved_tips, 1):
        species_label = entry["species"] if entry["species"] != "all" else "all species"
        lines.append(f"[{i}] ({entry['category']} / {species_label}): {entry['tip']}")

    return "\n".join(lines)


def get_ai_advice(
    scheduled_tasks: list,
    pets: list,
    api_key: str,
    conflicts: list[str] = None,
) -> str:
    """
    Main RAG function: retrieves relevant tips, then calls Claude to generate
    personalized care advice grounded in those tips.

    Args:
        scheduled_tasks: list of ScheduledTask objects from the generated schedule
        pets: list of Pet objects belonging to the owner
        api_key: Anthropic API key
        conflicts: list of conflict warning strings from the scheduler

    Returns:
        A string of personalized AI advice, or an error message if the call fails.
    """
    if not scheduled_tasks:
        logger.warning("AI advisor called with empty schedule — skipping.")
        return "No tasks are scheduled, so no advice to give. Add tasks and generate a schedule first."

    # --- Step 1: Retrieve relevant tips from knowledge base ---
    raw_tasks = [st.task for st in scheduled_tasks]
    retrieved = retrieve_tips(raw_tasks, pets, max_tips=6)

    logger.info(
        "RAG retrieval | tasks=%d | pets=%s | tips_retrieved=%d",
        len(scheduled_tasks),
        [p.name for p in pets],
        len(retrieved),
    )

    # --- Step 2: Build prompt components ---
    schedule_summary = build_schedule_summary(scheduled_tasks, pets)
    context_block = build_context_block(retrieved)
    conflict_section = ""
    if conflicts:
        conflict_section = (
            "\nSCHEDULING CONFLICTS DETECTED:\n"
            + "\n".join(f"  - {c}" for c in conflicts)
            + "\nPlease address these conflicts in your advice.\n"
        )

    system_prompt = (
        "You are PawPal's AI Care Advisor — a warm, knowledgeable assistant for pet owners. "
        "Your job is to give practical, personalized daily care advice based strictly on the "
        "owner's actual schedule and the retrieved pet care tips provided below. "
        "You must ground your advice in the retrieved context — do not give generic tips "
        "that aren't relevant to this specific schedule. "
        "Keep your response friendly, concise (3–5 bullet points), and actionable. "
        "If there are scheduling conflicts, address them directly."
    )

    user_prompt = f"""Here is today's pet care schedule:

{schedule_summary}
{conflict_section}
RETRIEVED CARE TIPS (use these to ground your advice):
{context_block}

Based on this schedule and these retrieved tips, give the owner 3–5 specific, 
actionable pieces of advice for today. Reference the actual tasks and pet names. 
Do not repeat the schedule back — just give the advice."""

    # --- Step 3: Call Claude ---
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        advice = response.content[0].text
        logger.info(
            "Claude response received | input_tokens=%d | output_tokens=%d",
            response.usage.input_tokens,
            response.usage.output_tokens,
        )
        return advice

    except anthropic.AuthenticationError:
        logger.error("Authentication failed — invalid API key.")
        return "⚠️ API key is invalid. Check your ANTHROPIC_API_KEY in the sidebar."

    except anthropic.RateLimitError:
        logger.error("Rate limit hit.")
        return "⚠️ Rate limit reached. Wait a moment and try again."

    except anthropic.APIConnectionError as e:
        logger.error("Connection error: %s", e)
        return "⚠️ Could not connect to the AI service. Check your internet connection."

    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return f"⚠️ Something went wrong: {e}"
