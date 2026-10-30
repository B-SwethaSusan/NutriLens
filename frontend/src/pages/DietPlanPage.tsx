import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import { AlertTriangle, FileText, Flame, Salad, Sparkles, Stethoscope } from 'lucide-react'
import { api, CONDITION_OPTIONS, type DietPlanResponse, type HealthProfile, type SymptomCheckResponse } from '../lib/api'
import { Badge, Button, Card, Input } from '../components/ui'
import { PageHeader } from '../components/Layout'

const defaults: HealthProfile = {
  age: 30, sex: 'male', height_cm: 170, weight_kg: 70, activity_level: 'moderate', goal: 'maintain',
  goal_rate_kg_per_week: 0, conditions: [], allergies: [], dietary_preferences: [], notes: '',
}

export function DietPlanPage() {
  const queryClient = useQueryClient()
  const profileQuery = useQuery({
    queryKey: ['health-profile'],
    queryFn: async () => { try { return (await api.get<HealthProfile>('/health-profile')).data } catch { return null } },
  })
  const [form, setForm] = useState<HealthProfile>(defaults)
  const [symptomText, setSymptomText] = useState('')
  const [symptomResult, setSymptomResult] = useState<SymptomCheckResponse | null>(null)
  const [plan, setPlan] = useState<DietPlanResponse | null>(null)
  const [allergyInput, setAllergyInput] = useState('')
  const [preferenceInput, setPreferenceInput] = useState('')

  useEffect(() => { if (profileQuery.data) setForm(profileQuery.data) }, [profileQuery.data])

  const saveProfile = useMutation({
    mutationFn: () => api.put<HealthProfile>('/health-profile', form),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['health-profile'] }),
  })
  const saveProfileError = (saveProfile.error as any)?.response?.data?.detail
    || (saveProfile.error ? 'Could not reach the server. Check that the backend is running.' : null)
  const checkSymptoms = useMutation({
    mutationFn: () => api.post<SymptomCheckResponse>('/symptom-check', { description: symptomText }),
    onSuccess: ({ data }) => setSymptomResult(data),
  })
  const generatePlan = useMutation({
    mutationFn: () => api.post<DietPlanResponse>('/diet-plan'),
    onSuccess: ({ data }) => setPlan(data),
  })

  function toggleCondition(condition: string) {
    setForm(prev => ({
      ...prev,
      conditions: prev.conditions.includes(condition) ? prev.conditions.filter(c => c !== condition) : [...prev.conditions, condition],
    }))
  }
  function addChip(list: 'allergies' | 'dietary_preferences', value: string, clear: () => void) {
    const trimmed = value.trim()
    if (!trimmed) return
    setForm(prev => ({ ...prev, [list]: [...prev[list], trimmed] }))
    clear()
  }
  function removeChip(list: 'allergies' | 'dietary_preferences', value: string) {
    setForm(prev => ({ ...prev, [list]: prev[list].filter(v => v !== value) }))
  }

  return <>
    <PageHeader eyebrow="Your dietitian" title="Diet Plan" description="Set up your health profile once, then generate a plan grounded in your uploaded nutrition guidelines." />
    <div className="grid gap-6 xl:grid-cols-[1.1fr_1fr]">
      <Card className="p-6 sm:p-8">
        <div className="mb-6 flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-sage-100 text-sage-700"><Salad size={19} /></div>
          <div><h2 className="font-bold">Health profile</h2><p className="text-xs text-ink/45">Used to compute your calorie and macro targets.</p></div>
        </div>

        <div className="grid gap-5 sm:grid-cols-2">
          <Field label="Age"><Input type="number" min={10} max={100} value={form.age} onChange={e => setForm({ ...form, age: Number(e.target.value) })} /></Field>
          <Field label="Sex">
            <select className="w-full rounded-xl border border-sage-200 bg-white px-3.5 py-2.5 text-sm outline-none ring-sage-300 focus:ring-2" value={form.sex} onChange={e => setForm({ ...form, sex: e.target.value as HealthProfile['sex'] })}>
              <option value="male">Male</option><option value="female">Female</option>
            </select>
          </Field>
          <Field label="Height (cm)"><Input type="number" min={100} max={250} value={form.height_cm} onChange={e => setForm({ ...form, height_cm: Number(e.target.value) })} /></Field>
          <Field label="Weight (kg)"><Input type="number" min={25} max={300} value={form.weight_kg} onChange={e => setForm({ ...form, weight_kg: Number(e.target.value) })} /></Field>
          <Field label="Activity level">
            <select className="w-full rounded-xl border border-sage-200 bg-white px-3.5 py-2.5 text-sm outline-none ring-sage-300 focus:ring-2" value={form.activity_level} onChange={e => setForm({ ...form, activity_level: e.target.value as HealthProfile['activity_level'] })}>
              <option value="sedentary">Sedentary</option><option value="light">Light</option><option value="moderate">Moderate</option><option value="active">Active</option><option value="very_active">Very active</option>
            </select>
          </Field>
          <Field label="Goal">
            <select className="w-full rounded-xl border border-sage-200 bg-white px-3.5 py-2.5 text-sm outline-none ring-sage-300 focus:ring-2" value={form.goal} onChange={e => setForm({ ...form, goal: e.target.value as HealthProfile['goal'] })}>
              <option value="lose">Lose weight</option><option value="maintain">Maintain</option><option value="gain">Gain weight</option>
            </select>
          </Field>
          {form.goal !== 'maintain' && <Field label="Target rate (kg/week)"><Input type="number" step="0.1" min={0} max={1.5} value={form.goal_rate_kg_per_week} onChange={e => setForm({ ...form, goal_rate_kg_per_week: Number(e.target.value) })} /></Field>}
        </div>

        <div className="mt-6">
          <span className="mb-2 block text-sm font-bold">Conditions</span>
          <div className="flex flex-wrap gap-2">
            {CONDITION_OPTIONS.map(condition => (
              <button key={condition} onClick={() => toggleCondition(condition)}
                className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${form.conditions.includes(condition) ? 'bg-sage-700 text-white' : 'bg-sage-50 text-ink/55 hover:bg-sage-100'}`}>
                {condition.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-6 rounded-xl border border-sage-100 bg-sage-50/60 p-4">
          <div className="mb-2 flex items-center gap-2 text-sm font-bold"><Stethoscope size={16} className="text-sage-700" />Not sure which condition applies?</div>
          <p className="mb-3 text-xs leading-5 text-ink/55">Describe your symptoms or diagnosis in plain words and we'll suggest conditions to add.</p>
          <div className="flex gap-2">
            <Input value={symptomText} onChange={e => setSymptomText(e.target.value)} placeholder="e.g. I was diagnosed with PCOS and want to lose weight" />
            <Button variant="secondary" onClick={() => checkSymptoms.mutate()} disabled={!symptomText.trim() || checkSymptoms.isPending}>{checkSymptoms.isPending ? 'Checking…' : 'Check'}</Button>
          </div>
          {symptomResult && <div className="mt-3 text-xs leading-5">
            <p className="text-ink/60">{symptomResult.rationale}</p>
            {symptomResult.detected_conditions.length > 0 && <div className="mt-2 flex flex-wrap gap-2">
              {symptomResult.detected_conditions.map(condition => (
                <button key={condition} onClick={() => !form.conditions.includes(condition) && toggleCondition(condition)}
                  className="rounded-full border border-sage-300 bg-white px-3 py-1 font-semibold text-sage-700 hover:bg-sage-50">
                  + {condition.replace('_', ' ')}
                </button>
              ))}
            </div>}
            <p className="mt-2 text-ink/40">{symptomResult.suggested_next_step}</p>
          </div>}
        </div>

        <div className="mt-6 grid gap-5 sm:grid-cols-2">
          <ChipField label="Allergies" chips={form.allergies} value={allergyInput} onChange={setAllergyInput}
            onAdd={() => addChip('allergies', allergyInput, () => setAllergyInput(''))} onRemove={v => removeChip('allergies', v)} />
          <ChipField label="Dietary preferences" chips={form.dietary_preferences} value={preferenceInput} onChange={setPreferenceInput}
            onAdd={() => addChip('dietary_preferences', preferenceInput, () => setPreferenceInput(''))} onRemove={v => removeChip('dietary_preferences', v)} />
        </div>

        <div className="mt-8 flex flex-wrap justify-end gap-3">
          <Button variant="secondary" onClick={() => saveProfile.mutate()} disabled={saveProfile.isPending}>{saveProfile.isPending ? 'Saving…' : saveProfile.isSuccess ? 'Saved ✓' : 'Save profile'}</Button>
          <Button onClick={() => generatePlan.mutate()} disabled={generatePlan.isPending}><Sparkles size={16} />{generatePlan.isPending ? 'Generating…' : 'Generate my diet plan'}</Button>
        </div>
        {saveProfileError && <p className="mt-3 text-right text-xs text-red-600">Couldn't save: {saveProfileError}</p>}
        {generatePlan.isError && <p className="mt-3 text-right text-xs text-red-600">Save your profile first, then generate a plan.</p>}
      </Card>

      <div className="space-y-6">
        {plan ? <>
          <Card className="p-6">
            <div className="mb-4 flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-xl bg-citrus/20 text-citrus"><Flame size={19} /></div><h2 className="font-bold">Daily targets</h2></div>
            <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-3">
              <Stat label="Calories" value={`${plan.targets.calories_kcal} kcal`} />
              <Stat label="Protein" value={`${plan.targets.protein_g} g`} />
              <Stat label="Carbs" value={`${plan.targets.carbs_g} g`} />
              <Stat label="Fat" value={`${plan.targets.fat_g} g`} />
              <Stat label="Fiber" value={`${plan.targets.fiber_g} g`} />
              <Stat label="BMR / TDEE" value={`${plan.bmr_kcal} / ${plan.tdee_kcal}`} />
            </div>
          </Card>

          <Card className="p-6">
            <h2 className="mb-4 font-bold">Meal timing</h2>
            <div className="space-y-2">
              {plan.meal_timing.map(meal => <div key={meal.meal} className="flex items-center justify-between rounded-xl bg-sage-50/60 px-4 py-3 text-sm">
                <div><p className="font-semibold">{meal.meal}</p><p className="text-xs text-ink/45">{meal.time_window}</p></div>
                <Badge tone="green">{meal.calories_kcal} kcal</Badge>
              </div>)}
            </div>
          </Card>

          {plan.condition_guidance.length > 0 && <Card className="p-6">
            <h2 className="mb-3 font-bold">Condition-specific guidance</h2>
            <ul className="space-y-2 text-sm leading-6 text-ink/65">{plan.condition_guidance.map((g, i) => <li key={i} className="flex gap-2"><span className="text-sage-600">•</span>{g}</li>)}</ul>
          </Card>}

          <Card className="p-6">
            <h2 className="mb-3 font-bold">Why this plan</h2>
            <div className="text-sm leading-7 text-ink/65">
              <ReactMarkdown
                components={{
                  h2: ({ children }) => <h3 className="mb-2 mt-5 text-xs font-bold uppercase tracking-wide text-sage-700 first:mt-0">{children}</h3>,
                  ul: ({ children }) => <ul className="space-y-1.5">{children}</ul>,
                  li: ({ children }) => <li className="flex gap-2"><span className="mt-1 text-sage-500">•</span><span>{children}</span></li>,
                  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                }}
              >
                {plan.explanation}
              </ReactMarkdown>
            </div>
            {plan.citations.length > 0 && <div className="mt-3 flex flex-wrap gap-2">
              {plan.citations.map((c, i) => <span key={i} className="inline-flex items-center gap-1 rounded-lg border border-sage-100 bg-white px-2 py-1 text-[11px] text-ink/55"><FileText size={12} className="text-sage-600" />{c.filename} · p. {c.page_number}</span>)}
            </div>}
            <div className="mt-4 flex items-start gap-2 rounded-xl bg-amber-50 p-3 text-xs leading-5 text-amber-800"><AlertTriangle size={14} className="mt-0.5 shrink-0" />{plan.disclaimer}</div>
          </Card>
        </> : <Card className="flex h-full flex-col items-center justify-center p-10 text-center">
          <div className="grid h-14 w-14 place-items-center rounded-2xl bg-sage-50 text-sage-600"><Salad size={24} /></div>
          <h3 className="mt-4 font-bold">Your plan will appear here</h3>
          <p className="mt-2 max-w-xs text-sm leading-6 text-ink/50">Fill in your profile and click "Generate my diet plan" to see your targets, meal timing, and grounded guidance.</p>
        </Card>}
      </div>
    </div>
  </>
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <label><span className="mb-2 block text-sm font-bold">{label}</span>{children}</label>
}
function Stat({ label, value }: { label: string; value: string }) {
  return <div className="rounded-xl bg-sage-50/60 p-3"><p className="text-[11px] font-semibold text-ink/45">{label}</p><p className="mt-1 font-bold">{value}</p></div>
}
function ChipField({ label, chips, value, onChange, onAdd, onRemove }: { label: string; chips: string[]; value: string; onChange: (v: string) => void; onAdd: () => void; onRemove: (v: string) => void }) {
  return <label>
    <span className="mb-2 block text-sm font-bold">{label}</span>
    <div className="flex gap-2"><Input value={value} onChange={e => onChange(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); onAdd() } }} placeholder="Type and press Enter" />
      <Button variant="secondary" onClick={onAdd} type="button">Add</Button></div>
    {chips.length > 0 && <div className="mt-2 flex flex-wrap gap-2">{chips.map(chip => <span key={chip} onClick={() => onRemove(chip)} className="cursor-pointer rounded-full bg-sage-100 px-3 py-1 text-xs font-semibold text-sage-700 hover:bg-sage-200">{chip} ×</span>)}</div>}
  </label>
}
