"""Additional home remedies for everyday problems not covered by the
curated or CCRAS-sourced lists — supplied directly by the app's own team
(Swetha) from common household/wellness knowledge, not transcribed from
any single published source. Covers common complaints (eye strain,
immunity, muscle cramps, cholesterol, PMS, teething, etc.) with widely
known, generic self-care practices.
"""

GENERAL_REMEDIES_SEED: list[dict] = [
    {
        "title": "Warm compress for eye strain & tired eyes",
        "problem_tags": ["eye_strain"],
        "ingredients": ["warm water or a warm compress", "chilled cucumber slices (optional)"],
        "instructions": (
            "Apply a warm compress over closed eyelids for a few minutes to relax eye muscles, "
            "or use chilled cucumber slices over closed eyes for a cooling, soothing effect.\n"
            "Follow the 20-20-20 rule during screen use: every 20 minutes, look at something "
            "20 feet away for 20 seconds, to reduce strain."
        ),
        "caution": None,
    },
    {
        "title": "Ginger-honey-lemon tea for cold prevention & immunity",
        "problem_tags": ["cold", "immunity"],
        "ingredients": ["fresh ginger", "honey", "lemon", "vitamin C-rich foods (citrus, bell peppers)", "zinc-rich foods"],
        "instructions": (
            "Drink ginger tea with honey and lemon regularly, especially during cold season.\n"
            "Increase intake of Vitamin C (citrus fruits, bell peppers) and zinc-rich foods to "
            "support immunity.\n"
            "Prioritize 7-9 hours of sleep, which is essential for a healthy immune response."
        ),
        "caution": "Avoid giving honey to children under 1 year of age.",
    },
    {
        "title": "Fennel & peppermint for gas / flatulence",
        "problem_tags": ["bloating", "abdominal_pain"],
        "ingredients": ["peppermint or chamomile tea", "fennel seeds", "warm water", "fresh ginger"],
        "instructions": (
            "Sip peppermint or chamomile tea to ease gas and bloating.\n"
            "Chew half a teaspoon of fennel seeds after meals to aid digestion.\n"
            "Alternatively, drink warm water with a pinch of grated ginger."
        ),
        "caution": None,
    },
    {
        "title": "Potassium & heat therapy for muscle cramps",
        "problem_tags": ["body_ache"],
        "ingredients": ["bananas, spinach (potassium/magnesium-rich foods)", "a warm heating pad", "pickle juice"],
        "instructions": (
            "Increase potassium and magnesium intake through foods like bananas and spinach.\n"
            "Apply a warm heating pad to the affected muscle and gently stretch the area.\n"
            "Pickle juice can give quick electrolyte replenishment for sudden cramps."
        ),
        "caution": "See a doctor if cramps are frequent, severe, or unexplained.",
    },
    {
        "title": "Overnight soak & moisturize for dry/cracked heels",
        "problem_tags": ["dry_skin"],
        "ingredients": ["warm soapy water", "a pumice stone", "petroleum jelly or coconut oil", "cotton socks"],
        "instructions": (
            "Soak feet in warm, soapy water for 15 minutes to soften the skin.\n"
            "Gently scrub cracked areas with a pumice stone.\n"
            "Apply a thick layer of petroleum jelly or coconut oil and wear cotton socks overnight "
            "to lock in moisture."
        ),
        "caution": None,
    },
    {
        "title": "Oil suffocation method for hair lice",
        "problem_tags": ["hair_lice"],
        "ingredients": ["olive oil, almond oil, or mayonnaise", "a shower cap", "a fine-tooth metal nit comb"],
        "instructions": (
            "Coat the hair completely in olive oil, almond oil, or mayonnaise.\n"
            "Cover with a shower cap and leave overnight to suffocate the lice.\n"
            "The next day, comb through wet hair thoroughly with a fine-tooth metal nit comb to "
            "remove lice and eggs. Repeat over several days as needed."
        ),
        "caution": "Check with a doctor or pharmacist before use on young children.",
    },
    {
        "title": "Pinch & lean forward for nosebleed",
        "problem_tags": ["nosebleed"],
        "ingredients": ["a cold compress"],
        "instructions": (
            "Sit upright and lean slightly forward — never backward.\n"
            "Pinch the soft part of the nose just below the bony bridge continuously for 10-15 minutes.\n"
            "Apply a cold compress to the bridge of the nose to help constrict blood vessels."
        ),
        "caution": "See a doctor if bleeding doesn't stop after 20-30 minutes, or is frequent/heavy.",
    },
    {
        "title": "Electrolytes & ginger for hangover",
        "problem_tags": ["hangover", "nausea"],
        "ingredients": ["clear broth or a sports drink", "bland complex carbs (toast, crackers)", "ginger tea"],
        "instructions": (
            "Drink clear broths or sports drinks to replenish lost electrolytes.\n"
            "Eat bland, complex carbohydrates like toast or crackers to settle the stomach.\n"
            "Ginger tea helps calm nausea."
        ),
        "caution": None,
    },
    {
        "title": "Hydration & small meals for mild fatigue",
        "problem_tags": ["fatigue"],
        "ingredients": ["water", "small frequent meals", "natural sunlight"],
        "instructions": (
            "Stay well hydrated throughout the day.\n"
            "Eat small, frequent meals to keep blood sugar stable rather than large infrequent ones.\n"
            "Take a brisk 10-minute walk in natural sunlight to help boost energy levels."
        ),
        "caution": "See a doctor if fatigue is persistent or unexplained — it can signal an underlying condition.",
    },
    {
        "title": "Apple cider vinegar & fiber for weight management",
        "problem_tags": ["weight_management"],
        "ingredients": ["apple cider vinegar", "warm water", "dietary fiber (vegetables, whole grains)", "lean protein", "green tea"],
        "instructions": (
            "Drink a glass of warm water with a tablespoon of apple cider vinegar before meals.\n"
            "Increase dietary fiber and lean protein intake.\n"
            "Replace sugary drinks with green tea."
        ),
        "caution": "Dilute apple cider vinegar well — undiluted vinegar can irritate the throat and erode tooth enamel.",
    },
    {
        "title": "Hibiscus tea & low sodium for high blood pressure",
        "problem_tags": ["high_blood_pressure"],
        "ingredients": ["hibiscus tea", "potassium-rich foods", "reduced sodium intake"],
        "instructions": (
            "Drink hibiscus tea daily.\n"
            "Reduce sodium intake and eat more potassium-rich foods (bananas, leafy greens).\n"
            "Practice deep breathing or meditation regularly for stress reduction, which also helps "
            "blood pressure."
        ),
        "caution": "This supports but does not replace prescribed blood pressure medication — consult a doctor before relying on it, especially if already on medication.",
    },
    {
        "title": "Garlic & soluble fiber for high cholesterol",
        "problem_tags": ["high_cholesterol"],
        "ingredients": ["raw garlic", "oats and beans (soluble fiber)", "unsalted almonds or walnuts"],
        "instructions": (
            "Consume raw garlic daily.\n"
            "Increase soluble fiber intake through oats and beans.\n"
            "Eat a handful of unsalted almonds or walnuts daily."
        ),
        "caution": "Consult a doctor before relying on this if already on cholesterol medication.",
    },
    {
        "title": "Iron + Vitamin C pairing for anemia",
        "problem_tags": ["anemia"],
        "ingredients": ["iron-rich foods (spinach, lentils, red meat)", "Vitamin C sources (lemon)", "a cast-iron skillet (optional)"],
        "instructions": (
            "Eat iron-rich foods such as spinach, lentils, and red meat.\n"
            "Pair them with Vitamin C sources — like a squeeze of lemon — to maximize iron absorption.\n"
            "Cooking acidic foods in a cast-iron skillet can also slightly increase their iron content."
        ),
        "caution": "Confirmed anemia needs medical diagnosis and treatment — see a doctor rather than self-treating alone.",
    },
    {
        "title": "Colloidal oatmeal bath for eczema / psoriasis",
        "problem_tags": ["eczema"],
        "ingredients": ["colloidal oatmeal", "lukewarm water", "unrefined coconut oil or aloe vera gel"],
        "instructions": (
            "Take lukewarm baths with colloidal oatmeal added to soothe irritated skin.\n"
            "Apply unrefined coconut oil or aloe vera gel to damp skin immediately after bathing "
            "to lock in moisture."
        ),
        "caution": "See a dermatologist for persistent or severe flare-ups.",
    },
    {
        "title": "Tea tree spot treatment for pimples & blackheads",
        "problem_tags": ["acne", "pimples"],
        "ingredients": ["tea tree oil (diluted)", "honey", "cinnamon", "hot water for steaming"],
        "instructions": (
            "Apply a spot treatment of diluted tea tree oil directly to pimples.\n"
            "A honey and cinnamon mask can help with its antibacterial properties.\n"
            "Steam your face over a bowl of hot water to open pores before cleansing."
        ),
        "caution": "Always dilute tea tree oil before applying to skin — undiluted oil can cause irritation.",
    },
    {
        "title": "Elevation & witch hazel for varicose veins",
        "problem_tags": ["varicose_veins"],
        "ingredients": ["witch hazel", "a cotton pad", "compression stockings"],
        "instructions": (
            "Elevate your legs above heart level for 15 minutes, several times a day.\n"
            "Apply witch hazel locally using a cotton pad to help reduce swelling.\n"
            "Wearing compression stockings can also help with symptoms."
        ),
        "caution": "See a doctor if veins are painful, rapidly worsening, or you notice skin changes.",
    },
    {
        "title": "Oil massage & vinegar soak for brittle nails",
        "problem_tags": ["brittle_nails"],
        "ingredients": ["olive oil or coconut oil", "warm water", "apple cider vinegar"],
        "instructions": (
            "Massage cuticles daily with olive oil or coconut oil.\n"
            "Soak nails in a mixture of warm water and apple cider vinegar for 10 minutes."
        ),
        "caution": None,
    },
    {
        "title": "Saltwater rinse & probiotic yogurt for oral thrush",
        "problem_tags": ["oral_thrush"],
        "ingredients": ["salt", "warm water", "plain unsweetened yogurt with active probiotic cultures"],
        "instructions": (
            "Rinse the mouth with a warm saltwater solution (1/2 tsp salt in 1 cup warm water), "
            "several times a day.\n"
            "Eat plain, unsweetened yogurt containing active probiotic cultures to help restore "
            "healthy bacteria."
        ),
        "caution": "See a doctor if thrush doesn't improve within a week, especially in infants or anyone with a weakened immune system.",
    },
    {
        "title": "Oil pulling & aloe rinse for gum disease",
        "problem_tags": ["gum_disease", "bleeding_gums"],
        "ingredients": ["coconut or sesame oil", "aloe vera juice"],
        "instructions": (
            "Practice oil pulling by swishing a tablespoon of coconut or sesame oil in the mouth "
            "for about 15 minutes daily, then spitting it out (never swallow).\n"
            "Rinse with aloe vera juice to help reduce gum inflammation."
        ),
        "caution": "See a dentist for proper diagnosis and treatment — this supports but doesn't replace dental care.",
    },
    {
        "title": "Ice & lysine for cold sores",
        "problem_tags": ["cold_sores"],
        "ingredients": ["an ice pack", "aloe vera gel or lemon balm extract", "lysine-rich foods"],
        "instructions": (
            "Apply an ice pack directly to the area at the first sign of tingling, to reduce "
            "severity and duration.\n"
            "Dab on aloe vera gel or lemon balm extract.\n"
            "Increase intake of lysine-rich foods, which may help healing."
        ),
        "caution": "Cold sores are contagious — avoid touching the area and then your eyes or others.",
    },
    {
        "title": "Baking soda paste & chamomile for insect/mosquito bites",
        "problem_tags": ["insect_bites"],
        "ingredients": ["baking soda", "water", "a chilled chamomile tea bag or aloe vera gel"],
        "instructions": (
            "Apply a thick paste made of baking soda and water to the bite to reduce itching.\n"
            "Rub a chilled chamomile tea bag or aloe vera gel over the area for additional relief."
        ),
        "caution": "See a doctor for signs of allergic reaction (spreading swelling, difficulty breathing) or infection.",
    },
    {
        "title": "Oil massage for scars & stretch marks",
        "problem_tags": ["scars"],
        "ingredients": ["rosehip seed oil, vitamin E oil, or cocoa butter"],
        "instructions": (
            "Massage the area daily with rosehip seed oil, vitamin E oil, or pure cocoa butter to "
            "improve skin elasticity and support healing over time."
        ),
        "caution": None,
    },
    {
        "title": "Chilled tea bags for puffy eyes & dark circles",
        "problem_tags": ["puffy_eyes"],
        "ingredients": ["chilled caffeinated tea bags or cold metal spoons", "an extra pillow"],
        "instructions": (
            "Place chilled, damp caffeinated tea bags or cold metal spoons over closed eyes for "
            "about 10 minutes.\n"
            "Elevate your head with an extra pillow while sleeping to help prevent fluid pooling."
        ),
        "caution": None,
    },
    {
        "title": "Magnesium & calming tea for PMS",
        "problem_tags": ["pms", "stress"],
        "ingredients": ["magnesium supplement or dark chocolate", "chamomile or oat straw tea"],
        "instructions": (
            "Take a magnesium supplement, or eat magnesium-rich dark chocolate.\n"
            "Drink chamomile or oat straw tea to help calm the nervous system."
        ),
        "caution": None,
    },
    {
        "title": "Fenugreek & warm compress for breastfeeding support",
        "problem_tags": ["lactation"],
        "ingredients": ["fenugreek or fennel seed tea", "oatmeal", "a warm compress"],
        "instructions": (
            "Drink fenugreek or fennel seed tea, traditionally used to support milk supply.\n"
            "Eat a bowl of oatmeal daily.\n"
            "Apply a warm compress to the breasts right before nursing to help with let-down."
        ),
        "caution": "Consult a lactation consultant or doctor if you have ongoing supply concerns.",
    },
    {
        "title": "Chilled washcloth for children's teething pain",
        "problem_tags": ["teething"],
        "ingredients": ["a clean, chilled (not frozen) damp washcloth"],
        "instructions": (
            "Offer a clean, chilled (not frozen) damp washcloth for the child to chew on.\n"
            "Gently massage the gums with a clean finger to ease discomfort."
        ),
        "caution": "Never give a frozen object to a teething child — it can injure the gums. Consult a pediatrician for persistent fussiness or fever.",
    },
    {
        "title": "Peri bottle & sitz bath for post-pregnancy recovery",
        "problem_tags": ["postpartum_care"],
        "ingredients": ["a peri bottle", "warm water", "witch hazel"],
        "instructions": (
            "Use a peri bottle with warm water during bathroom visits for gentler, more comfortable "
            "cleansing.\n"
            "Take shallow, warm sitz baths infused with witch hazel to soothe the perineal area."
        ),
        "caution": "See a doctor for signs of infection (fever, foul odor, worsening pain) or heavy bleeding.",
    },
    {
        "title": "Side-sleeping & steam inhalation for snoring",
        "problem_tags": ["snoring"],
        "ingredients": ["eucalyptus or peppermint essential oil", "steam (hot water)"],
        "instructions": (
            "Sleep on your side rather than your back to reduce airway obstruction.\n"
            "Inhale steam with a few drops of eucalyptus or peppermint essential oil before bed to "
            "clear nasal passages.\n"
            "Elevate the head of the bed by a few inches."
        ),
        "caution": "Loud, frequent snoring with gasping or daytime fatigue can indicate sleep apnea — see a doctor.",
    },
]
