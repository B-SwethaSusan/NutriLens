import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { ChevronLeft, ChevronRight, FileText, LayoutDashboard, MessageCircle, Settings, Sparkles, UploadCloud } from 'lucide-react'
import { cn } from '../lib/utils'

const links = [
  { to: '/', label: 'Overview', icon: LayoutDashboard },
  { to: '/documents', label: 'Documents', icon: FileText },
  { to: '/chat', label: 'Ask NutriLens', icon: MessageCircle },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export function Layout() {
  const [collapsed, setCollapsed] = useState(false)
  return <div className="min-h-screen bg-paper text-ink">
    <aside className={cn('fixed inset-y-0 left-0 z-20 hidden border-r border-sage-100 bg-white/90 p-4 backdrop-blur transition-all lg:flex lg:flex-col', collapsed ? 'w-20' : 'w-64')}>
      <div className="mb-10 flex items-center gap-3 px-2"><div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-sage-700 text-white"><Sparkles size={20} /></div>{!collapsed && <div><p className="font-bold tracking-tight">NutriLens</p><p className="text-[11px] text-ink/45">your document dietitian</p></div>}</div>
      <nav className="space-y-1">{links.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} end={to === '/'} title={label} className={({ isActive }) => cn('flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold transition', isActive ? 'bg-sage-100 text-sage-700' : 'text-ink/50 hover:bg-sage-50 hover:text-ink', collapsed && 'justify-center')}>{({ isActive }) => <><Icon size={19} strokeWidth={isActive ? 2.4 : 1.8} />{!collapsed && label}</>}</NavLink>)}</nav>
      <div className="mt-auto space-y-2"><button onClick={() => setCollapsed(!collapsed)} className="hidden w-full items-center justify-center rounded-xl p-2 text-ink/40 hover:bg-sage-50 lg:flex">{collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}</button><div className={cn('flex items-center gap-3 rounded-xl bg-sage-50 p-3', collapsed && 'justify-center p-2')}><div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-citrus text-sm font-bold text-white">A</div>{!collapsed && <div className="min-w-0"><p className="truncate text-xs font-bold">Nutrition workspace</p><p className="truncate text-[11px] text-ink/45">Private and grounded</p></div>}</div></div>
    </aside>
    <main className={cn('min-h-screen transition-all lg:pl-64', collapsed && 'lg:pl-20')}><div className="mx-auto max-w-7xl p-5 sm:p-8"><Outlet /></div></main>
    <div className="fixed inset-x-0 bottom-0 z-30 flex justify-around border-t border-sage-100 bg-white p-2 lg:hidden">{links.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => cn('flex flex-col items-center gap-1 px-3 py-1 text-[10px] font-semibold', isActive ? 'text-sage-700' : 'text-ink/40')}><Icon size={19} />{label}</NavLink>)}</div>
  </div>
}

export function PageHeader({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description?: string; action?: React.ReactNode }) { return <header className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="mb-2 text-xs font-bold uppercase tracking-[0.2em] text-sage-600">{eyebrow || 'Workspace'}</p><h1 className="text-3xl font-bold tracking-tight sm:text-4xl">{title}</h1>{description && <p className="mt-2 max-w-xl text-sm leading-6 text-ink/55">{description}</p>}</div>{action}</header> }
