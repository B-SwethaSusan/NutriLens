import { forwardRef, type ButtonHTMLAttributes, type InputHTMLAttributes, type HTMLAttributes } from 'react'
import { cn } from '../lib/utils'

export const Button = forwardRef<HTMLButtonElement, ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'ghost' | 'danger' }>(function Button({ className, variant = 'primary', ...props }, ref) {
  const variants = { primary: 'bg-sage-700 text-white hover:bg-sage-600', secondary: 'bg-sage-100 text-sage-700 hover:bg-sage-200', ghost: 'text-ink/60 hover:bg-sage-50 hover:text-ink', danger: 'bg-red-50 text-red-700 hover:bg-red-100' }
  return <button ref={ref} className={cn('inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50', variants[variant], className)} {...props} />
})
export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(function Input({ className, ...props }, ref) { return <input ref={ref} className={cn('w-full rounded-xl border border-sage-200 bg-white px-3.5 py-2.5 text-sm text-ink outline-none ring-sage-300 transition placeholder:text-ink/35 focus:ring-2', className)} {...props} /> })
export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) { return <div className={cn('rounded-2xl border border-sage-100 bg-white shadow-soft', className)} {...props} /> }
export function Badge({ children, tone = 'neutral' }: { children: React.ReactNode; tone?: 'neutral' | 'green' | 'amber' | 'red' }) { const tones = { neutral: 'bg-sage-50 text-ink/60', green: 'bg-emerald-50 text-emerald-700', amber: 'bg-amber-50 text-amber-700', red: 'bg-red-50 text-red-700' }; return <span className={cn('inline-flex rounded-full px-2.5 py-1 text-xs font-semibold', tones[tone])}>{children}</span> }
