import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Scale, TrendingDown, TrendingUp, Minus } from 'lucide-react'
import { api, type ProgressSummary } from '../lib/api'
import { Badge, Button, Card, Input } from '../components/ui'
import { PageHeader } from '../components/Layout'
import { formatDate } from '../lib/utils'

export function ProgressPage() {
  const queryClient = useQueryClient()
  const query = useQuery({ queryKey: ['progress'], queryFn: async () => (await api.get<ProgressSummary>('/progress')).data })
  const [weight, setWeight] = useState('')
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10))
  const [note, setNote] = useState('')

  const logEntry = useMutation({
    mutationFn: () => api.post('/progress', { log_date: `${date}T00:00:00Z`, weight_kg: weight ? Number(weight) : null, note: note || null }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['progress'] }); setWeight(''); setNote('') },
  })

  const logs = query.data?.logs || []
  const trend = query.data?.trend

  return <>
    <PageHeader eyebrow="Keep going" title="Progress" description="Log your weight over time and see an honest trend — no overfitting to a handful of noisy points." />
    <div className="grid gap-6 xl:grid-cols-[1fr_1.3fr]">
      <Card className="p-6 sm:p-8">
        <div className="mb-6 flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-xl bg-sage-100 text-sage-700"><Scale size={19} /></div><h2 className="font-bold">Log today</h2></div>
        <form onSubmit={e => { e.preventDefault(); logEntry.mutate() }} className="grid gap-4">
          <label><span className="mb-2 block text-sm font-bold">Date</span><Input type="date" value={date} onChange={e => setDate(e.target.value)} /></label>
          <label><span className="mb-2 block text-sm font-bold">Weight (kg)</span><Input type="number" step="0.1" value={weight} onChange={e => setWeight(e.target.value)} placeholder="e.g. 68.5" /></label>
          <label><span className="mb-2 block text-sm font-bold">Note (optional)</span><Input value={note} onChange={e => setNote(e.target.value)} placeholder="How did today go?" /></label>
          <Button type="submit" disabled={!weight || logEntry.isPending}>{logEntry.isPending ? 'Saving…' : 'Save entry'}</Button>
        </form>

        {trend && <div className="mt-6 rounded-xl bg-sage-50/60 p-4">
          <div className="mb-2 flex items-center gap-2 text-sm font-bold">
            {trend.slope_kg_per_week < -0.05 ? <TrendingDown size={16} className="text-emerald-600" /> : trend.slope_kg_per_week > 0.05 ? <TrendingUp size={16} className="text-amber-600" /> : <Minus size={16} className="text-ink/40" />}
            Trend
          </div>
          <p className="text-sm leading-6 text-ink/65">{trend.message}</p>
          {trend.on_track !== null && <Badge tone={trend.on_track ? 'green' : 'amber'} >{trend.on_track ? 'On track' : 'Below target pace'}</Badge>}
        </div>}
      </Card>

      <div className="space-y-6">
        <Card className="p-6">
          <h2 className="mb-4 font-bold">Weight over time</h2>
          {logs.filter(l => l.weight_kg != null).length >= 2
            ? <WeightChart logs={logs.filter(l => l.weight_kg != null)} />
            : <p className="py-10 text-center text-sm text-ink/45">Log at least 2 entries to see a chart. Need 3+ for a trend projection.</p>}
        </Card>
        <Card className="overflow-hidden">
          <div className="border-b border-sage-100 px-5 py-4"><h3 className="text-sm font-bold">History</h3></div>
          <div className="max-h-80 overflow-y-auto divide-y divide-sage-50">
            {logs.length ? [...logs].reverse().map(log => <div key={log.id} className="flex items-center justify-between px-5 py-3 text-sm">
              <div><p className="font-semibold">{formatDate(log.log_date)}</p>{log.note && <p className="text-xs text-ink/45">{log.note}</p>}</div>
              {log.weight_kg != null && <Badge>{log.weight_kg} kg</Badge>}
            </div>) : <p className="p-5 text-sm text-ink/45">No entries yet — log your first one.</p>}
          </div>
        </Card>
      </div>
    </div>
  </>
}

function WeightChart({ logs }: { logs: { log_date: string; weight_kg?: number | null }[] }) {
  const points = logs.map(l => ({ date: new Date(l.log_date).getTime(), weight: l.weight_kg as number })).sort((a, b) => a.date - b.date)
  const width = 560, height = 180, padding = 24
  const minWeight = Math.min(...points.map(p => p.weight)) - 1
  const maxWeight = Math.max(...points.map(p => p.weight)) + 1
  const minDate = points[0].date, maxDate = points[points.length - 1].date || minDate + 1
  const x = (d: number) => padding + (d - minDate) / Math.max(maxDate - minDate, 1) * (width - padding * 2)
  const y = (w: number) => height - padding - (w - minWeight) / Math.max(maxWeight - minWeight, 1) * (height - padding * 2)
  const path = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${x(p.date)},${y(p.weight)}`).join(' ')

  return <svg viewBox={`0 0 ${width} ${height}`} className="w-full" role="img" aria-label="Weight trend chart">
    <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#c8e1cb" strokeWidth={1} />
    <path d={path} fill="none" stroke="#398257" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
    {points.map((p, i) => <circle key={i} cx={x(p.date)} cy={y(p.weight)} r={3.5} fill="#286746" />)}
  </svg>
}
