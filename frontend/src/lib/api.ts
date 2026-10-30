import axios from 'axios'

export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || '/api' })
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('nutrilens_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('nutrilens_token')
    }
    return Promise.reject(error)
  },
)

export type User = { id: string; email: string; full_name?: string | null; created_at: string }
export type Document = { id: string; filename: string; source?: string | null; author?: string | null; page_count: number; chunk_count: number; file_size: number; status: string; error_message?: string | null; created_at: string; updated_at?: string | null }
export type Citation = { filename: string; page_number: number; chunk_number: number; similarity: number }
export type ChatResponse = { conversation_id: string; answer: string; citations: Citation[] }
export type Conversation = { id: string; title: string; created_at: string; updated_at?: string | null; messages: { id: string; role: string; content: string; citations?: Citation[] | null; created_at: string }[] }
export type Settings = { chunk_size: number; chunk_overlap: number; top_k: number; temperature: number; llm_model?: string | null; embedding_model: string }

export async function authRequest(path: '/signup' | '/login', payload: object) {
  const { data } = await api.post<{ access_token: string; user: User }>(`/auth${path}`, payload)
  localStorage.setItem('nutrilens_token', data.access_token)
  return data
}

// --- Health profile / diet plan / symptom checker / progress / food photo ---

export type ActivityLevel = 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active'
export type Goal = 'lose' | 'gain' | 'maintain'

export type HealthProfile = {
  id?: string
  age: number
  sex: 'male' | 'female'
  height_cm: number
  weight_kg: number
  activity_level: ActivityLevel
  goal: Goal
  goal_rate_kg_per_week: number
  conditions: string[]
  allergies: string[]
  dietary_preferences: string[]
  notes?: string | null
}

export const CONDITION_OPTIONS = ['diabetes', 'hypertension', 'pcos', 'thyroid', 'ckd', 'gi_issues'] as const

export type MacroTargets = { calories_kcal: number; protein_g: number; carbs_g: number; fat_g: number; fiber_g: number }
export type MealTiming = { meal: string; time_window: string; calories_kcal: number; guidance: string }
export type DietPlanResponse = {
  bmr_kcal: number
  tdee_kcal: number
  targets: MacroTargets
  meal_timing: MealTiming[]
  condition_guidance: string[]
  explanation: string
  citations: Citation[]
  disclaimer: string
}

export type SymptomCheckResponse = {
  detected_conditions: string[]
  confidence: 'low' | 'medium' | 'high'
  rationale: string
  suggested_next_step: string
}

export type ProgressLog = { id: string; log_date: string; weight_kg?: number | null; waist_cm?: number | null; adherence_pct?: number | null; note?: string | null; created_at: string }
export type ProgressTrend = { slope_kg_per_week: number; projected_weight_kg: number; projected_date?: string | null; on_track?: boolean | null; message: string }
export type ProgressSummary = { logs: ProgressLog[]; trend: ProgressTrend | null }

export type NutritionPer100g = { calories_kcal: number; protein_g: number; carbs_g: number; fat_g: number; fibre_g: number | null; sugar_g: number | null }
export type ServingUnit = { label: string; grams: number }
export type FoodDish = {
  name: string
  region: string
  category: string
  diet: 'veg' | 'non-veg' | 'varies'
  description: string
  ingredients: string[]
  food_groups: string[]
  per_100g: NutritionPer100g | null
  default_serving: ServingUnit
  units: ServingUnit[]
  source: { name: string; code: string | null; recipe: string | null }
  reliability: 'high' | 'medium' | 'low' | 'unavailable'
  reliability_note: string | null
}
export type FoodDishListItem = FoodDish & { label: string }
export type FoodPrediction = { label: string; name: string; confidence: number }
export type FoodPhotoResponse = {
  status: 'recognized' | 'uncertain'
  confidence_level: 'high' | 'medium' | 'low'
  top_prediction: FoodPrediction
  alternatives: FoodPrediction[]
  dishes: Record<string, FoodDish>
  model_info: { calibrated: boolean; num_classes: number; reject_below: number; high_at: number; heldout_top1_accuracy: number | null }
  note: string
}

export type HomeRemedy = {
  id: string
  title: string
  problem_tags: string[]
  ingredients: string[]
  instructions: string
  caution?: string | null
  language: string
  source: 'curated' | 'community'
  upvotes: number
  created_at: string
}
export type HomeRemedyDraft = { title: string; problem_tags: string[]; ingredients: string[]; instructions: string; caution?: string; language: string }
export type ModerationResult = { allowed: boolean; abusive: boolean; off_topic: boolean; detected_language: string; reason: string }
export type HomeRemedySubmitResponse = { remedy: HomeRemedy | null; moderation: ModerationResult }

export const REMEDY_PROBLEM_TAGS = [
  'cold', 'cough', 'sore_throat', 'indigestion', 'acidity', 'bloating', 'headache', 'nausea',
  'constipation', 'menstrual_cramps', 'insomnia', 'minor_burns', 'toothache', 'mouth_ulcers',
  'dry_skin', 'blocked_nose', 'body_ache', 'stress', 'fever', 'diabetes', 'acne', 'hair_fall',
  'dandruff', 'bad_breath', 'abdominal_pain', 'bleeding_gums', 'ear_pain', 'joint_pain',
  'diarrhea', 'vomiting', 'piles', 'wounds_burns', 'skin_allergy', 'loss_of_appetite',
  'eye_strain', 'immunity', 'hair_lice', 'nosebleed', 'hangover', 'fatigue',
  'weight_management', 'high_blood_pressure', 'high_cholesterol', 'anemia', 'eczema',
  'pimples', 'varicose_veins', 'brittle_nails', 'oral_thrush', 'gum_disease', 'cold_sores',
  'insect_bites', 'scars', 'puffy_eyes', 'pms', 'lactation', 'teething', 'postpartum_care',
  'snoring', 'diaper_rash', 'colic', 'cradle_cap', 'chickenpox', 'exam_stress',
  'growing_pains', 'dengue', 'conjunctivitis', 'heat_rash', 'migraine', 'uti', 'stye',
  'food_poisoning', 'back_pain', 'low_blood_pressure', 'ringworm', 'athletes_foot',
  'body_odor', 'vertigo', 'tonsillitis', 'premature_greying', 'frozen_shoulder', 'sciatica',
  'chilblains',
] as const
