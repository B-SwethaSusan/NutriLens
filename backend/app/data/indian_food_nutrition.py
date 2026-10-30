"""Static nutrition reference table for the merged Indian-food classifier,
combining two Hugging Face datasets:

  - rajistics/indian_food_images            (20 classes)
  - SKSKCulinaryAI/Indian_Food_Images_Dataset (25 classes)

The two sources name some of the same dishes differently (e.g. "Chappati"
vs "chapati", "Kathi roll" vs "kaathi_rolls"). INDIAN_FOOD_CLASSES below is
the single merged, de-duplicated list every image ends up labeled with
regardless of which source it came from — see SOURCE_B_ALIASES in
backend/training/train_food_classifier.py for the exact name mapping.

"burger" and "pizza" (present in source A) were originally dropped from
this list as "not Indian". That was a mistake for a real app: a model that
has never seen a pizza still has to output SOMETHING when shown one, and
on held-out test images it confidently mislabelled pizza as chapati,
pav bhaji or dhokla, and burgers as kaathi rolls. Both are commonly eaten
in India, so they're now included (appended at the end so earlier class
indices are unchanged).

INDIAN_FOOD_CLASSES order MUST match the class-index order the training
script (backend/training/train_food_classifier.py --dataset indian) uses.
Changing this list requires retraining — the ONNX model's output indices
are positional, matching this exact order.

Values are APPROXIMATE, representative per-typical-serving figures (not a
per-dish lab measurement) intended for general educational estimates.
Swap in real IFCT 2017 (Indian Food Composition Tables) lookups for
production accuracy — this table exists so the feature works end-to-end
with zero external API calls.
"""

INDIAN_FOOD_CLASSES: list[str] = [
    "biryani", "butter_chicken", "butter_naan", "chai", "chapati", "chole_bhature", "dal_makhani", "dhokla",
    "fried_rice", "gajar_halwa", "ghevar", "gulab_jamun", "idli", "jalebi", "kaathi_rolls", "kadai_paneer",
    "kofta", "kulfi", "masala_bhindi", "masala_dosa", "meduvada", "momos", "paani_puri", "pakode",
    "pav_bhaji", "poori", "rasgulla", "samosa", "tandoori_chicken", "toor_dal", "vada_pav",
    "burger", "pizza",
]

# {class_name: {serving, calories_kcal, protein_g, carbs_g, fat_g}}
NUTRITION_TABLE: dict[str, dict] = {
    "biryani": {"serving": "1 plate (300g)", "calories_kcal": 450, "protein_g": 18, "carbs_g": 60, "fat_g": 15},
    "butter_chicken": {"serving": "1 bowl (200g)", "calories_kcal": 490, "protein_g": 27, "carbs_g": 10, "fat_g": 38},
    "butter_naan": {"serving": "1 piece (90g)", "calories_kcal": 310, "protein_g": 7, "carbs_g": 44, "fat_g": 12},
    "chai": {"serving": "1 cup (150ml)", "calories_kcal": 120, "protein_g": 3, "carbs_g": 18, "fat_g": 4},
    "chapati": {"serving": "1 piece (40g)", "calories_kcal": 104, "protein_g": 3, "carbs_g": 18, "fat_g": 2},
    "chole_bhature": {"serving": "1 plate (300g)", "calories_kcal": 650, "protein_g": 15, "carbs_g": 80, "fat_g": 28},
    "dal_makhani": {"serving": "1 bowl (200g)", "calories_kcal": 280, "protein_g": 10, "carbs_g": 25, "fat_g": 16},
    "dhokla": {"serving": "3 pieces (100g)", "calories_kcal": 160, "protein_g": 6, "carbs_g": 25, "fat_g": 4},
    "fried_rice": {"serving": "1 plate (250g)", "calories_kcal": 430, "protein_g": 10, "carbs_g": 65, "fat_g": 14},
    "gajar_halwa": {"serving": "1 bowl (100g)", "calories_kcal": 300, "protein_g": 5, "carbs_g": 30, "fat_g": 18},
    "ghevar": {"serving": "1 piece (80g)", "calories_kcal": 320, "protein_g": 4, "carbs_g": 40, "fat_g": 16},
    "gulab_jamun": {"serving": "2 pieces (80g)", "calories_kcal": 300, "protein_g": 4, "carbs_g": 40, "fat_g": 14},
    "idli": {"serving": "3 pieces (150g)", "calories_kcal": 170, "protein_g": 6, "carbs_g": 35, "fat_g": 1},
    "jalebi": {"serving": "100g", "calories_kcal": 350, "protein_g": 3, "carbs_g": 60, "fat_g": 12},
    "kaathi_rolls": {"serving": "1 roll (200g)", "calories_kcal": 450, "protein_g": 18, "carbs_g": 45, "fat_g": 22},
    "kadai_paneer": {"serving": "1 bowl (200g)", "calories_kcal": 380, "protein_g": 14, "carbs_g": 15, "fat_g": 30},
    "kofta": {"serving": "4 pieces with gravy (200g)", "calories_kcal": 350, "protein_g": 12, "carbs_g": 20, "fat_g": 25},
    "kulfi": {"serving": "1 piece (100g)", "calories_kcal": 200, "protein_g": 4, "carbs_g": 22, "fat_g": 11},
    "masala_bhindi": {"serving": "1 bowl (150g)", "calories_kcal": 160, "protein_g": 4, "carbs_g": 14, "fat_g": 10},
    "masala_dosa": {"serving": "1 piece (250g)", "calories_kcal": 370, "protein_g": 8, "carbs_g": 55, "fat_g": 13},
    "meduvada": {"serving": "2 pieces (100g)", "calories_kcal": 180, "protein_g": 6, "carbs_g": 22, "fat_g": 8},
    "momos": {"serving": "6 pieces (180g)", "calories_kcal": 250, "protein_g": 9, "carbs_g": 35, "fat_g": 8},
    "paani_puri": {"serving": "6 pieces (120g)", "calories_kcal": 180, "protein_g": 4, "carbs_g": 30, "fat_g": 5},
    "pakode": {"serving": "100g", "calories_kcal": 330, "protein_g": 8, "carbs_g": 28, "fat_g": 21},
    "pav_bhaji": {"serving": "1 plate (300g)", "calories_kcal": 450, "protein_g": 10, "carbs_g": 55, "fat_g": 20},
    "poori": {"serving": "2 pieces (60g)", "calories_kcal": 180, "protein_g": 3, "carbs_g": 20, "fat_g": 10},
    "rasgulla": {"serving": "2 pieces (80g)", "calories_kcal": 180, "protein_g": 4, "carbs_g": 35, "fat_g": 2},
    "samosa": {"serving": "1 piece (60g)", "calories_kcal": 260, "protein_g": 4, "carbs_g": 24, "fat_g": 17},
    "tandoori_chicken": {"serving": "2 pieces (200g)", "calories_kcal": 330, "protein_g": 40, "carbs_g": 4, "fat_g": 17},
    "toor_dal": {"serving": "1 bowl (200g)", "calories_kcal": 190, "protein_g": 10, "carbs_g": 28, "fat_g": 5},
    "vada_pav": {"serving": "1 piece (150g)", "calories_kcal": 290, "protein_g": 7, "carbs_g": 40, "fat_g": 11},
}


def get_nutrition(label: str) -> dict | None:
    return NUTRITION_TABLE.get(label)
