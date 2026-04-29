"""
pet_care_kb.py — PawPal+ Knowledge Base

A curated set of pet care tips organized by category and species.
The RAG advisor retrieves relevant entries based on the scheduled tasks
before passing them to Claude, so Claude's advice is grounded in
this specific knowledge rather than just general training data.
"""

# ---------------------------------------------------------------------------
# Knowledge base entries
# Each entry has: category, species (or "all"), and a tip string
# ---------------------------------------------------------------------------

KNOWLEDGE_BASE = [
    # --- Medication ---
    {
        "category": "medication",
        "species": "all",
        "tip": "Always give medication at the same time each day to maintain consistent blood levels. Set a phone alarm if needed.",
    },
    {
        "category": "medication",
        "species": "all",
        "tip": "Never abruptly stop a prescribed medication. Contact your vet before making any changes to dosage or schedule.",
    },
    {
        "category": "medication",
        "species": "dog",
        "tip": "Many dogs take pills more willingly when hidden in a small amount of peanut butter, cheese, or a pill pocket treat.",
    },
    {
        "category": "medication",
        "species": "cat",
        "tip": "For cats resistant to pills, ask your vet about compounding the medication into a flavored liquid or transdermal gel applied to the ear.",
    },
    {
        "category": "medication",
        "species": "all",
        "tip": "Log every dose given — date, time, and any reactions. This record is invaluable at vet visits.",
    },

    # --- Feeding ---
    {
        "category": "feeding",
        "species": "dog",
        "tip": "Dogs thrive on consistent meal times. Free-feeding can lead to obesity; scheduled meals make it easier to monitor appetite changes.",
    },
    {
        "category": "feeding",
        "species": "cat",
        "tip": "Cats are obligate carnivores. Ensure their food is high in animal protein and low in carbohydrates.",
    },
    {
        "category": "feeding",
        "species": "dog",
        "tip": "Wait at least 30 minutes after a large meal before vigorous exercise to reduce the risk of bloat (GDV), especially in large breeds.",
    },
    {
        "category": "feeding",
        "species": "cat",
        "tip": "Multiple small meals per day better match a cat's natural hunting pattern and can reduce vomiting from eating too fast.",
    },
    {
        "category": "feeding",
        "species": "all",
        "tip": "Fresh water should always be available. Change it at least once daily to keep it clean and appealing.",
    },
    {
        "category": "feeding",
        "species": "all",
        "tip": "Introduce any new food gradually over 7–10 days by mixing it with the old food to avoid digestive upset.",
    },

    # --- Walk ---
    {
        "category": "walk",
        "species": "dog",
        "tip": "Morning walks are great for dogs — they burn off overnight energy and provide mental stimulation before you start your day.",
    },
    {
        "category": "walk",
        "species": "dog",
        "tip": "On hot days, check the pavement temperature with the back of your hand. If it's too hot for your hand after 5 seconds, it's too hot for paw pads.",
    },
    {
        "category": "walk",
        "species": "dog",
        "tip": "Let your dog sniff during walks — it's mentally enriching and can be as tiring as physical exercise.",
    },
    {
        "category": "walk",
        "species": "dog",
        "tip": "Senior dogs still need walks, but shorter and more frequent outings are often better than one long walk.",
    },

    # --- Grooming ---
    {
        "category": "grooming",
        "species": "dog",
        "tip": "Brush your dog before bathing to remove tangles; wet mats are much harder to remove and can cause skin irritation.",
    },
    {
        "category": "grooming",
        "species": "cat",
        "tip": "Most cats groom themselves, but long-haired cats benefit from daily brushing to prevent mats and reduce hairballs.",
    },
    {
        "category": "grooming",
        "species": "all",
        "tip": "Check ears during grooming sessions for redness, odor, or discharge — early signs of infection are easy to miss otherwise.",
    },
    {
        "category": "grooming",
        "species": "all",
        "tip": "Trim nails every 3–4 weeks. Overgrown nails can cause pain, altered gait, and joint problems over time.",
    },
    {
        "category": "grooming",
        "species": "dog",
        "tip": "Make grooming a positive experience with treats and praise. Dogs that associate grooming with rewards are much easier to handle.",
    },

    # --- Appointment ---
    {
        "category": "appointment",
        "species": "all",
        "tip": "Bring a written list of questions and any behavioral changes you've noticed. Vet appointments go fast and it's easy to forget things.",
    },
    {
        "category": "appointment",
        "species": "all",
        "tip": "Withhold food for a few hours before a vet visit if your pet gets car sick — check with your vet for their recommendation.",
    },
    {
        "category": "appointment",
        "species": "cat",
        "tip": "Leave the cat carrier out in the home days before the appointment so the cat becomes comfortable with it and the visit is less stressful.",
    },
    {
        "category": "appointment",
        "species": "dog",
        "tip": "A tired dog is a calmer dog at the vet. A short walk before the appointment can help reduce anxiety in the waiting room.",
    },
    {
        "category": "appointment",
        "species": "all",
        "tip": "Keep a copy of your pet's vaccination records, medications, and any past diagnoses. Many vets now offer digital records via an app.",
    },

    # --- General / other ---
    {
        "category": "other",
        "species": "all",
        "tip": "Enrichment activities — puzzle feeders, scent games, training — keep pets mentally sharp and reduce boredom behaviors.",
    },
    {
        "category": "other",
        "species": "dog",
        "tip": "Rotate toys weekly to keep them feeling 'new.' Dogs habituate quickly to the same toys and lose interest.",
    },
    {
        "category": "other",
        "species": "cat",
        "tip": "Provide vertical space — cat trees, shelves, perches — so cats can observe their environment from a safe height.",
    },
    {
        "category": "other",
        "species": "all",
        "tip": "Watch for subtle behavioral changes like hiding, appetite shifts, or unusual vocalizations — they're often the first sign something is wrong.",
    },
]


def retrieve_tips(tasks, pets, max_tips: int = 6) -> list[dict]:
    """
    RAG retrieval: given a list of scheduled Tasks and Pet objects,
    find the most relevant knowledge base entries.

    Strategy:
    - Match tips by category (must match a scheduled task's category)
    - Prefer species-specific tips over generic "all" tips
    - Deduplicate and cap at max_tips

    Returns a list of tip dicts with keys: category, species, tip
    """
    # Collect categories present in scheduled tasks
    scheduled_categories = {task.category for task in tasks}

    # Collect species present among the owner's pets
    pet_species = {pet.species for pet in pets}

    scored = []
    for entry in KNOWLEDGE_BASE:
        if entry["category"] not in scheduled_categories:
            continue

        # Score: species-specific match scores higher than "all"
        if entry["species"] in pet_species:
            score = 2
        elif entry["species"] == "all":
            score = 1
        else:
            continue  # tip is for a species not present

        scored.append((score, entry))

    # Sort: higher score first, then stable order
    scored.sort(key=lambda x: x[0], reverse=True)

    # Deduplicate tips (identical tip text)
    seen = set()
    results = []
    for _, entry in scored:
        if entry["tip"] not in seen:
            seen.add(entry["tip"])
            results.append(entry)
        if len(results) >= max_tips:
            break

    return results
