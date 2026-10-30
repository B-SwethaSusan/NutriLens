import type { NutritionPer100g } from './api'

export type ScaledNutrition = {
  calories_kcal: number
  protein_g: number
  carbs_g: number
  fat_g: number
  fibre_g: number | null
  sugar_g: number | null
}

/** nutrient for a portion = nutrient per 100 g × grams / 100.
 *  Calories are whole numbers; grams of nutrients keep one decimal. Unknown
 *  values (null) stay null, so the UI shows "—" instead of a made-up number. */
export function scaleNutrition(per100g: NutritionPer100g, grams: number): ScaledNutrition {
  const factor = Math.max(0, grams) / 100
  const g = (v: number | null) => (v === null ? null : Math.round(v * factor * 10) / 10)
  return {
    calories_kcal: Math.round(per100g.calories_kcal * factor),
    protein_g: g(per100g.protein_g) as number,
    carbs_g: g(per100g.carbs_g) as number,
    fat_g: g(per100g.fat_g) as number,
    fibre_g: g(per100g.fibre_g),
    sugar_g: g(per100g.sugar_g),
  }
}

/** Share of calories from protein, carbs and fat (4/4/9 kcal per gram).
 *  Independent of portion size. Percentages sum to 100. */
export function macroEnergySplit(per100g: NutritionPer100g): { protein: number; carbs: number; fat: number } {
  const p = per100g.protein_g * 4
  const c = per100g.carbs_g * 4
  const f = per100g.fat_g * 9
  const total = p + c + f
  if (total <= 0) return { protein: 0, carbs: 0, fat: 0 }
  const protein = Math.round((p / total) * 100)
  const carbs = Math.round((c / total) * 100)
  return { protein, carbs, fat: 100 - protein - carbs }
}
