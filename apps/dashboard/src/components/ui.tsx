// Reusable component library (section 11). Token-driven, dark/light aware.
import { useState, useEffect, useRef, type ReactNode, type ButtonHTMLAttributes, type TextareaHTMLAttributes } from 'react'
import { BracketCheck, Check, ChevronDown, Alert, Info, Plug, Pause, Clock, File as FileIcon } from '../lib/icons'

/* -------------------------------- Button -------------------------------- */
type ButtonVariant = 'primary' | 'secondary' | 'text' | 'destructive'
export function Button({
  variant = 'primary',
  loading,
  children,
  className = '',
  disabled,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: ButtonVariant; loading?: boolean }) {
  const variants: Record<ButtonVariant, string> = {
    primary:
      'bg-action text-on-action hover:brightness-110 disabled:opacity-40 disabled:cursor-not-allowed font-medium',
    secondary:
      'bg-transparent text-primary border border-control hover:bg-raised disabled:opacity-40 disabled:cursor-not-allowed',
    text: 'bg-transparent text-action hover:bg-raised disabled:opacity-40 disabled:cursor-not-allowed',
    destructive:
      'bg-transparent text-error border border-[color:color-mix(in_srgb,var(--status-error)_50%,transparent)] hover:bg-[color:color-mix(in_srgb,var(--status-error)_12%,transparent)] disabled:opacity-40',
  }
  return (
    <button
      disabled={disabled || loading}
      className={`inline-flex h-9 items-center justify-center gap-2 rounded-[var(--radius-control)] px-4 text-[13px] leading-5 transition-[filter,background-color,color] duration-150 ${variants[variant]} ${className}`}
      {...props}
    >
      {loading && (
        <span className="bp-spin inline-block h-3.5 w-3.5 rounded-full border-[1.5px] border-current border-t-transparent" />
      )}
      {children}
    </button>
  )
}

/* ------------------------------ StatusBadge ----------------------------- */
export type StatusKind = 'needs-explanation' | 'needs-followup' | 'verified' | 'paused' | 'unavailable'
const statusMeta: Record<StatusKind, { label: string; color: string; icon: ReactNode }> = {
  'needs-explanation': { label: 'Needs explanation', color: 'var(--status-attention)', icon: <Alert size={13} /> },
  'needs-followup': { label: 'Needs follow-up', color: 'var(--status-attention)', icon: <Info size={13} /> },
  verified: { label: 'Verified', color: 'var(--status-success)', icon: <Check size={13} /> },
  paused: { label: 'Paused', color: 'var(--text-secondary)', icon: <Pause size={13} /> },
  unavailable: { label: 'Unavailable', color: 'var(--status-error)', icon: <Alert size={13} /> },
}
export function StatusBadge({ kind, label }: { kind: StatusKind; label?: string }) {
  const m = statusMeta[kind]
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[12px] font-medium"
      style={{
        color: m.color,
        background: `color-mix(in srgb, ${m.color} 14%, transparent)`,
      }}
    >
      <span style={{ color: m.color }}>{m.icon}</span>
      {label ?? m.label}
    </span>
  )
}

/* -------------------------- ConnectionIndicator ------------------------- */
export type ConnKind = 'connected' | 'reconnecting' | 'disconnected'
export function ConnectionIndicator({ kind }: { kind: ConnKind }) {
  const meta = {
    connected: { label: 'Connected', color: 'var(--status-success)' },
    reconnecting: { label: 'Reconnecting…', color: 'var(--status-attention)' },
    disconnected: { label: 'Disconnected', color: 'var(--status-error)' },
  }[kind]
  return (
    <span className="inline-flex items-center gap-1.5 text-[12px] text-secondary">
      <span
        className={`h-2 w-2 rounded-full ${kind === 'reconnecting' ? 'bp-spin' : ''}`}
        style={{ background: meta.color, boxShadow: `0 0 0 3px color-mix(in srgb, ${meta.color} 18%, transparent)` }}
      />
      {meta.label}
    </span>
  )
}

/* ---------------------------- IntegrationMode --------------------------- */
export type IntegrationKind = 'native' | 'managed' | 'simulated'
export function IntegrationMode({ kind }: { kind: IntegrationKind }) {
  const meta = {
    native: { label: 'Claude Code connected', color: 'var(--status-success)' },
    managed: { label: 'BeProgram AI connected', color: 'var(--status-info)' },
    simulated: { label: 'Demo — external AI lock simulated', color: 'var(--status-attention)' },
  }[kind]
  return (
    <span
      className="inline-flex max-w-full shrink-0 items-center gap-1.5 rounded-full border px-2.5 py-1 text-[12px] font-medium leading-5"
      style={{ color: meta.color, borderColor: `color-mix(in srgb, ${meta.color} 40%, transparent)` }}
    >
      <Plug size={13} className="shrink-0" />
      <span className="min-w-0">{meta.label}</span>
    </span>
  )
}

/* -------------------------------- TextArea ------------------------------ */
export function TextArea({
  label,
  helper,
  error,
  className = '',
  ...props
}: TextareaHTMLAttributes<HTMLTextAreaElement> & { label: string; helper?: ReactNode; error?: string }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-[13px] font-medium text-primary">{label}</span>
      <textarea
        aria-label={label}
        className={`bp-scroll w-full resize-y rounded-[var(--radius-control)] border bg-canvas px-3 py-2.5 font-sans text-[14px] leading-[22px] text-primary placeholder:text-secondary/60 transition-colors ${
          error ? 'border-error' : 'border-control focus:border-action'
        } ${className}`}
        {...props}
      />
      {error ? (
        <span className="mt-1.5 flex items-center gap-1.5 text-[12px] text-error">
          <Alert size={12} /> {error}
        </span>
      ) : helper ? (
        <span className="mt-1.5 block text-[12px] text-secondary">{helper}</span>
      ) : null}
    </label>
  )
}

/* ------------------------------ InlineNotice ---------------------------- */
export type NoticeKind = 'info' | 'pending' | 'success' | 'error'
export function InlineNotice({
  kind,
  children,
  title,
}: {
  kind: NoticeKind
  title?: string
  children: ReactNode
}) {
  const meta = {
    info: { color: 'var(--status-info)', icon: <Info size={16} /> },
    pending: { color: 'var(--status-attention)', icon: <Clock size={16} /> },
    success: { color: 'var(--status-success)', icon: <Check size={16} /> },
    error: { color: 'var(--status-error)', icon: <Alert size={16} /> },
  }[kind]
  return (
    <div
      className="flex gap-2.5 rounded-[var(--radius-panel)] p-3 text-[13px] leading-5"
      style={{
        background: `color-mix(in srgb, ${meta.color} 10%, transparent)`,
        border: `1px solid color-mix(in srgb, ${meta.color} 28%, transparent)`,
      }}
    >
      <span className="mt-px shrink-0" style={{ color: meta.color }}>
        {meta.icon}
      </span>
      <div className="text-primary">
        {title && <div className="font-medium">{title}</div>}
        <div className={title ? 'text-secondary' : ''}>{children}</div>
      </div>
    </div>
  )
}

/* ------------------------------ FilePath -------------------------------- */
// Long paths truncate in the middle; full path exposed on hover/focus (section 6).
export function FilePath({ path, className = '' }: { path: string; className?: string }) {
  return (
    <span
      title={path}
      tabIndex={0}
      className={`inline-flex max-w-full items-center gap-1.5 truncate font-mono text-[13px] text-secondary ${className}`}
    >
      <FileIcon size={14} className="shrink-0" />
      <span className="truncate">{path}</span>
    </span>
  )
}

/* ------------------------------- Disclosure ---------------------------- */
export function Disclosure({
  summary,
  children,
  defaultOpen = false,
}: {
  summary: ReactNode
  children: ReactNode
  defaultOpen?: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="rounded-[var(--radius-panel)] border border-subtle">
      <button
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-2 rounded-[var(--radius-panel)] px-3 py-2.5 text-left text-[13px] font-medium text-primary hover:bg-raised"
      >
        {summary}
        <ChevronDown
          size={16}
          className="shrink-0 text-secondary transition-transform duration-150"
          style={{ transform: open ? 'rotate(180deg)' : 'none' }}
        />
      </button>
      {open && <div className="border-t border-subtle px-3 py-3">{children}</div>}
    </div>
  )
}

/* -------------------------------- Wordmark ----------------------------- */
export function Wordmark({ size = 'md' }: { size?: 'sm' | 'md' }) {
  return (
    <span className="inline-flex items-center gap-2 text-primary">
      <BracketCheck size={size === 'sm' ? 18 : 22} />
      <span className={`font-semibold tracking-tight ${size === 'sm' ? 'text-[14px]' : 'text-[16px]'}`}>
        BeProgram
      </span>
    </span>
  )
}

/* -------------------------------- Modal -------------------------------- */
export function Modal({
  children,
  onClose,
  wide,
}: {
  children: ReactNode
  onClose: () => void
  wide?: boolean
}) {
  const dialog = useRef<HTMLDivElement>(null)
  const close = useRef(onClose)
  close.current = onClose
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null
    const node = dialog.current
    const targets = () => Array.from(node?.querySelectorAll<HTMLElement>('button:not([disabled]),a[href],input:not([disabled]),textarea:not([disabled]),select:not([disabled]),[tabindex="0"]') || [])
    ;(targets()[0] || node)?.focus()
    const keyboard = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { event.preventDefault(); close.current() }
      if (event.key === 'Tab') {
        const items = targets(), first = items[0], last = items[items.length - 1]
        if (!items.length) { event.preventDefault(); node?.focus() }
        else if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
      }
    }
    document.addEventListener('keydown', keyboard)
    return () => { document.removeEventListener('keydown', keyboard); previous?.focus() }
  }, [])
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
      role="presentation"
    >
      <div
        ref={dialog}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-label="BeProgram dialog"
        onClick={(e) => e.stopPropagation()}
        className={`bp-enter bp-scroll max-h-[90vh] w-full overflow-y-auto rounded-[var(--radius-dialog)] border border-subtle bg-panel p-5 shadow-2xl ${
          wide ? 'max-w-[560px]' : 'max-w-[440px]'
        }`}
      >
        {children}
      </div>
    </div>
  )
}

/* ------------------------------- Annotation ---------------------------- */
// Developer handoff notes live OUTSIDE the application canvas (section 16).
export function Annotation({ id, children }: { id: string; children: ReactNode }) {
  return (
    <div className="flex items-start gap-2 rounded-[var(--radius-control)] border border-dashed border-subtle bg-canvas/40 px-3 py-2 font-mono text-[11px] leading-[16px] text-secondary">
      <span className="rounded bg-raised px-1.5 py-0.5 font-medium text-action">{id}</span>
      <span>{children}</span>
    </div>
  )
}
