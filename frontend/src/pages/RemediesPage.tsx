import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AlertTriangle, ChefHat, Search, ShieldAlert, ThumbsUp, Upload } from 'lucide-react'
import { api, REMEDY_PROBLEM_TAGS, type HomeRemedy, type HomeRemedySubmitResponse } from '../lib/api'
import { Badge, Button, Card, Input } from '../components/ui'
import { PageHeader } from '../components/Layout'

const emptyDraft = { title: '', ingredients: [] as string[], instructions: '', caution: '', problem_tags: [] as string[], language: 'en' }

export function RemediesPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [activeTag, setActiveTag] = useState<string | null>(null)
  const [draft, setDraft] = useState(emptyDraft)
  const [ingredientInput, setIngredientInput] = useState('')
  const [submitResult, setSubmitResult] = useState<HomeRemedySubmitResponse | null>(null)

  const remedies = useQuery({
    queryKey: ['remedies', search, activeTag],
    queryFn: async () => (await api.get<HomeRemedy[]>('/remedies', { params: { query: search || undefined, tag: activeTag || undefined } })).data,
  })

  const submit = useMutation({
    mutationFn: () => api.post<HomeRemedySubmitResponse>('/remedies', draft),
    onSuccess: ({ data }) => {
      setSubmitResult(data)
      if (data.remedy) {
        setDraft(emptyDraft)
        queryClient.invalidateQueries({ queryKey: ['remedies'] })
      }
    },
    onError: (err: any) => setSubmitResult({ remedy: null, moderation: { allowed: false, abusive: false, off_topic: false, detected_language: 'unknown', reason: err.response?.data?.detail || 'Something went wrong.' } }),
  })

  const upvote = useMutation({
    mutationFn: (id: string) => api.post(`/remedies/${id}/upvote`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['remedies'] }),
  })

  function addIngredient() {
    const trimmed = ingredientInput.trim()
    if (!trimmed) return
    setDraft(d => ({ ...d, ingredients: [...d.ingredients, trimmed] }))
    setIngredientInput('')
  }
  function toggleDraftTag(tag: string) {
    setDraft(d => ({ ...d, problem_tags: d.problem_tags.includes(tag) ? d.problem_tags.filter(t => t !== tag) : [...d.problem_tags, tag] }))
  }

  return <>
    <PageHeader eyebrow="From the kitchen" title="Home Remedies" description="Traditional household remedies for everyday discomforts, grounded in generations of practice — and a place to share your own." />

    <div className="mb-6 flex flex-wrap gap-3">
      <div className="relative flex-1 min-w-[220px]">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/35" />
        <Input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search by problem, e.g. cough, headache…" className="pl-9" />
      </div>
      <div className="flex flex-wrap gap-2">
        {REMEDY_PROBLEM_TAGS.slice(0, 8).map(tag => (
          <button key={tag} onClick={() => setActiveTag(activeTag === tag ? null : tag)}
            className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${activeTag === tag ? 'bg-sage-700 text-white' : 'bg-sage-50 text-ink/55 hover:bg-sage-100'}`}>
            {tag.replace('_', ' ')}
          </button>
        ))}
      </div>
    </div>

    <div className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
      <div className="space-y-4">
        {remedies.data?.length ? remedies.data.map(remedy => <RemedyCard key={remedy.id} remedy={remedy} onUpvote={() => upvote.mutate(remedy.id)} />) : (
          <Card className="flex flex-col items-center p-10 text-center">
            <div className="grid h-12 w-12 place-items-center rounded-2xl bg-sage-50 text-sage-600"><ChefHat size={23} /></div>
            <h3 className="mt-4 font-bold">No remedies found</h3>
            <p className="mt-2 max-w-xs text-sm leading-6 text-ink/50">Try a different search, or be the first to share one for this problem.</p>
          </Card>
        )}
      </div>

      <Card className="h-fit p-6 sm:p-7">
        <div className="mb-5 flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-xl bg-citrus/20 text-citrus"><Upload size={18} /></div><div><h2 className="font-bold">Share a remedy</h2><p className="text-xs text-ink/45">Checked automatically before it's added.</p></div></div>
        <form onSubmit={e => { e.preventDefault(); submit.mutate() }} className="grid gap-4">
          <label><span className="mb-2 block text-sm font-bold">Title</span><Input value={draft.title} onChange={e => setDraft({ ...draft, title: e.target.value })} placeholder="e.g. Ajwain water for gas" required /></label>

          <div>
            <span className="mb-2 block text-sm font-bold">Problem(s)</span>
            <div className="flex flex-wrap gap-2">
              {REMEDY_PROBLEM_TAGS.map(tag => (
                <button type="button" key={tag} onClick={() => toggleDraftTag(tag)}
                  className={`rounded-full px-2.5 py-1 text-[11px] font-semibold transition ${draft.problem_tags.includes(tag) ? 'bg-sage-700 text-white' : 'bg-sage-50 text-ink/55 hover:bg-sage-100'}`}>
                  {tag.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          <label>
            <span className="mb-2 block text-sm font-bold">Ingredients</span>
            <div className="flex gap-2"><Input value={ingredientInput} onChange={e => setIngredientInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addIngredient() } }} placeholder="Type and press Enter" /><Button type="button" variant="secondary" onClick={addIngredient}>Add</Button></div>
            {draft.ingredients.length > 0 && <div className="mt-2 flex flex-wrap gap-2">{draft.ingredients.map(ing => <span key={ing} onClick={() => setDraft(d => ({ ...d, ingredients: d.ingredients.filter(i => i !== ing) }))} className="cursor-pointer rounded-full bg-sage-100 px-3 py-1 text-xs font-semibold text-sage-700 hover:bg-sage-200">{ing} ×</span>)}</div>}
          </label>

          <label><span className="mb-2 block text-sm font-bold">Instructions</span><textarea value={draft.instructions} onChange={e => setDraft({ ...draft, instructions: e.target.value })} rows={4} placeholder="How to prepare and use it…" required className="w-full rounded-xl border border-sage-200 bg-white px-3.5 py-2.5 text-sm outline-none ring-sage-300 placeholder:text-ink/35 focus:ring-2" /></label>

          <label><span className="mb-2 block text-sm font-bold">When to see a doctor instead (optional)</span><Input value={draft.caution} onChange={e => setDraft({ ...draft, caution: e.target.value })} placeholder="e.g. if symptoms last more than a week" /></label>

          <Button type="submit" disabled={!draft.title || !draft.instructions || !draft.problem_tags.length || !draft.ingredients.length || submit.isPending}>
            {submit.isPending ? 'Checking…' : 'Submit remedy'}
          </Button>
        </form>

        {submitResult && (submitResult.remedy
          ? <div className="mt-4 flex items-start gap-2 rounded-xl bg-emerald-50 p-3 text-xs leading-5 text-emerald-800"><ThumbsUp size={14} className="mt-0.5 shrink-0" />Thanks — your remedy was added.</div>
          : <div className="mt-4 flex items-start gap-2 rounded-xl bg-red-50 p-3 text-xs leading-5 text-red-700"><ShieldAlert size={14} className="mt-0.5 shrink-0" />{submitResult.moderation.reason || "This couldn't be added — it didn't pass our content check."}</div>
        )}
      </Card>
    </div>
  </>
}

function RemedyCard({ remedy, onUpvote }: { remedy: HomeRemedy; onUpvote: () => void }) {
  return <Card className="p-5 sm:p-6">
    <div className="mb-3 flex items-start justify-between gap-3">
      <div><h3 className="font-bold">{remedy.title}</h3>
        <div className="mt-1.5 flex flex-wrap gap-1.5">{remedy.problem_tags.map(tag => <Badge key={tag}>{tag.replace('_', ' ')}</Badge>)}</div>
      </div>
      <Badge tone={remedy.source === 'curated' ? 'green' : 'neutral'}>{remedy.source === 'curated' ? 'Traditional' : 'Community'}</Badge>
    </div>
    <p className="text-sm leading-6 text-ink/65"><span className="font-semibold text-ink/80">You'll need: </span>{remedy.ingredients.join(', ')}</p>
    <p className="mt-2 whitespace-pre-line text-sm leading-6 text-ink/65">{remedy.instructions}</p>
    {remedy.caution && <div className="mt-3 flex items-start gap-2 rounded-xl bg-amber-50 p-2.5 text-xs leading-5 text-amber-800"><AlertTriangle size={13} className="mt-0.5 shrink-0" />{remedy.caution}</div>}
    <button onClick={onUpvote} className="mt-3 inline-flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs font-semibold text-ink/45 hover:bg-sage-50 hover:text-sage-700"><ThumbsUp size={13} />{remedy.upvotes} found this helpful</button>
  </Card>
}
