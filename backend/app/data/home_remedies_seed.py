"""Curated seed set of traditional Indian household/kitchen remedies.

These are well-known folk remedies passed down across generations, using
common kitchen ingredients, for everyday minor discomforts. They are
presented as traditional practice, not as clinical treatment: each entry
carries a `caution` field telling the user when to stop relying on the
remedy and see a doctor instead. Scope is deliberately limited to mild,
common, low-risk discomforts — nothing here substitutes for diagnosis or
treatment of a serious or persistent condition.

Seeded once at startup (see seed_home_remedies in services/remedies.py);
re-running is idempotent (checks by title before inserting).
"""

HOME_REMEDIES_SEED: list[dict] = [
    {
        "title": "Ginger-honey-tulsi tea for cough and cold",
        "problem_tags": ["cold", "cough", "sore_throat", "fever"],
        "ingredients": ["ginger (grated, 1 tsp)", "tulsi/holy basil leaves (5-6)", "honey (1 tsp)", "water (1 cup)"],
        "instructions": "Boil grated ginger and tulsi leaves in water for 5 minutes. Strain, let cool slightly, then stir in honey. Sip warm, 2-3 times a day.",
        "caution": "Avoid giving honey to children under 1 year. See a doctor if fever is high, cough lasts more than a week, or breathing feels difficult.",
    },
    {
        "title": "Turmeric milk (haldi doodh) for cold and sore throat",
        "problem_tags": ["cold", "sore_throat", "body_ache", "fever"],
        "ingredients": ["milk (1 cup)", "turmeric powder (1/2 tsp)", "black pepper (a pinch, optional)"],
        "instructions": "Warm the milk, stir in turmeric (and pepper if using), and drink before bed.",
        "caution": "People on blood-thinning medication should check with a doctor before regular turmeric use.",
    },
    {
        "title": "Salt water gargle for sore throat",
        "problem_tags": ["sore_throat", "mouth_ulcers"],
        "ingredients": ["warm water (1 cup)", "salt (1/2 tsp)"],
        "instructions": "Dissolve salt in warm water and gargle for 30 seconds, a few times a day.",
        "caution": "Do not swallow the gargle water. See a doctor if throat pain is severe or you have trouble swallowing.",
    },
    {
        "title": "Jeera (cumin) water for indigestion",
        "problem_tags": ["indigestion", "bloating", "acidity"],
        "ingredients": ["cumin seeds (1 tsp)", "water (1 cup)"],
        "instructions": "Boil cumin seeds in water for a few minutes, strain, and sip warm after meals.",
        "caution": "See a doctor if abdominal pain is severe, persistent, or accompanied by vomiting or fever.",
    },
    {
        "title": "Ajwain (carom seed) water for acidity and gas",
        "problem_tags": ["acidity", "bloating", "indigestion"],
        "ingredients": ["ajwain/carom seeds (1 tsp)", "warm water (1 cup)"],
        "instructions": "Dry-roast ajwain lightly, crush, and steep in warm water for 5 minutes before drinking.",
        "caution": "Avoid large amounts during pregnancy. See a doctor if symptoms persist beyond a few days.",
    },
    {
        "title": "Ginger tea for nausea",
        "problem_tags": ["nausea", "motion_sickness"],
        "ingredients": ["fresh ginger (small piece)", "water (1 cup)", "honey (optional)"],
        "instructions": "Simmer sliced ginger in water for 5-10 minutes, strain, add honey if desired, sip slowly.",
        "caution": "See a doctor if vomiting is persistent, severe, or you can't keep fluids down.",
    },
    {
        "title": "Warm compress and ginger-fennel tea for menstrual cramps",
        "problem_tags": ["menstrual_cramps"],
        "ingredients": ["fennel seeds (1 tsp)", "ginger (small piece)", "water (1 cup)", "hot water bottle or warm cloth"],
        "instructions": "Boil fennel seeds and ginger in water for 5 minutes, strain and sip warm. Apply a warm compress to the lower abdomen.",
        "caution": "See a doctor if pain is severe, worsening, or different from your usual pattern.",
    },
    {
        "title": "Warm milk with a pinch of nutmeg for sleep",
        "problem_tags": ["insomnia", "stress"],
        "ingredients": ["milk (1 cup)", "nutmeg powder (a small pinch)"],
        "instructions": "Warm the milk, stir in a small pinch of nutmeg, and drink about 30 minutes before bed.",
        "caution": "Use only a small pinch of nutmeg — larger amounts can cause discomfort. See a doctor if sleep problems persist for weeks.",
    },
    {
        "title": "Aloe vera gel for minor burns and sunburn",
        "problem_tags": ["minor_burns", "sunburn", "skin_irritation"],
        "ingredients": ["fresh aloe vera gel"],
        "instructions": "Cool the burn under running water first for several minutes, then apply fresh aloe vera gel gently to the area.",
        "caution": "For burns larger than a small area, deep burns, blistering, or burns on the face/hands/genitals, seek medical care immediately — do not rely on home care.",
    },
    {
        "title": "Clove oil dab for toothache",
        "problem_tags": ["toothache", "mouth_ulcers"],
        "ingredients": ["clove oil (a few drops)", "cotton ball"],
        "instructions": "Dab a small amount of clove oil onto a cotton ball and hold gently against the affected tooth/gum.",
        "caution": "This is temporary relief only — see a dentist for the underlying problem, especially if pain is severe or there's swelling.",
    },
    {
        "title": "Coconut oil for dry skin and chapped lips",
        "problem_tags": ["dry_skin", "chapped_lips"],
        "ingredients": ["virgin coconut oil"],
        "instructions": "Apply a small amount of coconut oil to the affected area after washing, a couple of times a day.",
        "caution": "Discontinue if you notice irritation or an allergic reaction.",
    },
    {
        "title": "Fenugreek (methi) water for mild constipation",
        "problem_tags": ["constipation", "indigestion"],
        "ingredients": ["fenugreek seeds (1 tsp)", "water (1 cup)"],
        "instructions": "Soak fenugreek seeds in water overnight; drink the water (and seeds if desired) in the morning.",
        "caution": "See a doctor if constipation is severe, lasts more than a week, or comes with abdominal pain or blood in stool.",
    },
    {
        "title": "Soaked raisins (kishmish) water for constipation",
        "problem_tags": ["constipation"],
        "ingredients": ["raisins (8-10)", "water (1 cup)"],
        "instructions": "Soak raisins in water overnight. Eat the raisins and drink the water in the morning on an empty stomach.",
        "caution": "People with diabetes should be mindful of the sugar content. See a doctor for persistent constipation.",
    },
    {
        "title": "Peppermint oil temple massage for tension headache",
        "problem_tags": ["headache"],
        "ingredients": ["peppermint oil (diluted, a few drops)", "carrier oil (coconut/almond, 1 tsp)"],
        "instructions": "Mix peppermint oil with a carrier oil and gently massage onto temples and forehead.",
        "caution": "Avoid near eyes. See a doctor for sudden severe headaches, headaches with vision changes, or ones that don't improve with rest.",
    },
    {
        "title": "Steam inhalation with eucalyptus/ajwain for blocked nose",
        "problem_tags": ["cold", "blocked_nose", "sinus_congestion"],
        "ingredients": ["hot water (a bowl)", "eucalyptus oil or ajwain seeds (a few drops/1 tsp)"],
        "instructions": "Add eucalyptus oil or ajwain to a bowl of hot (not boiling) water, lean over with a towel over your head, and breathe the steam for 5-10 minutes.",
        "caution": "Keep a safe distance to avoid scalding. Not recommended for young children. See a doctor if congestion lasts more than 10 days or comes with high fever.",
    },
]
