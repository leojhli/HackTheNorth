// The learning-history website (section 9). Shares the extension's typography,
// status language, and components; uses more whitespace. Evidence-led, not a
// chart dashboard.
import { useState } from 'react'
import * as fx from '../lib/fixture'
import { Button, StatusBadge, Wordmark, InlineNotice, FilePath } from './ui'
import { CodeDiff, CodeUnavailable } from './CodeExcerpt'
import { ReceiptCard } from './v3'
import { ArrowLeft, ChevronRight, ExternalLink, Refresh, Lock, Trash, Settings, Check, Plug } from '../lib/icons'

export type WebCallbacks = {
  onCreateReceipt: () => void
  onPreparePR: () => void
  onImportPR: () => void
}

type WebRoute =
  | { name: 'today' }
  | { name: 'evidence'; file: string }
  | { name: 'settings' }
type HistoryVariant = 'ready' | 'empty' | 'loading' | 'error'

export function Website({
  passed,
  onOpenVSCode,
  cb,
}: {
  passed: boolean
  onOpenVSCode: () => void
  cb: WebCallbacks
}) {
  const [route, setRoute] = useState<WebRoute>({ name: 'today' })
  const [variant, setVariant] = useState<HistoryVariant>('ready')
  const rows = passed ? fx.HISTORY_AFTER : fx.HISTORY_BEFORE

  return (
    <div className="min-h-full bg-canvas text-primary">
      <TopNav />
      <main className="mx-auto w-full max-w-[1120px] px-4 py-8 sm:px-6 md:px-8">
        {route.name === 'today' && (
          <Today
            rows={rows}
            passed={passed}
            variant={variant}
            onVariant={setVariant}
            onOpenEvidence={(file) => setRoute({ name: 'evidence', file })}
            onOpenVSCode={onOpenVSCode}
            onSettings={() => setRoute({ name: 'settings' })}
          />
        )}
        {route.name === 'evidence' && (
          <Evidence file={route.file} passed={passed} onBack={() => setRoute({ name: 'today' })} cb={cb} />
        )}
        {route.name === 'settings' && (
          <SettingsPage onBack={() => setRoute({ name: 'today' })} cb={cb} />
        )}
      </main>
    </div>
  )
}

function TopNav() {
  return (
    <header className="sticky top-0 z-10 border-b border-subtle bg-panel/85 backdrop-blur">
      <div className="mx-auto flex w-full max-w-[1120px] items-center justify-between gap-4 px-4 py-3 sm:px-6 md:px-8">
        <div className="flex items-center gap-3">
          <Wordmark size="sm" />
          <span className="hidden text-[13px] text-secondary sm:inline">
            · <span className="font-mono">{fx.PROJECT}</span> · {fx.SESSION_DATE}
          </span>
        </div>
        <button className="flex h-8 w-8 items-center justify-center rounded-full bg-raised text-[12px] font-medium text-primary">
          AR
        </button>
      </div>
    </header>
  )
}

/* ------------------------------- W01 ----------------------------------- */
function Today({
  rows,
  passed,
  variant,
  onVariant,
  onOpenEvidence,
  onOpenVSCode,
  onSettings,
}: {
  rows: fx.HistoryRow[]
  passed: boolean
  variant: HistoryVariant
  onVariant: (v: HistoryVariant) => void
  onOpenEvidence: (file: string) => void
  onOpenVSCode: () => void
  onSettings: () => void
}) {
  const demonstrated = rows.filter((r) => r.status === 'demonstrated').length
  const awaiting = rows.filter((r) => r.status === 'needs-explanation').length

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div className="space-y-1.5">
          <h1 className="text-[28px] font-semibold leading-[36px]">Today’s session</h1>
          <p className="text-[14px] text-secondary">
            <span className="font-mono">{fx.PROJECT}</span> · {fx.LANGUAGE}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={onOpenVSCode}>
            <ExternalLink size={14} /> Open in VS Code
          </Button>
          <button
            aria-label="Refresh"
            className="flex h-9 w-9 items-center justify-center rounded-[var(--radius-control)] border border-subtle text-secondary hover:bg-raised hover:text-primary"
          >
            <Refresh size={16} />
          </button>
          <button
            aria-label="Settings"
            onClick={onSettings}
            className="flex h-9 w-9 items-center justify-center rounded-[var(--radius-control)] border border-subtle text-secondary hover:bg-raised hover:text-primary"
          >
            <Settings size={16} />
          </button>
        </div>
      </div>

      {/* Evidence counts — records in this session, not skill scores. */}
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-[14px] text-secondary">
        <span className="text-primary">
          <span className="font-semibold">{demonstrated}</span> concepts demonstrated
        </span>
        <span>·</span>
        <span>
          <span className="font-semibold text-primary">{awaiting}</span> awaiting explanation
        </span>
      </div>

      {/* Dev-only control to preview the required W03 history variants. */}
      <VariantSwitcher variant={variant} onVariant={onVariant} />

      {variant === 'loading' && <LoadingRows />}
      {variant === 'empty' && (
        <EmptyState
          title="Your learning history starts with your first checkpoint."
          body="Start a coding session in desktop VS Code, and demonstrated concepts will appear here."
          cta="Open VS Code"
          onCta={onOpenVSCode}
        />
      )}
      {variant === 'error' && (
        <EmptyState
          tone="error"
          title="We couldn’t load this session."
          body="This can happen if the connection dropped. Your saved history is safe."
          cta="Try again"
          onCta={() => onVariant('ready')}
        />
      )}

      {variant === 'ready' && (
        <div className="space-y-3">
          {rows.map((r) => (
            <button
              key={r.file}
              onClick={() => r.hasEvidence && onOpenEvidence(r.file)}
              disabled={!r.hasEvidence}
              className="group flex w-full items-center gap-4 rounded-[var(--radius-panel)] border border-subtle bg-panel px-4 py-4 text-left transition-colors hover:enabled:border-control disabled:cursor-default"
            >
              <div className="min-w-0 flex-1 space-y-1">
                <div className="flex items-center gap-3">
                  <span className="text-[15px] font-medium">{r.concept}</span>
                  <StatusBadge kind={r.status === 'demonstrated' ? 'verified' : 'needs-explanation'} />
                </div>
                <FilePath path={r.file} />
              </div>
              <span className="whitespace-nowrap text-[13px] text-secondary">{r.time}</span>
              {r.hasEvidence && (
                <ChevronRight size={18} className="text-secondary transition-transform group-hover:translate-x-0.5" />
              )}
            </button>
          ))}
        </div>
      )}

      <footer className="flex items-center gap-1.5 border-t border-subtle pt-5 text-[13px] text-secondary">
        <Lock size={14} /> Private to you
        {passed && (
          <span className="ml-auto inline-flex items-center gap-1.5 text-success">
            <Check size={14} /> Session up to date
          </span>
        )}
      </footer>
    </div>
  )
}

/* ------------------------------- W02 ----------------------------------- */
function Evidence({
  file,
  passed,
  onBack,
  cb,
}: {
  file: string
  passed: boolean
  onBack: () => void
  cb: WebCallbacks
}) {
  const [codeAvailable, setCodeAvailable] = useState(true)
  const row = (passed ? fx.HISTORY_AFTER : fx.HISTORY_BEFORE).find((r) => r.file === file)
  const isPassed = row?.status === 'demonstrated'

  return (
    <div className="space-y-6">
      <button onClick={onBack} className="inline-flex items-center gap-1.5 text-[13px] text-secondary hover:text-primary">
        <ArrowLeft size={16} /> Today’s session <span className="text-subtle">/</span>{' '}
        <span className="text-primary">{fx.CONCEPT}</span>
      </button>

      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-[28px] font-semibold leading-[36px]">{fx.CONCEPT}</h1>
        <StatusBadge kind={isPassed ? 'verified' : 'needs-explanation'} />
      </div>
      <p className="text-[14px] text-secondary">
        <FilePath path={file} /> · {row?.time} · This result covers the captured code shown below.
      </p>

      {/* Desktop: code beside the reasoning sequence. */}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,44%)_minmax(0,56%)]">
        <div className="space-y-3 lg:sticky lg:top-20 lg:self-start">
          {codeAvailable ? (
            <CodeDiff file={file} capturedAt="2:24 PM" lines={fx.CAPTURED_DIFF} />
          ) : (
            <CodeUnavailable file={file} />
          )}
          <button
            onClick={() => setCodeAvailable((v) => !v)}
            className="text-[12px] text-secondary underline decoration-dotted hover:text-primary"
          >
            Preview “code excerpt unavailable” state
          </button>
        </div>

        <div className="space-y-5">
          <EvidenceSection label="Initial question">{fx.INITIAL_QUESTION.replace(/`/g, '')}</EvidenceSection>
          <EvidenceSection label="Initial answer" muted>
            {fx.WEAK_ANSWER}
          </EvidenceSection>
          <EvidenceSection label="Feedback">{fx.FOLLOWUP_FEEDBACK}</EvidenceSection>
          <EvidenceSection label="Follow-up question">{fx.FOLLOWUP_QUESTION.replace(/`/g, '')}</EvidenceSection>
          <EvidenceSection label="Follow-up answer" muted>
            {fx.PASSING_ANSWER}
          </EvidenceSection>
          {isPassed && (
            <div
              className="rounded-[var(--radius-panel)] border p-4"
              style={{
                borderColor: 'color-mix(in srgb, var(--status-success) 32%, transparent)',
                background: 'color-mix(in srgb, var(--status-success) 8%, transparent)',
              }}
            >
              <div className="mb-1.5 flex items-center gap-1.5 text-[13px] font-medium text-success">
                <Check size={15} /> Demonstrated reasoning
              </div>
              <p className="text-[14px] leading-[22px] text-primary">{fx.SUCCESS_FEEDBACK}</p>
            </div>
          )}

          {isPassed && (
            <>
              <ReceiptCard onCreate={cb.onCreateReceipt} />
              <div className="flex items-center gap-2">
                <Button variant="secondary" onClick={cb.onPreparePR}>
                  Prepare PR summary
                </Button>
                <span className="text-[12px] text-secondary">Owner-approved evidence only</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function EvidenceSection({ label, children, muted }: { label: string; children: React.ReactNode; muted?: boolean }) {
  return (
    <div>
      <div className="mb-1.5 text-[12px] font-medium uppercase tracking-wide text-secondary">{label}</div>
      <p
        className={`text-[14px] leading-[22px] ${
          muted ? 'rounded-[var(--radius-panel)] border border-subtle bg-panel p-3.5 text-primary' : 'text-primary'
        }`}
      >
        {children}
      </p>
    </div>
  )
}

/* ------------------------------- S01 ----------------------------------- */
function SettingsPage({ onBack, cb }: { onBack: () => void; cb: WebCallbacks }) {
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [github, setGithub] = useState(true)
  return (
    <div className="mx-auto max-w-[720px] space-y-6">
      <button onClick={onBack} className="inline-flex items-center gap-1.5 text-[13px] text-secondary hover:text-primary">
        <ArrowLeft size={16} /> Back to session
      </button>
      <h1 className="text-[28px] font-semibold leading-[36px]">Project scope &amp; privacy</h1>

      <Card title="Source files in scope">
        <ul className="divide-y divide-[color:var(--border-subtle)]">
          {fx.INCLUDED_FILES.map((f) => (
            <li key={f} className="flex items-center justify-between py-2.5">
              <FilePath path={f} />
              <input type="checkbox" defaultChecked className="accent-[var(--action-primary)]" aria-label={`Include ${f}`} />
            </li>
          ))}
          {fx.EXCLUDED_FILES.map((f) => (
            <li key={f.path} className="flex items-center justify-between py-2.5 opacity-70">
              <FilePath path={f.path} />
              <span className="text-[12px] text-secondary">{f.reason}</span>
            </li>
          ))}
        </ul>
      </Card>

      <Card title="Connected services">
        <ul className="divide-y divide-[color:var(--border-subtle)]">
          <li className="flex items-center justify-between gap-3 py-3">
            <div className="flex items-center gap-2">
              <Plug size={16} className="text-info" />
              <div>
                <div className="text-[14px]">CodeProof AI</div>
                <div className="text-[12px] text-secondary">Managed evaluation · code review scope</div>
              </div>
            </div>
            <StatusBadge kind="verified" label="Connected" />
          </li>
          <li className="flex items-center justify-between gap-3 py-3">
            <div className="flex items-center gap-2">
              <Plug size={16} className={github ? 'text-success' : 'text-secondary'} />
              <div>
                <div className="text-[14px]">GitHub</div>
                <div className="text-[12px] text-secondary">
                  {github ? `@${fx.GITHUB_ACCOUNT} · read PRs on selected repos` : 'Not connected'}
                </div>
              </div>
            </div>
            {github ? (
              <div className="flex items-center gap-2">
                <Button variant="secondary" onClick={cb.onImportPR}>
                  Review a PR
                </Button>
                <Button variant="text" onClick={() => setGithub(false)}>
                  Unlink
                </Button>
              </div>
            ) : (
              <Button variant="secondary" onClick={() => setGithub(true)}>
                Connect
              </Button>
            )}
          </li>
        </ul>
      </Card>

      <Card title="AI provider &amp; privacy">
        <InlineNotice kind="info">{fx.PROVIDER_DISCLOSURE}</InlineNotice>
        <div className="mt-3 flex items-center gap-1.5 text-[13px] text-secondary">
          <Lock size={14} /> Visibility: Private to you
        </div>
      </Card>

      <div className="flex gap-2">
        <Button>Save settings</Button>
        <Button variant="secondary" onClick={onBack}>
          Cancel
        </Button>
      </div>

      <Card title="Danger zone" tone="error">
        <p className="mb-3 text-[13px] leading-5 text-secondary">
          Delete all learning history for <span className="font-mono text-primary">{fx.PROJECT}</span>. This removes
          every stored explanation and captured excerpt for this project. Ending a session does not delete history —
          this does.
        </p>
        {!confirmDelete ? (
          <Button variant="destructive" onClick={() => setConfirmDelete(true)}>
            <Trash size={14} /> Delete project history
          </Button>
        ) : (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[13px] text-error">Permanently delete all evidence for {fx.PROJECT}?</span>
            <Button variant="destructive">Yes, delete history</Button>
            <Button variant="secondary" onClick={() => setConfirmDelete(false)}>
              Keep history
            </Button>
          </div>
        )}
      </Card>
    </div>
  )
}

function Card({
  title,
  children,
  tone,
}: {
  title: React.ReactNode
  children: React.ReactNode
  tone?: 'error'
}) {
  return (
    <section
      className="rounded-[var(--radius-panel)] border bg-panel p-5"
      style={
        tone === 'error'
          ? { borderColor: 'color-mix(in srgb, var(--status-error) 32%, transparent)' }
          : { borderColor: 'var(--border-subtle)' }
      }
    >
      <h2 className={`mb-3 text-[15px] font-semibold ${tone === 'error' ? 'text-error' : ''}`}>{title}</h2>
      {children}
    </section>
  )
}

/* --------------------------- W03 variants ------------------------------ */
function VariantSwitcher({ variant, onVariant }: { variant: HistoryVariant; onVariant: (v: HistoryVariant) => void }) {
  const opts: HistoryVariant[] = ['ready', 'loading', 'empty', 'error']
  return (
    <div className="flex flex-wrap items-center gap-1.5 text-[12px]">
      <span className="mr-1 font-mono text-secondary">W03 states:</span>
      {opts.map((o) => (
        <button
          key={o}
          onClick={() => onVariant(o)}
          className={`rounded-full px-2.5 py-1 capitalize transition-colors ${
            variant === o ? 'bg-action text-on-action' : 'border border-subtle text-secondary hover:bg-raised'
          }`}
        >
          {o}
        </button>
      ))}
    </div>
  )
}

function LoadingRows() {
  return (
    <div className="space-y-3">
      {[0, 1, 2].map((i) => (
        <div key={i} className="flex items-center gap-4 rounded-[var(--radius-panel)] border border-subtle bg-panel px-4 py-4">
          <div className="flex-1 space-y-2">
            <div className="h-4 w-40 rounded bg-raised" />
            <div className="h-3 w-56 rounded bg-raised opacity-70" />
          </div>
          <div className="h-3 w-12 rounded bg-raised opacity-70" />
        </div>
      ))}
    </div>
  )
}

function EmptyState({
  title,
  body,
  cta,
  onCta,
  tone,
}: {
  title: string
  body: string
  cta: string
  onCta: () => void
  tone?: 'error'
}) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-[var(--radius-panel)] border border-dashed border-subtle bg-panel px-6 py-14 text-center">
      <div
        className="flex h-11 w-11 items-center justify-center rounded-full"
        style={{
          background:
            tone === 'error'
              ? 'color-mix(in srgb, var(--status-error) 14%, transparent)'
              : 'var(--surface-raised)',
          color: tone === 'error' ? 'var(--status-error)' : 'var(--text-secondary)',
        }}
      >
        {tone === 'error' ? <Refresh size={20} /> : <Lock size={20} />}
      </div>
      <h3 className="text-[16px] font-semibold">{title}</h3>
      <p className="max-w-[420px] text-[14px] leading-[22px] text-secondary">{body}</p>
      <Button variant={tone === 'error' ? 'secondary' : 'primary'} onClick={onCta} className="mt-1">
        {cta}
      </Button>
    </div>
  )
}
