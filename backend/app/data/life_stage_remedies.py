"""Home remedies for problems specific to a life stage — babies, kids/teens,
adults, and elders — supplied directly by the app's own team (Swetha) from
common household/traditional knowledge, not transcribed from any single
published source.
"""

LIFE_STAGE_REMEDIES_SEED: list[dict] = [
    # --- Babies / infants ---
    {
        "title": "Coconut oil or breast milk for diaper rash",
        "problem_tags": ["diaper_rash"],
        "ingredients": ["cold-pressed coconut oil or breast milk"],
        "instructions": (
            "Apply cold-pressed coconut oil or breast milk directly to the affected area.\n"
            "Let the baby go diaper-free for short periods to allow the skin to air out and heal."
        ),
        "caution": "See a pediatrician if the rash blisters, spreads, or doesn't improve within a few days.",
    },
    {
        "title": "Hing paste & leg massage for baby colic / gas",
        "problem_tags": ["colic", "bloating"],
        "ingredients": ["asafoetida (hing)", "warm water"],
        "instructions": (
            "Mix a pinch of asafoetida (hing) with warm water into a thin paste and apply it around "
            "the baby's navel (not inside it).\n"
            "Gently move the baby's legs in a bicycling motion to help release trapped gas."
        ),
        "caution": "Use only a tiny pinch of hing, applied externally — never give it orally to an infant. Consult a pediatrician for persistent crying.",
    },
    {
        "title": "Warm oil massage for cradle cap",
        "problem_tags": ["cradle_cap"],
        "ingredients": ["warm coconut or almond oil", "a soft baby brush", "mild baby shampoo"],
        "instructions": (
            "Gently massage the scalp with warm coconut or almond oil.\n"
            "Leave it on for 20 minutes, then use a soft baby brush to gently loosen the flakes "
            "before washing with a mild baby shampoo."
        ),
        "caution": "Be gentle — a baby's scalp is delicate. See a pediatrician if the scalp looks inflamed or infected.",
    },
    # --- Kids / teens ---
    {
        "title": "Neem bath & calamine for chickenpox itching",
        "problem_tags": ["chickenpox"],
        "ingredients": ["boiled neem leaves or colloidal oatmeal", "lukewarm bathwater", "calamine lotion"],
        "instructions": (
            "Add boiled neem leaves or colloidal oatmeal to lukewarm bathwater to soothe itching.\n"
            "Apply calamine lotion to the blisters to ease the intense itch."
        ),
        "caution": "Keep nails trimmed to reduce scratching/scarring. See a doctor for fever, breathing trouble, or signs of infected blisters.",
    },
    {
        "title": "Turmeric milk & mustard oil massage for children's cold",
        "problem_tags": ["cold"],
        "ingredients": ["turmeric", "milk", "warm mustard oil", "garlic", "carom seeds (ajwain)"],
        "instructions": (
            "Give warm turmeric milk (haldi doodh) before bed.\n"
            "Gently massage the chest and back with warm mustard oil infused with garlic and "
            "carom seeds (ajwain)."
        ),
        "caution": "Avoid giving honey to children under 1 year. See a doctor if fever is high or breathing is affected.",
    },
    {
        "title": "Brahmi milk & soaked almonds for exam stress",
        "problem_tags": ["exam_stress", "stress", "memory"],
        "ingredients": ["warm milk", "Brahmi powder or Ashwagandha", "almonds"],
        "instructions": (
            "Offer warm milk blended with a pinch of Brahmi powder or Ashwagandha before bed.\n"
            "Give 5-6 almonds soaked overnight and peeled, traditionally used to support memory "
            "and focus."
        ),
        "caution": "Check with a doctor before giving Ashwagandha regularly to children or teens.",
    },
    {
        "title": "Warm oil leg massage for growing pains",
        "problem_tags": ["growing_pains", "body_ache"],
        "ingredients": ["warm sesame or olive oil", "a warm heating pad"],
        "instructions": (
            "Massage the child's legs gently with warm sesame or olive oil before bedtime.\n"
            "Apply a warm heating pad to the aching muscles for 15 minutes."
        ),
        "caution": "See a doctor if pain is one-sided, persistent during the day, or accompanied by swelling or limping.",
    },
    # --- Adults ---
    {
        "title": "Papaya leaf juice & giloy for dengue/viral fever recovery",
        "problem_tags": ["dengue", "fever"],
        "ingredients": ["fresh papaya leaves", "fresh coconut water", "giloy (Tinospora cordifolia) stem"],
        "instructions": (
            "Drink 2-3 tablespoons of freshly extracted papaya leaf juice daily to help support "
            "platelet counts.\n"
            "Stay hydrated with fresh coconut water and giloy stem tea."
        ),
        "caution": "This supports recovery but doesn't replace medical care — dengue needs monitoring by a doctor, especially for platelet counts and warning signs.",
    },
    {
        "title": "Cold compress & rose water for conjunctivitis (Madras eye)",
        "problem_tags": ["conjunctivitis"],
        "ingredients": ["a cold compress", "pure medical-grade rose water"],
        "instructions": (
            "Apply a cold compress over closed eyelids multiple times a day.\n"
            "Place 1-2 drops of pure, medical-grade rose water in the eyes to reduce redness and "
            "burning."
        ),
        "caution": "Conjunctivitis spreads easily — avoid sharing towels/pillows and wash hands often. See a doctor if there's thick discharge, pain, or vision changes.",
    },
    {
        "title": "Sandalwood & multani mitti paste for heat rash / prickly heat",
        "problem_tags": ["heat_rash"],
        "ingredients": ["sandalwood powder", "rose water or multani mitti (Fuller's earth)", "neem-infused water"],
        "instructions": (
            "Apply a cooling paste made of sandalwood powder and rose water, or multani mitti, to "
            "the affected areas.\n"
            "Wash with neem-infused water to soothe and cleanse the skin."
        ),
        "caution": None,
    },
    {
        "title": "Ginger tea & peppermint oil for migraine",
        "problem_tags": ["migraine", "headache"],
        "ingredients": ["fresh ginger", "diluted peppermint essential oil"],
        "instructions": (
            "Drink strong ginger tea at the onset of the headache.\n"
            "Massage a drop of diluted peppermint essential oil into the temples and rest in a "
            "dark, quiet room."
        ),
        "caution": "See a doctor for migraines that are frequent, severe, or come with vision changes or numbness.",
    },
    {
        "title": "Barley water & cranberry juice for UTI",
        "problem_tags": ["uti"],
        "ingredients": ["barley grains", "water", "unsweetened cranberry juice"],
        "instructions": (
            "Drink barley water daily — boil barley grains in water, strain, and cool — to help "
            "flush the urinary tract.\n"
            "Consume unsweetened cranberry juice and significantly increase overall water intake."
        ),
        "caution": "See a doctor for a proper diagnosis and antibiotics if needed — UTIs can worsen quickly, especially with fever or back pain.",
    },
    {
        "title": "Warm compress for stye",
        "problem_tags": ["stye"],
        "ingredients": ["a warm, damp cloth or a warm green tea bag"],
        "instructions": (
            "Apply a warm, damp cloth or a warm green tea bag to the closed eye for 10-15 minutes, "
            "3-4 times a day, to help the stye rupture and drain naturally."
        ),
        "caution": "Never try to pop a stye yourself. See a doctor if it doesn't improve in a few days or affects vision.",
    },
    {
        "title": "Cumin-coriander water & ORS for food poisoning",
        "problem_tags": ["food_poisoning", "diarrhea", "vomiting"],
        "ingredients": ["cumin (jeera)", "coriander seeds", "water", "oral rehydration solution (ORS)", "bananas, rice, applesauce, toast (BRAT diet)"],
        "instructions": (
            "Drink water boiled with cumin (jeera) and coriander seeds.\n"
            "Sip oral rehydration solution (ORS) continuously to prevent dehydration.\n"
            "Once vomiting stops, stick to the BRAT diet (bananas, rice, applesauce, toast)."
        ),
        "caution": "See a doctor for high fever, blood in stool/vomit, signs of severe dehydration, or symptoms lasting more than a couple of days.",
    },
    {
        "title": "Hot-cold therapy & oil massage for back pain",
        "problem_tags": ["back_pain"],
        "ingredients": ["hot and cold packs", "warm Mahanarayan oil or sesame oil", "Epsom salts"],
        "instructions": (
            "Alternate between hot and cold packs on the affected area.\n"
            "Massage the back with warm Mahanarayan oil or sesame oil.\n"
            "Soak in a warm bath with Epsom salts for additional relief."
        ),
        "caution": "See a doctor if pain radiates down a leg, follows an injury, or comes with numbness or weakness.",
    },
    {
        "title": "Salt-sugar water & tulsi for low blood pressure",
        "problem_tags": ["low_blood_pressure"],
        "ingredients": ["salt", "sugar", "water", "fresh tulsi (holy basil) leaves", "black coffee"],
        "instructions": (
            "Drink a glass of water mixed with 1/2 teaspoon of salt and 1 teaspoon of sugar.\n"
            "Chew on 5-6 fresh tulsi leaves in the morning, or drink black coffee for a quick boost."
        ),
        "caution": "See a doctor if low blood pressure causes fainting, is frequent, or you're on medication that affects it.",
    },
    {
        "title": "Garlic/turmeric paste for ringworm & fungal skin infection",
        "problem_tags": ["ringworm"],
        "ingredients": ["fresh garlic or turmeric powder", "water", "diluted tea tree oil"],
        "instructions": (
            "Apply a paste of fresh garlic or turmeric powder and water directly to the patch.\n"
            "Alternatively, dab diluted tea tree oil onto the area using a cotton swab."
        ),
        "caution": "Keep the area dry and avoid sharing towels/clothing. See a doctor if it spreads or doesn't improve in 1-2 weeks.",
    },
    {
        "title": "Apple cider vinegar soak for athlete's foot",
        "problem_tags": ["athletes_foot"],
        "ingredients": ["apple cider vinegar", "warm water"],
        "instructions": (
            "Soak the feet in a basin of warm water mixed with half a cup of apple cider vinegar "
            "for 20 minutes daily.\n"
            "Ensure feet are thoroughly dried afterward, especially between the toes."
        ),
        "caution": "See a doctor if it spreads, doesn't improve, or you have diabetes (foot infections need prompt care).",
    },
    {
        "title": "Alum & vinegar wipe for body odor / excessive sweating",
        "problem_tags": ["body_odor"],
        "ingredients": ["alum (phitkari)", "diluted apple cider vinegar", "a cotton pad"],
        "instructions": (
            "Add a small block of alum (phitkari) to your bathing water.\n"
            "Wipe the underarms with a cotton pad soaked in diluted apple cider vinegar after "
            "showering."
        ),
        "caution": None,
    },
    {
        "title": "Ginger tea & hydration for vertigo / dizziness",
        "problem_tags": ["vertigo", "nausea"],
        "ingredients": ["ginger tea", "water"],
        "instructions": (
            "Drink ginger tea to reduce associated nausea.\n"
            "Sit down immediately, focus on a stationary object, and stay well hydrated, since "
            "dehydration is a common trigger."
        ),
        "caution": "See a doctor for frequent, severe, or unexplained dizziness, or if it comes with hearing changes or fainting.",
    },
    {
        "title": "Salt-turmeric gargle for tonsillitis / throat infection",
        "problem_tags": ["tonsillitis", "sore_throat"],
        "ingredients": ["salt", "turmeric", "warm water", "honey", "fresh ginger juice"],
        "instructions": (
            "Gargle with warm water containing half a teaspoon of salt and a pinch of turmeric.\n"
            "Drink warm water mixed with a tablespoon of honey and fresh ginger juice."
        ),
        "caution": "See a doctor for high fever, difficulty swallowing/breathing, or white patches on the tonsils — these need medical evaluation.",
    },
    {
        "title": "Curry leaf oil & amla paste for premature greying",
        "problem_tags": ["premature_greying", "hair_fall"],
        "ingredients": ["fresh curry leaves", "coconut oil", "Amla (Indian gooseberry) powder", "water"],
        "instructions": (
            "Boil a handful of fresh curry leaves in coconut oil until they turn black; cool and "
            "massage this oil into the scalp twice a week.\n"
            "Apply a paste of Amla powder and water to the hair roots."
        ),
        "caution": None,
    },
    # --- Elders ---
    {
        "title": "Warm compress & pendulum swings for frozen shoulder",
        "problem_tags": ["frozen_shoulder", "joint_pain"],
        "ingredients": ["a warm compress", "warm mustard oil", "garlic"],
        "instructions": (
            "Apply a warm compress to the shoulder joint for 15 minutes before doing gentle, "
            "pendulum-like arm swings.\n"
            "Massage the area with warm mustard oil infused with a few cloves of crushed garlic."
        ),
        "caution": "See a doctor/physiotherapist for a proper exercise plan — frozen shoulder needs guided movement, not just rest.",
    },
    {
        "title": "Ice then heat & turmeric milk for sciatica",
        "problem_tags": ["sciatica", "joint_pain"],
        "ingredients": ["ice packs", "a heating pad", "turmeric", "milk"],
        "instructions": (
            "Apply ice packs to the lower back for the first few days to reduce inflammation, then "
            "switch to a heating pad.\n"
            "Drink warm turmeric milk daily for its systemic anti-inflammatory benefits."
        ),
        "caution": "See a doctor if pain is severe, causes numbness/weakness in the leg, or affects bladder/bowel control (seek care immediately for the latter).",
    },
    {
        "title": "Warm mustard oil massage for chilblains",
        "problem_tags": ["chilblains"],
        "ingredients": ["warm mustard oil"],
        "instructions": (
            "Massage the fingers and toes gently with warm mustard oil to improve circulation.\n"
            "Keep the extremities elevated and warm, but avoid putting them directly against a "
            "room heater or hot water bag to prevent rapid temperature changes."
        ),
        "caution": "See a doctor if skin breaks, blisters, or doesn't improve with warmth — this can signal poor circulation that needs evaluation.",
    },
    {
        "title": "Ginger & rock salt before meals for low appetite in old age",
        "problem_tags": ["loss_of_appetite"],
        "ingredients": ["fresh ginger", "rock salt (kala namak)", "cumin and coriander seeds"],
        "instructions": (
            "Chew on a small, thin slice of fresh ginger sprinkled with a pinch of rock salt about "
            "15-20 minutes before a meal to stimulate digestive juices.\n"
            "Drink a light cumin and coriander seed tea in the morning."
        ),
        "caution": "Persistent loss of appetite in older adults can signal an underlying condition — worth a doctor's check if it continues.",
    },
]
