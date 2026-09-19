// CodeExcerpt (section 11): inline diff, plain, loading, unavailable variants.
import { type DiffLine } from '../lib/fixture'
import { FilePath } from './ui'
import { Clock, Alert } from '../lib/icons'

type Common = { file: string; capturedAt?: string; collapsible?: boolean; label?: string }

function Frame({
  file,
  capturedAt,
  children,
  label = 'Captured for this checkpoint',
}: Common & { children: React.ReactNode; label?: string }) {
  return (
    <div className="overflow-hidden rounded-[var(--radius-panel)] border border-subtle bg-canvas">
      <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 border-b border-subtle bg-panel/60 px-3 py-2">
        <FilePath path={file} />
        <span className="flex flex-wrap items-center gap-1.5 text-[12px] text-secondary">
          {label}
          {capturedAt && (
            <>
              <span aria-hidden>·</span>
              <span className="inline-flex items-center gap-1.5 whitespace-nowrap"><Clock size={12} /> {capturedAt}</span>
            </>
          )}
        </span>
      </div>
      <div className="bp-scroll max-h-[280px] overflow-auto">{children}</div>
    </div>
  )
}

export function CodeDiff({ lines, ...common }: Common & { lines: DiffLine[] }) {
  return (
    <Frame {...common}>
      <pre className="min-w-max font-mono text-[13px] leading-5">
        {lines.map((l, i) => {
          const marker = l.kind === 'add' ? '+' : l.kind === 'del' ? '−' : ' '
          const bg =
            l.kind === 'add'
              ? 'color-mix(in srgb, var(--status-success) 12%, transparent)'
              : l.kind === 'del'
                ? 'color-mix(in srgb, var(--status-error) 12%, transparent)'
                : 'transparent'
          const markerColor =
            l.kind === 'add' ? 'var(--status-success)' : l.kind === 'del' ? 'var(--status-error)' : 'var(--text-secondary)'
          return (
            <div key={i} className="flex" style={{ background: bg }}>
              <span
                className="w-8 shrink-0 select-none border-r border-subtle/60 px-2 text-right text-[11px]"
                style={{ color: 'var(--text-secondary)' }}
              >
                {i + 1}
              </span>
              <span className="w-5 shrink-0 select-none text-center font-medium" style={{ color: markerColor }} aria-label={l.kind}>
                {marker}
              </span>
              <code className="whitespace-pre pr-4 text-primary">{l.text}</code>
            </div>
          )
        })}
      </pre>
    </Frame>
  )
}

export function CodePlain({ code, ...common }: Common & { code: string }) {
  return (
    <Frame {...common}>
      <pre className="min-w-max px-3 py-2 font-mono text-[13px] leading-5 text-primary">
        <code>{code}</code>
      </pre>
    </Frame>
  )
}

export function CodeLoading({ file }: { file: string }) {
  return (
    <Frame file={file} label="Capturing…">
      <div className="space-y-2 px-3 py-3">
        {[70, 92, 60, 84, 48].map((w, i) => (
          <div key={i} className="h-3.5 rounded bg-raised" style={{ width: `${w}%`, opacity: 0.6 }} />
        ))}
      </div>
    </Frame>
  )
}

export function CodeUnavailable({ file }: { file: string }) {
  return (
    <Frame file={file} label="Code excerpt unavailable">
      <div className="flex items-center gap-2 px-3 py-6 text-[13px] text-secondary">
        <Alert size={16} className="text-attention" />
        This captured code has expired or been deleted. The result metadata is retained below.
      </div>
    </Frame>
  )
}
