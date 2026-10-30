"""Home remedies sourced from "Ayurvedic Home Remedies", published by the
Central Council for Research in Ayurveda and Siddha (CCRAS), Department of
ISM&H, Ministry of Health & Family Welfare, Government of India (reprint
2005). An authoritative, official source — unlike the hand-curated
HOME_REMEDIES_SEED entries, these come from a government Ayurveda
research body.

One entry per kitchen ingredient (25 total, matching the booklet's index),
each covering every ailment that ingredient is used for in the source —
this mirrors how people actually think about home remedies ("what is
ginger good for") and keeps the remedy list browsable rather than
fragmenting into 100+ near-duplicate single-line entries. Every ailment
is still fully searchable: RemedyService.search() matches the search
query against title, problem_tags, AND the full instructions text.

Dosages are as published for adults; see the booklet's own general
instructions (halve or quarter doses for children, stop if discomfort
occurs, see a doctor if no relief within 2-3 days) — reflected in each
entry's `caution` field where the source called it out specifically.
"""

AYURVEDIC_REMEDIES_SEED: list[dict] = [
    {
        "title": "Adrak/Sonth (Ginger) — for indigestion, cold, cough, headache & more",
        "problem_tags": ["indigestion", "ear_pain", "cold", "cough", "headache", "abdominal_pain", "body_ache"],
        "ingredients": ["ginger (Zingiber officinale) — fresh rhizome and dry powder (sonth)"],
        "instructions": (
            "Indigestion: 5 gm crushed rhizome with salt or jaggery, twice daily before meals.\n"
            "Ear pain: 2-4 drops of fresh warm ginger juice instilled in the ear.\n"
            "Hoarseness of voice: 1-3 gm powder of dry rhizome with honey, in three divided doses.\n"
            "Aches & pains: 10-20 ml decoction from 2 gm dry rhizome, twice a day.\n"
            "Cold/Cough: 2-5 gm powder of dry rhizome with jaggery, thrice a day in divided doses. "
            "10 ml decoction from a piece of ginger every morning helps prevent recurrent colds.\n"
            "Headache: warm ginger paste applied over the forehead, up to 3-4 times a day.\n"
            "Abdominal pain: 5 ml ginger juice in a glass of buttermilk with lemon & salt."
        ),
        "caution": "Do not use ginger juice in the ear if there is any discharge.",
    },
    {
        "title": "Ajvain (Carom seeds) — for piles, gas, sinus congestion & more",
        "problem_tags": ["piles", "menstrual_cramps", "skin_allergy", "abdominal_pain", "bloating", "sinus_congestion", "blocked_nose", "loss_of_appetite"],
        "ingredients": ["carom seeds / ajwain (Trachyspermum ammi)"],
        "instructions": (
            "Piles: 1 gm powder with 1 gm black salt in buttermilk, twice daily.\n"
            "Painful menses: 1-2 gm powder of seeds with warm milk, thrice a day for 2-3 days.\n"
            "Urticaria/skin allergy: 1-2 gm powder of seeds with water, twice daily.\n"
            "Abdominal pain: 1 gm powder with lukewarm water, twice or thrice.\n"
            "Flatulence (gas): 2 gm ajvain powder with an equal quantity of saunf (fennel) powder, with warm water.\n"
            "Sinusitis: warm paste applied over the forehead and lightly below the eyes, in the morning.\n"
            "Nasal block: 1-2 gm powder in steaming water, vapour inhaled 2-3 times a day.\n"
            "Loss of appetite: 1 gm powder with warm water, half an hour before meals."
        ),
        "caution": None,
    },
    {
        "title": "Anar (Pomegranate) — for indigestion, bleeding piles, acidity & more",
        "problem_tags": ["indigestion", "piles", "diarrhea", "acidity", "bad_breath", "acne"],
        "ingredients": ["pomegranate (Punica granatum) — fruit juice, rind and seeds"],
        "instructions": (
            "A very nutritious fruit, suitable for all and usable alongside diet in almost any condition.\n"
            "Indigestion: 10 ml fruit juice with 1 gm black salt or fried jeera powder, with honey or sugar, held in the mouth a while before food.\n"
            "Bleeding piles: 10 ml fruit juice with sugar twice a day, or 10 gm powder of dry fruit rind with an equal quantity of sugar twice a day.\n"
            "Diarrhoea/Dysentery: 10 ml decoction of fruit skin thrice a day; the fruit may also be eaten in plenty.\n"
            "Hyper-acidity: 10 ml fruit juice twice a day (the fruit itself may also be eaten).\n"
            "Bad breath: gargle with warm decoction of fruit skin, 3-4 times a day.\n"
            "Acne: paste of seeds applied to the affected part, twice daily."
        ),
        "caution": None,
    },
    {
        "title": "Amla (Indian gooseberry) — for acidity, stress, diabetes, hair & gums",
        "problem_tags": ["acidity", "constipation", "stress", "diabetes", "hair_fall", "dandruff", "bleeding_gums"],
        "ingredients": ["Indian gooseberry / amla (Emblica officinalis)"],
        "instructions": (
            "General health: regular use of amla provides nutrition and boosts good health.\n"
            "Hyperacidity/Peptic ulcer/Constipation: 3-5 gm powdered fruit rind twice a day with milk, "
            "or 10-20 ml fruit juice twice a day (raw amla can also be eaten).\n"
            "Stress: external application of 25-50 gm fruit rind ground in buttermilk, on the forehead.\n"
            "Diabetes: 10-20 ml fruit juice with 10-20 ml juice of fresh turmeric (haldi) rhizome, twice a day.\n"
            "Greying of hair/Hair fall/Dandruff: fruit rind soaked overnight in water, applied to scalp two hours "
            "before bath; or paste from fruit rind applied two hours before bath. 1-2 fresh fruits eaten every "
            "morning helps prevent hair fall and early greying.\n"
            "Bleeding gums: fine amla powder gently massaged onto gums after brushing, at least twice daily."
        ),
        "caution": None,
    },
    {
        "title": "Dalchini (Cinnamon) — for indigestion, vomiting, headache & stress",
        "problem_tags": ["indigestion", "loss_of_appetite", "vomiting", "headache", "stress", "cough"],
        "ingredients": ["cinnamon (Cinnamomum zeylanicum) — bark powder"],
        "instructions": (
            "A commonly used digestive spice with a soothing effect on the mind.\n"
            "Indigestion: 2 gm powder of bark with water, twice a day.\n"
            "Loss of appetite: 2 gm powder of equal parts dalchini and ajvain, chewed in three divided doses before food.\n"
            "Vomiting: 1-2 gm powder with honey, thrice a day in divided doses.\n"
            "Tension headache: rubbed with water on a rough surface and applied to the forehead.\n"
            "Mental tension: the aroma has a soothing action — crushed pieces can be kept in a hanky or near the pillow.\n"
            "Dry cough: chewing controls throat irritation and helps with dry cough."
        ),
        "caution": None,
    },
    {
        "title": "Dhania (Coriander) — for cold, worms, heatstroke & fever",
        "problem_tags": ["cold", "cough", "intestinal_worms", "sun_stroke", "dehydration", "indigestion", "fever"],
        "ingredients": ["coriander seeds (Coriandrum sativum)"],
        "instructions": (
            "Cold/Cough: 20 ml decoction from 5 gm coarse powder with sugar and turmeric, thrice a day. "
            "Dhania powder as a herbal tea every morning helps prevent cold, cough and digestion problems.\n"
            "Intestinal worms: 3-5 gm powder with jaggery, twice a day for 5 days.\n"
            "Sun stroke/Dehydration: 20 ml decoction from coarse powder with sugar and a pinch of salt, frequently.\n"
            "Indigestion: 20 ml decoction from 5 gm coarse powder with a pinch of ginger powder, thrice a day.\n"
            "Fever: 20 ml decoction from 5 gm powder with sugar, 3-4 times a day."
        ),
        "caution": None,
    },
    {
        "title": "Elaichi (Cardamom) — for hiccups, vomiting, cold & cough",
        "problem_tags": ["hiccup", "vomiting", "bad_breath", "diarrhea", "cold", "cough"],
        "ingredients": ["cardamom (Elettaria cardamomum)"],
        "instructions": (
            "Hiccough: 1-2 fruits chewed frequently (not more than 4/day).\n"
            "Vomiting: 250-500 mg powder of seeds fried in ghee, thrice daily with honey.\n"
            "Bad breath: 1-2 seeds chewed frequently (not more than 4/day).\n"
            "Diarrhoea/Vomiting: ash of elaichi skin, 2 gm with a little honey, 4-5 times a day.\n"
            "Cold: 20 ml decoction from 5 gm dhania, 1 gm methi seeds and a little turmeric, 2-3 times a day.\n"
            "Cough: elaichi powder with a teaspoon of honey, 3-4 times a day; chewing elaichi (not more than 3/day) "
            "also helps with both dry and productive cough."
        ),
        "caution": None,
    },
    {
        "title": "Ghee (Clarified Butter) — for wounds, appetite, memory & constipation",
        "problem_tags": ["wounds_burns", "loss_of_appetite", "memory", "constipation"],
        "ingredients": ["ghee (clarified butter)"],
        "instructions": (
            "Ghee is used as a vehicle for many Ayurvedic medicines; judicious use is good for physical and "
            "psychological health.\n"
            "Ulcer/Wounds/Burns: applied over the affected part frequently.\n"
            "Loss of appetite: with hing and jeera powder, mixed into food.\n"
            "Memory: daily use of ghee in children's diet is said to improve memory.\n"
            "Constipation: 5 ml ghee in a cup of warm milk with sugar, at bedtime."
        ),
        "caution": None,
    },
    {
        "title": "Haldi (Turmeric) — for diabetes, acne, cold, wounds & skin allergy",
        "problem_tags": ["diabetes", "acne", "cold", "wounds_burns", "skin_allergy"],
        "ingredients": ["turmeric (Curcuma longa)"],
        "instructions": (
            "Diabetes: 10 ml fresh turmeric juice with 10 ml amla juice, twice daily.\n"
            "Acne: turmeric paste applied to the affected part twice a day. Turmeric with water, milk or cream on "
            "the face gives a glow and can help remove unwanted hair with regular use.\n"
            "Cold: 2 gm powder with warm milk and sugar, twice a day. A decoction of 1 gm turmeric powder, or "
            "turmeric in herbal tea, is said to help prevent allergic problems.\n"
            "Wound/Ulcer/Skin disease: wash with turmeric decoction and apply turmeric paste; paste mixed with "
            "ghee or coconut oil can be applied over the affected part.\n"
            "Skin allergy: 1-3 gm powder with jaggery, twice a day."
        ),
        "caution": None,
    },
    {
        "title": "Hing (Asafoetida) — for abdominal pain, toothache & appetite",
        "problem_tags": ["abdominal_pain", "toothache", "loss_of_appetite"],
        "ingredients": ["asafoetida / hing (Ferula narthex)"],
        "instructions": (
            "Using hing in the daily diet is good for digestion. Best used lightly fried in ghee.\n"
            "Abdominal pain: stirred and dissolved in water, applied on and around the navel — especially helpful "
            "for abdominal distention in children or infants. Also: 1 gm hing fried in ghee with buttermilk, "
            "twice a day.\n"
            "Toothache: a little fried hing kept in the carious tooth.\n"
            "Loss of appetite: a pinch of hing fried in ghee with a piece of crushed ginger, taken with buttermilk "
            "before food."
        ),
        "caution": None,
    },
    {
        "title": "Jayphal (Nutmeg) — for children's diarrhoea, irritability & pigmentation",
        "problem_tags": ["diarrhea", "irritability", "abdominal_pain"],
        "ingredients": ["nutmeg (Myristica fragrans)"],
        "instructions": (
            "Diarrhoea in children: a pinch of powder or fruit rubbed on a clean surface with milk or water, "
            "given 3-4 times a day.\n"
            "Irritability: if a child is restless and irritable, 1-2 pinches of powder with milk acts as a mild "
            "sedative; may be used 3-4 times a day.\n"
            "Black pigmentation: jayphal rubbed in milk and applied to pigmented areas, especially common around "
            "menopausal age.\n"
            "Abdominal pain (from diarrhoea): 2 gm powder with warm water, 4-5 times a day — reduces intestinal "
            "motility and so the pain."
        ),
        "caution": "Use only small pinches in children — nutmeg is sedative in larger amounts.",
    },
    {
        "title": "Jeera (Cumin) — for indigestion, acidity, skin & cold",
        "problem_tags": ["indigestion", "diarrhea", "acidity", "cold", "cough"],
        "ingredients": ["cumin seeds (Cuminum cyminum)"],
        "instructions": (
            "Indigestion: 3-6 gm powder of fried jeera and rock salt with warm water, thrice daily.\n"
            "Diarrhoea/Dysentery: 1-2 gm powder of fried jeera with 250 ml buttermilk, four times daily.\n"
            "Hyper-acidity: 5-10 gm ghee boiled with jeera, taken with rice during meals.\n"
            "Skin disease: 1-2 gm powder of fried jeera with milk, twice daily.\n"
            "Cold: warm decoction of 2 gm jeera, 5 gm dhania, 1 gm haldi, 1 gm methi powder and a little pepper, "
            "with honey/sugar and lemon, two to three times.\n"
            "Cough: the decoction above, or chewing a few grains frequently, helps dry and productive cough."
        ),
        "caution": None,
    },
    {
        "title": "Kalimirach (Black Pepper) — for cough, skin disease, indigestion & gums",
        "problem_tags": ["cough", "indigestion", "loss_of_appetite", "bleeding_gums", "bad_breath"],
        "ingredients": ["black pepper (Piper nigrum)"],
        "instructions": (
            "Cough: 1 gm powder of seeds with ghee and honey, twice daily.\n"
            "Skin diseases: a little powder with coconut oil, for local application.\n"
            "Hoarseness of voice: 1-2 gm powder of seed fried with ghee, twice daily, kept in the mouth.\n"
            "Hiccough: 1-2 gm powder of seeds with sugar, twice daily.\n"
            "Indigestion: a pinch of powder with a piece of crushed ginger and rock salt, before meals.\n"
            "Loss of appetite: a pinch of powder with 2 teaspoons of lemon juice in water, half an hour before food.\n"
            "Bleeding gums/tartar/bad breath: a pinch of powder mixed with honey, applied to gums after gargling "
            "with warm salt water, twice a day."
        ),
        "caution": None,
    },
    {
        "title": "Karela (Bitter Gourd) — for diabetes, indigestion, skin & appetite",
        "problem_tags": ["indigestion", "diabetes", "loss_of_appetite", "intestinal_worms", "acne"],
        "ingredients": ["bitter gourd (Momordica charantia)"],
        "instructions": (
            "Indigestion: 5-10 ml juice of fruit, twice daily.\n"
            "Diabetes: 1-3 gm powder of seeds with water, twice a day.\n"
            "Loss of appetite: 5-10 ml juice with buttermilk, 1-2 times.\n"
            "Skin diseases: 5-10 ml juice every morning on an empty stomach.\n"
            "Intestinal worms: 10 ml juice with jaggery in the morning, for 3 days.\n"
            "Acne: 5-10 ml juice on an empty stomach, once a day."
        ),
        "caution": None,
    },
    {
        "title": "Lahsun (Garlic) — for ear pain, flatulence, cold & joint pain",
        "problem_tags": ["ear_pain", "bloating", "cough", "cold", "joint_pain"],
        "ingredients": ["garlic (Allium sativum)"],
        "instructions": (
            "Ear pain: 2-4 drops of warm fresh juice instilled in the ear, twice a day; or a little paste boiled "
            "in coconut/mustard oil filled in the ear, 2-3 times a day.\n"
            "Flatulence: 6 ml juice with honey, twice a day.\n"
            "Cough/Cold: crushed bulb boiled in water, taken with sugar.\n"
            "Joint pain: 5 gm paste of bulb with honey or food, twice a day; warm paste mixed in any oil applied "
            "over the joint."
        ),
        "caution": "Do not use garlic juice/oil in the ear if there is any discharge.",
    },
    {
        "title": "Laung (Clove) — for cough, toothache, indigestion & bad breath",
        "problem_tags": ["cough", "cold", "hiccup", "indigestion", "toothache", "bad_breath", "ear_pain"],
        "ingredients": ["clove (Syzygium aromaticum)"],
        "instructions": (
            "Cough: chewed frequently, or 1 gm powder with honey 2-3 times in divided doses. Also: 20 ml warm "
            "decoction of 1 gm clove, 3-4 times daily — useful for both dry and productive cough.\n"
            "Cold/Hiccough: 1-2 gm powder with honey, in three divided doses.\n"
            "Indigestion: 1-2 gm powder with warm water.\n"
            "Toothache: a crushed clove kept in the carious tooth.\n"
            "Bad breath: a small piece chewed frequently.\n"
            "Ear pain: warm coconut oil boiled with clove powder, filled in the ear twice daily."
        ),
        "caution": "Do not use clove-infused oil in the ear if there is any discharge.",
    },
    {
        "title": "Madhu (Honey) — for cough, wounds, bleeding gums & weight",
        "problem_tags": ["loss_of_appetite", "cough", "wounds_burns", "bleeding_gums"],
        "ingredients": ["honey"],
        "instructions": (
            "Commonly prescribed in Ayurveda as a vehicle for medicine, especially in respiratory disorders.\n"
            "Obesity: one teaspoon with a glass of warm water in the morning.\n"
            "Loss of appetite: with a pinch of pepper powder, three to four times a day.\n"
            "Cough: with a pinch of clove (laung) powder, three to four times.\n"
            "Wounds/Ulcer/Burn: honey and ghee mixed and applied.\n"
            "Pyorrhoea (bleeding gums): apply a mixture of ginger, pepper, rock salt, honey & ghee to the gums, "
            "twice a day.\n"
            "Face pack: applying honey is said to give a glow to the skin."
        ),
        "caution": "Honey should not be boiled. Do not give honey to children under 1 year of age.",
    },
    {
        "title": "Methi (Fenugreek) — for diabetes, body ache, lactation & dandruff",
        "problem_tags": ["diabetes", "body_ache", "dandruff"],
        "ingredients": ["fenugreek (Trigonella foenum-graecum)"],
        "instructions": (
            "Diabetes: 2 gm powder with milk, twice daily.\n"
            "Body ache: 2 gm powder mixed with 2 gm jeera powder, with warm milk and sugar, twice daily.\n"
            "Lactation (to increase mother's milk): 5 gm powder with milk and sugar, in the morning.\n"
            "Dandruff: scalp massaged with paste mixed in water, half an hour before bath; coconut oil boiled "
            "with methi powder used regularly; methi paste also acts as a good hair conditioner."
        ),
        "caution": None,
    },
    {
        "title": "Nariyal (Coconut) — for acidity, kidney stones, hair & heatstroke",
        "problem_tags": ["acidity", "wounds_burns", "dehydration", "hair_fall", "sun_stroke"],
        "ingredients": ["coconut (Cocos nucifera) — tender coconut water and oil"],
        "instructions": (
            "Hyper-acidity: tender coconut water, twice daily.\n"
            "Kidney stone: tender coconut water, twice daily.\n"
            "Wounds/Ulcer/Burn: coconut oil applied frequently.\n"
            "Dehydration: tender coconut water, taken frequently.\n"
            "Hair fall: coconut oil processed with methi powder and amla powder, used regularly.\n"
            "Sun stroke: tender coconut water, taken frequently."
        ),
        "caution": None,
    },
    {
        "title": "Neem — for skin disease, wounds, worms & dandruff",
        "problem_tags": ["skin_allergy", "wounds_burns", "intestinal_worms", "loss_of_appetite", "dandruff"],
        "ingredients": ["neem leaves (Azadirachta indica)"],
        "instructions": (
            "Skin disease: 10 ml juice of leaves with honey, twice a day.\n"
            "Wounds/Ulcer: warm application of paste prepared from leaves, over the affected part.\n"
            "Intestinal worms: 20 ml decoction made from a handful of leaves, on an empty stomach for three days.\n"
            "Loss of appetite: 20 ml decoction made from a handful of leaves, on an empty stomach for three days.\n"
            "Dandruff/Ring worm: decoction made from a handful of leaves, applied to scalp one hour before bath."
        ),
        "caution": None,
    },
    {
        "title": "Nimbu (Lemon) — for indigestion, dehydration, gums & hair",
        "problem_tags": ["indigestion", "dehydration", "sun_stroke", "bleeding_gums", "loss_of_appetite", "hair_fall", "vomiting"],
        "ingredients": ["lemon (Citrus limon)"],
        "instructions": (
            "Indigestion: 5-10 ml juice with a pinch of salt and pepper, before food.\n"
            "Dehydration/Sun stroke: one lemon squeezed into a glass of water mixed with salt and sugar.\n"
            "Bleeding gums: the fruit skin crushed and rubbed gently to the gums, twice a day regularly.\n"
            "Loss of appetite: 5 ml juice with salt and a pinch of pepper, before meals.\n"
            "Hair fall: coconut oil processed with dried, powdered lemon skin.\n"
            "Vomiting: 5-10 ml juice mixed with water, sugar and a pinch of salt, frequently in small quantities."
        ),
        "caution": None,
    },
    {
        "title": "Pyaj (Onion) — for heatstroke, cold, cough & dysentery",
        "problem_tags": ["sun_stroke", "cold", "cough", "diarrhea"],
        "ingredients": ["onion (Allium cepa) — white variety preferred"],
        "instructions": (
            "Sun stroke: plenty of onion used for prevention of sun stroke.\n"
            "Cold/Cough: in children, decoction made from a piece of onion given with jaggery, thrice daily.\n"
            "Dysentery: white onion, chopped and fried in ghee, eaten with rice."
        ),
        "caution": None,
    },
    {
        "title": "Pippali (Long Pepper) — for indigestion, cold, cough & fever",
        "problem_tags": ["indigestion", "cold", "cough", "bleeding_gums", "diarrhea", "fever"],
        "ingredients": ["long pepper (Piper longum)"],
        "instructions": (
            "Indigestion: 2 gm powder with jaggery (guda), twice daily before meals.\n"
            "Cold/Cough: 2 gm powder with honey, thrice a day in divided doses. Also: 10-20 ml decoction with "
            "2-3 gm powder of pippali, ginger and black pepper with sugar or honey, 2-3 times a day.\n"
            "Pyorrhoea: decoction of pippali with honey & ghee, kept inside the mouth for a while in the "
            "morning and before bed.\n"
            "Diarrhoea: mix 2-3 gm powder in 1 litre buttermilk, divide into 4 parts, take 1 part every 6 hours.\n"
            "Cold with fever: 2 gm powder with honey, twice daily."
        ),
        "caution": None,
    },
    {
        "title": "Saunf (Fennel) — for indigestion, abdominal pain & appetite",
        "problem_tags": ["indigestion", "diarrhea", "abdominal_pain", "bad_breath", "loss_of_appetite"],
        "ingredients": ["fennel seeds (Foeniculum vulgare)"],
        "instructions": (
            "Indigestion: 3-5 gm powder with powder of fried jeera and rock salt, with warm water, thrice daily.\n"
            "Diarrhoea/Dysentery: 3-5 gm powder with buttermilk, 3-4 times daily.\n"
            "Abdominal pain: 3-5 gm powder with buttermilk, 3-4 times daily.\n"
            "Bad breath: a little quantity chewed after food.\n"
            "Loss of appetite: 3-5 gm powder of roasted saunf with buttermilk, a little pepper powder and salt, "
            "twice daily."
        ),
        "caution": None,
    },
    {
        "title": "Tulsi (Holy Basil) — for cough, cold, fever & skin allergy",
        "problem_tags": ["cough", "cold", "fever", "skin_allergy", "indigestion", "loss_of_appetite", "hair_fall", "wounds_burns", "ear_pain"],
        "ingredients": ["holy basil / tulsi leaves (Ocimum sanctum)"],
        "instructions": (
            "Cough/Cold: 5-10 ml juice, two or three times a day, with honey.\n"
            "Fever: 30 ml decoction from a handful of leaves and 5 gm dhania, thrice a day.\n"
            "Skin allergy: 5-10 ml juice, two or three times daily.\n"
            "Indigestion/Loss of appetite: 5-10 ml juice, two or three times daily.\n"
            "Greying of hair: coconut oil processed with tulsi juice, for regular use.\n"
            "Wound/Ulcer: juice mixed with honey and turmeric (haldi) powder, for application.\n"
            "Ear pain: 2-3 lukewarm drops, twice daily."
        ),
        "caution": "Do not use tulsi drops in the ear if there is any discharge.",
    },
]
