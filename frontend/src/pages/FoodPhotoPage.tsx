import { useMemo, useRef, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { AlertTriangle, Database, ImageUp, Info, Leaf, Search, UploadCloud, Utensils } from 'lucide-react'
import { api, type FoodDish, type FoodDishListItem, type FoodPhotoResponse, type ServingUnit } from '../lib/api'
import { macroEnergySplit, scaleNutrition } from '../lib/nutrition'
import { Badge, Button, Card, Input } from '../components/ui'
import { PageHeader } from '../components/Layout'

const ACCEPTED = ['image/jpeg', 'image/png', 'image/webp']
const MAX_BYTES = 10 * 1024 * 1024
const GRAM_PRESETS = [50, 100, 150, 200, 250]

// Never display 100% — no photo classifier is certain. Tiny values read as "<1%".
export const pct = (c: number) => (c < 0.005 ? '<1%' : `${Math.min(99, Math.round(c * 100))}%`)

type View = { kind: 'photo'; data: FoodPhotoResponse; chosen: string | null } | { kind: 'manual'; label: string }

export function FoodPhotoPage() {
  const [preview, setPreview] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [view, setView] = useState<View | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)
  const resultRef = useRef<HTMLDivElement>(null)
  // On phones the result card sits below the upload + search cards; bring it into view.
  const showResult = () => setTimeout(() => {
    if (window.innerWidth < 1280) resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, 50)

  const dishes = useQuery({
    queryKey: ['food-dishes'],
    queryFn: async () => (await api.get<FoodDishListItem[]>('/food-photo/dishes')).data,
    staleTime: 5 * 60_000,
  })

  const analyze = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return (await api.post<FoodPhotoResponse>('/food-photo', formData, { headers: { 'Content-Type': 'multipart/form-data' } })).data
    },
    onSuccess: data => { setView({ kind: 'photo', data, chosen: null }); showResult() },
    onError: showResult,
  })

  function handleFile(file: File | undefined) {
    if (!file) return
    setUploadError(null)
    if (!ACCEPTED.includes(file.type)) return setUploadError('Please choose a JPEG, PNG or WEBP photo.')
    if (file.size > MAX_BYTES) return setUploadError('That photo is larger than 10 MB. Please choose a smaller one.')
    if (preview) URL.revokeObjectURL(preview)
    setPreview(URL.createObjectURL(file))
    analyze.mutate(file)
  }

  const dishByLabel = useMemo(() => Object.fromEntries((dishes.data ?? []).map(d => [d.label, d as FoodDish])), [dishes.data])

  return <>
    <PageHeader eyebrow="Snap & Food Search" title="Food Photo" description="Upload a photo of a dish to identify it and see its nutrition for a single serving." />
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
      <div className="min-w-0 space-y-6">
        <Card className="flex flex-col items-center p-6 text-center sm:p-8">
          {preview
            ? <img src={preview} alt="Your uploaded food" className="mb-5 max-h-72 w-full rounded-xl object-cover" />
            : <div className="mb-5 grid h-16 w-16 place-items-center rounded-3xl bg-sage-100 text-sage-700"><ImageUp size={28} /></div>}
          <input ref={fileRef} type="file" accept={ACCEPTED.join(',')} className="hidden" onChange={e => { handleFile(e.target.files?.[0]); e.target.value = '' }} />
          <Button onClick={() => fileRef.current?.click()} disabled={analyze.isPending}>
            <UploadCloud size={17} />{analyze.isPending ? 'Analysing…' : preview ? 'Upload another photo' : 'Upload a food photo'}
          </Button>
          <p className="mt-3 max-w-xs text-xs leading-5 text-ink/45">JPEG, PNG or WEBP, up to 10 MB. One dish per photo, clearly visible and well lit, works best.</p>
          {uploadError && <p className="mt-3 text-xs font-semibold text-red-600">{uploadError}</p>}
        </Card>
        <DishSearch dishes={dishes.data ?? []} loading={dishes.isLoading} onPick={label => { setView({ kind: 'manual', label }); showResult() }} />
      </div>

      <div ref={resultRef} className="min-w-0 scroll-mt-4"><Card className="p-5 sm:p-7">
        {analyze.isPending ? <Loading />
          : analyze.isError ? <ErrorNote error={analyze.error} />
          : view?.kind === 'photo' ? <PhotoResult view={view} onChoose={label => setView({ ...view, chosen: label })} />
          : view?.kind === 'manual' && dishByLabel[view.label] ? <ManualResult dish={dishByLabel[view.label]} />
          : <EmptyState />}
      </Card></div>
    </div>
  </>
}

function PhotoResult({ view, onChoose }: { view: Extract<View, { kind: 'photo' }>; onChoose: (label: string) => void }) {
  const { data, chosen } = view
  const top = data.top_prediction
  const candidates = [top, ...data.alternatives]
  const shownLabel = chosen ?? (data.status === 'recognized' ? top.label : null)
  const shownDish = shownLabel ? data.dishes[shownLabel] : null

  return <div>
    {data.status === 'uncertain' && !chosen ? <div className="mb-5 rounded-xl bg-amber-50 p-4 text-sm leading-6 text-amber-900">
      <p className="flex items-center gap-2 font-bold"><AlertTriangle size={16} />We couldn't identify this dish confidently</p>
      <p className="mt-1 text-amber-800">It may be a dish the model hasn't learned yet, or the photo may be unclear. If it's one of these, tap it, or search for it on the left.</p>
    </div> : <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
      <div className="min-w-0">
        <p className="text-xs font-semibold text-ink/45">{chosen ? 'You selected' : 'Identified dish'}</p>
        <h2 className="text-2xl font-bold">{candidates.find(c => c.label === shownLabel)?.name}</h2>
      </div>
      {!chosen && <ConfidenceBadge level={data.confidence_level} confidence={top.confidence} />}
    </div>}

    <div className="mb-6">
      <p className="mb-2 text-xs font-semibold text-ink/45">{data.status === 'uncertain' && !chosen ? 'Closest matches' : 'Not right? It might be:'}</p>
      <div className="flex flex-wrap gap-2">
        {candidates.filter(c => c.label !== shownLabel).map(c => (
          <button key={c.label} onClick={() => onChoose(c.label)} className="rounded-full border border-sage-200 bg-white px-3 py-1.5 text-xs font-semibold text-ink/70 hover:bg-sage-50">
            {c.name} · {pct(c.confidence)}
          </button>
        ))}
      </div>
    </div>

    {shownDish && <DishDetail key={shownLabel} dish={shownDish} />}
    <p className="mt-6 flex items-start gap-2 text-xs leading-5 text-ink/45"><Info size={13} className="mt-0.5 shrink-0" />
      Confidence is {data.model_info.calibrated ? 'calibrated on photos the model never trained on' : 'the model’s raw score (not yet calibrated)'}
      {data.model_info.heldout_top1_accuracy ? ` · model accuracy on held-out photos: ${Math.round(data.model_info.heldout_top1_accuracy * 100)}%` : ''}. {data.note}
    </p>
  </div>
}

function ManualResult({ dish }: { dish: FoodDish }) {
  return <div>
    <p className="text-xs font-semibold text-ink/45">Looked up from the dish list</p>
    <h2 className="mb-4 text-2xl font-bold">{dish.name}</h2>
    <DishDetail dish={dish} />
  </div>
}

function ConfidenceBadge({ level, confidence }: { level: FoodPhotoResponse['confidence_level']; confidence: number }) {
  const tone = level === 'high' ? 'green' : level === 'medium' ? 'amber' : 'red'
  const text = level === 'high' ? 'High confidence' : level === 'medium' ? 'Medium confidence' : 'Low confidence'
  return <div className="text-right"><Badge tone={tone}>{text} · {pct(confidence)}</Badge></div>
}

function DishDetail({ dish }: { dish: FoodDish }) {
  const options = useMemo(() => {
    const all: ServingUnit[] = [dish.default_serving, ...dish.units, ...GRAM_PRESETS.map(g => ({ label: `${g} g`, grams: g }))]
    return all.filter((o, i) => all.findIndex(x => x.label === o.label) === i)
  }, [dish])
  const [selected, setSelected] = useState(0)
  const [custom, setCustom] = useState('')
  const customGrams = Number(custom)
  const usingCustom = custom !== '' && customGrams > 0
  const grams = usingCustom ? Math.min(customGrams, 2000) : options[selected].grams
  const portionLabel = usingCustom ? `${grams} g (custom)` : `${options[selected].label}${options[selected].label.endsWith(' g') ? '' : ` ≈ ${options[selected].grams} g`}`

  return <div className="space-y-5">
    <div className="flex flex-wrap gap-2">
      <DietBadge diet={dish.diet} />
      <Badge>{dish.region}</Badge>
      <Badge>{dish.category}</Badge>
    </div>
    <p className="text-sm leading-6 text-ink/70">{dish.description}</p>
    <div className="grid gap-4 sm:grid-cols-2">
      <div><p className="mb-1.5 text-xs font-semibold text-ink/45">Main ingredients</p><p className="text-sm leading-6 text-ink/70">{dish.ingredients.join(', ')}</p></div>
      <div><p className="mb-1.5 text-xs font-semibold text-ink/45">Food groups</p>
        <div className="flex flex-wrap gap-1.5">{dish.food_groups.map(g => <span key={g} className="rounded-full bg-sage-50 px-2.5 py-1 text-[11px] font-semibold text-sage-700">{g}</span>)}</div></div>
    </div>

    <div className="rounded-2xl border border-sage-100 bg-sage-50/50 p-4">
      <p className="mb-2 text-sm font-bold">Serving size</p>
      <div className="flex flex-wrap gap-2">
        {options.map((o, i) => (
          <button key={o.label} onClick={() => { setSelected(i); setCustom('') }}
            className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${!usingCustom && selected === i ? 'bg-sage-700 text-white' : 'bg-white text-ink/60 hover:bg-sage-100'}`}>
            {o.label}{i === 0 ? ' (reference)' : ''}
          </button>
        ))}
        <label className="flex items-center gap-1.5 text-xs font-semibold text-ink/55">
          <Input type="number" min={1} max={2000} inputMode="numeric" value={custom} onChange={e => setCustom(e.target.value)} placeholder="Custom" className="h-8 w-24 px-2.5 py-1 text-xs" />g
        </label>
      </div>
      <p className="mt-2 text-xs text-ink/45">Showing nutrition for: <span className="font-semibold text-ink/70">{portionLabel}</span></p>
    </div>

    {dish.per_100g ? <NutritionPanel dish={dish} grams={grams} /> : <div className="flex items-start gap-2 rounded-xl bg-amber-50 p-4 text-sm leading-6 text-amber-900">
      <AlertTriangle size={16} className="mt-1 shrink-0" />No reliable nutrition data is available for this dish yet. We'd rather show nothing than a made-up number.
    </div>}

    <SourceBox dish={dish} />
  </div>
}

function NutritionPanel({ dish, grams }: { dish: FoodDish; grams: number }) {
  const per100 = dish.per_100g!
  const n = scaleNutrition(per100, grams)
  const split = macroEnergySplit(per100)
  const fmt = (v: number | null, unit: string) => (v === null ? '—' : `${v} ${unit}`)
  return <div>
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      <Stat label="Calories" value={`${n.calories_kcal} kcal`} highlight />
      <Stat label="Protein" value={fmt(n.protein_g, 'g')} />
      <Stat label="Carbohydrates" value={fmt(n.carbs_g, 'g')} />
      <Stat label="Fat" value={fmt(n.fat_g, 'g')} />
      <Stat label="Fibre" value={fmt(n.fibre_g, 'g')} />
      <Stat label="Sugar" value={fmt(n.sugar_g, 'g')} />
    </div>
    <div className="mt-4">
      <p className="mb-1.5 text-xs font-semibold text-ink/45">Where the calories come from</p>
      <div className="flex h-3 overflow-hidden rounded-full bg-sage-50" role="img" aria-label={`Protein ${split.protein}%, carbohydrates ${split.carbs}%, fat ${split.fat}%`}>
        <div className="bg-sage-600" style={{ width: `${split.protein}%` }} />
        <div className="bg-citrus" style={{ width: `${split.carbs}%` }} />
        <div className="bg-rose-400" style={{ width: `${split.fat}%` }} />
      </div>
      <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1 text-[11px] font-semibold text-ink/55">
        <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-sage-600" />Protein {split.protein}%</span>
        <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-citrus" />Carbs {split.carbs}%</span>
        <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-rose-400" />Fat {split.fat}%</span>
      </div>
    </div>
    <p className="mt-3 text-[11px] text-ink/40">Per 100 g: {per100.calories_kcal} kcal · protein {per100.protein_g} g · carbs {per100.carbs_g} g · fat {per100.fat_g} g</p>
  </div>
}

function SourceBox({ dish }: { dish: FoodDish }) {
  const rel = {
    high: { tone: 'green' as const, text: 'High reliability', desc: 'Same dish in the Indian Nutrient Databank (based on ICMR-NIN food composition tables).' },
    medium: { tone: 'amber' as const, text: 'Medium reliability', desc: 'Closest matching recipe in the Indian Nutrient Databank.' },
    low: { tone: 'red' as const, text: 'Rough estimate', desc: 'No verified databank value for this dish. Treat these numbers as approximate.' },
    unavailable: { tone: 'neutral' as const, text: 'No data', desc: '' },
  }[dish.reliability]
  return <div className="rounded-xl border border-sage-100 p-4 text-xs leading-5 text-ink/60">
    <div className="mb-1.5 flex flex-wrap items-center gap-2"><Database size={13} className="text-sage-600" /><span className="font-bold text-ink/75">Nutrition source</span><Badge tone={rel.tone}>{rel.text}</Badge></div>
    <p>{dish.source.name}{dish.source.code ? ` · recipe ${dish.source.code}: “${dish.source.recipe}”` : ''}</p>
    {rel.desc && <p className="mt-1">{rel.desc}</p>}
    {dish.reliability_note && <p className="mt-1">{dish.reliability_note}</p>}
    <p className="mt-1 text-ink/45">Home recipes vary (oil, ghee, portion), so actual values can differ. This is general information, not a personal dietary prescription.</p>
  </div>
}

function DishSearch({ dishes, loading, onPick }: { dishes: FoodDishListItem[]; loading: boolean; onPick: (label: string) => void }) {
  const [query, setQuery] = useState('')
  const [diet, setDiet] = useState<'all' | 'veg' | 'non-veg'>('all')
  const [region, setRegion] = useState('All')
  const regions = ['All', 'North', 'South', 'East', 'West', 'Other']
  const results = useMemo(() => {
    const q = query.trim().toLowerCase()
    return dishes.filter(d => {
      const haystack = [d.name, d.label.replace(/_/g, ' '), d.region, d.category, ...d.ingredients].join(' ').toLowerCase()
      if (q && !q.split(/\s+/).every(word => haystack.includes(word))) return false
      if (diet !== 'all' && d.diet !== diet) return false
      if (region !== 'All') {
        const named = ['North', 'South', 'East', 'West'].some(r => d.region.includes(`${r} Indian`))
        if (region === 'Other' ? named : !d.region.includes(`${region} Indian`)) return false
      }
      return true
    })
  }, [dishes, query, diet, region])

  return <Card className="p-5 sm:p-6">
    <div className="mb-3 flex items-center gap-2"><Search size={16} className="text-sage-700" /><h2 className="font-bold">Search dishes</h2></div>
    <p className="mb-3 text-xs leading-5 text-ink/50">The {dishes.length || ''} dishes the model can recognise. Search by name, region or ingredient, and tap one to see its nutrition.</p>
    <Input value={query} onChange={e => setQuery(e.target.value)} placeholder="e.g. dosa, paneer, Mumbai, chickpeas" />
    <div className="mt-3 flex flex-wrap gap-1.5">
      {(['all', 'veg', 'non-veg'] as const).map(d => <Chip key={d} active={diet === d} onClick={() => setDiet(d)}>{d === 'all' ? 'All' : d === 'veg' ? 'Veg' : 'Non-veg'}</Chip>)}
      <span className="mx-1 w-px bg-sage-100" />
      {regions.map(r => <Chip key={r} active={region === r} onClick={() => setRegion(r)}>{r}</Chip>)}
    </div>
    <div className="mt-3 max-h-80 space-y-1 overflow-y-auto pr-1">
      {loading ? <p className="py-4 text-center text-xs text-ink/45">Loading dishes…</p>
        : results.length === 0 ? <p className="py-4 text-center text-xs text-ink/45">No matching dishes. Try another word or clear the filters.</p>
        : results.map(d => (
          <button key={d.label} onClick={() => onPick(d.label)} className="flex w-full items-center justify-between gap-3 rounded-xl px-3 py-2 text-left hover:bg-sage-50">
            <span className="min-w-0"><span className="block truncate text-sm font-semibold">{d.name}</span><span className="block truncate text-[11px] text-ink/45">{d.region} · {d.category}</span></span>
            <span className="flex shrink-0 items-center gap-2 text-[11px] text-ink/50"><DietDot diet={d.diet} />{d.per_100g ? `${Math.round(d.per_100g.calories_kcal)} kcal/100 g` : 'no data'}</span>
          </button>
        ))}
    </div>
  </Card>
}

function Chip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return <button onClick={onClick} className={`rounded-full px-2.5 py-1 text-[11px] font-semibold transition ${active ? 'bg-sage-700 text-white' : 'bg-sage-50 text-ink/55 hover:bg-sage-100'}`}>{children}</button>
}
function DietDot({ diet }: { diet: FoodDish['diet'] }) {
  const color = diet === 'veg' ? 'border-emerald-600 bg-emerald-600' : diet === 'non-veg' ? 'border-red-600 bg-red-600' : 'border-ink/30 bg-white'
  return <span title={diet} className={`inline-block h-2.5 w-2.5 rounded-sm border ${color}`} />
}
function DietBadge({ diet }: { diet: FoodDish['diet'] }) {
  if (diet === 'veg') return <Badge tone="green"><span className="flex items-center gap-1"><Leaf size={11} />Vegetarian</span></Badge>
  if (diet === 'non-veg') return <Badge tone="red">Non-vegetarian</Badge>
  return <Badge>Veg or non-veg (varies)</Badge>
}
function Stat({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return <div className={`rounded-xl p-3 ${highlight ? 'bg-sage-700 text-white' : 'bg-sage-50/70'}`}>
    <p className={`text-[11px] font-semibold ${highlight ? 'text-white/70' : 'text-ink/45'}`}>{label}</p>
    <p className="mt-1 text-lg font-bold">{value}</p>
  </div>
}
function Loading() {
  return <div className="flex h-full flex-col items-center justify-center py-16 text-center">
    <div className="h-10 w-10 animate-spin rounded-full border-4 border-sage-100 border-t-sage-600" />
    <p className="mt-4 text-sm font-semibold text-ink/60">Identifying your dish…</p>
  </div>
}
function EmptyState() {
  return <div className="flex h-full flex-col items-center justify-center py-12 text-center">
    <div className="grid h-14 w-14 place-items-center rounded-2xl bg-sage-50 text-sage-600"><Utensils size={24} /></div>
    <h3 className="mt-4 font-bold">Your dish details will appear here</h3>
    <p className="mt-2 max-w-xs text-sm leading-6 text-ink/50">Upload a photo, or pick a dish from the search list, to see what it is and its nutrition per serving.</p>
  </div>
}
function ErrorNote({ error }: { error: unknown }) {
  const status = (error as any)?.response?.status
  const detail = (error as any)?.response?.data?.detail
  const title = status === 503 ? 'Food recognition is not available right now' : status === 400 || status === 413 || status === 415 ? 'We couldn’t use that photo' : 'Something went wrong'
  const message = detail || (status ? 'Please try again.' : 'Could not reach the server. Check your connection and try again.')
  return <div className="flex h-full flex-col items-center justify-center py-12 text-center">
    <div className="grid h-14 w-14 place-items-center rounded-2xl bg-amber-50 text-amber-700"><AlertTriangle size={24} /></div>
    <h3 className="mt-4 font-bold">{title}</h3>
    <p className="mt-2 max-w-sm text-sm leading-6 text-ink/50">{message}</p>
  </div>
}
