// PRD v3 delta: optional voice, assessment-receipt, and GitHub-PR features.
// All secondary/optional — learning success never depends on them (section 11).
import { useEffect, useRef, useState } from 'react'
import * as fx from '../lib/fixture'
import { Button, InlineNotice, Modal, StatusBadge, TextArea, FilePath, Wordmark } from './ui'
import {
  Check,
  X,
  Alert,
  Info,
  Plug,
  Lock,
  ArrowLeft,
  ExternalLink,
} from '../lib/icons'

/* ==================================================================== *
 * Voice — SpeechPlayback + VoiceAnswer (section 3). P1, reused E05/E07.
 * ==================================================================== */
export function SpeechPlayback({ text }: { text: string }) {
  const [playing, setPlaying] = useState(false)
  const supported = typeof window !== 'undefined' && 'speechSynthesis' in window
  useEffect(() => {
    return () => {
      if (supported) window.speechSynthesis.cancel()
    }
  }, [supported])
  if (!supported) {
    return (
      <span title="Playback unavailable in this browser" className="text-secondary/60">
        <SpeakerIcon muted />
      </span>
    )
  }
  const toggle = () => {
    if (playing) {
      window.speechSynthesis.cancel()
      setPlaying(false)
    } else {
      const u = new SpeechSynthesisUtterance(text.replace(/`/g, ''))
      u.onend = () => setPlaying(false)
      window.speechSynthesis.speak(u)
      setPlaying(true)
    }
  }
  return (
    <button
      onClick={toggle}
      aria-label={playing ? 'Stop playback' : 'Listen to question'}
      className="rounded-[var(--radius-control)] p-1.5 text-secondary hover:bg-raised hover:text-primary"
    >
      {playing ? <span className="text-action"><SpeakerIcon /></span> : <SpeakerIcon />}
    </button>
  )
}

function SpeakerIcon({ muted }: { muted?: boolean }) {
  return (
    <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <path d="M11 5 6 9H3v6h3l5 4V5Z" />
      {muted ? <path d="m22 9-6 6M16 9l6 6" /> : <path d="M15.5 8.5a5 5 0 0 1 0 7M18.5 6a9 9 0 0 1 0 12" />}
    </svg>
  )
}

type VoiceStage = 'ready' | 'permission' | 'recording' | 'transcribing' | 'review' | 'error'

// Record answer sits BESIDE the text input and never narrows it (section 3).
export function VoiceAnswer({ onTranscript }: { onTranscript: (t: string) => void }) {
  const [stage, setStage] = useState<VoiceStage>('ready')
  const [elapsed, setElapsed] = useState(0)
  const [transcript, setTranscript] = useState('')
  const timer = useRef<number>(0)

  useEffect(() => () => window.clearInterval(timer.current), [])

  const startRecording = () => {
    setStage('recording')
    setElapsed(0)
    timer.current = window.setInterval(() => setElapsed((e) => e + 1), 1000)
  }
  const stop = () => {
    window.clearInterval(timer.current)
    setStage('transcribing')
    window.setTimeout(() => {
      setTranscript(fx.PASSING_ANSWER)
      setStage('review')
    }, 1400)
  }
  const cancel = () => {
    window.clearInterval(timer.current)
    setStage('ready')
  }

  if (stage === 'ready') {
    return (
      <button
        onClick={() => setStage('permission')}
        className="inline-flex items-center gap-2 rounded-[var(--radius-control)] border border-control px-3 py-2 text-[13px] text-primary hover:bg-raised"
      >
        <MicIcon /> Record answer
      </button>
    )
  }
  if (stage === 'permission') {
    return (
      <div className="space-y-2 rounded-[var(--radius-panel)] border border-subtle bg-canvas p-3">
        <p className="text-[13px] text-secondary">
          CodeProof needs microphone access to record your spoken explanation. Audio is transcribed to
          reviewable text; you submit the text.
        </p>
        <div className="flex gap-2">
          <Button onClick={startRecording}>Allow microphone</Button>
          <Button variant="secondary" onClick={() => setStage('error')}>
            Not now
          </Button>
        </div>
      </div>
    )
  }
  if (stage === 'recording') {
    return (
      <div className="flex items-center gap-3 rounded-[var(--radius-panel)] border border-subtle bg-canvas p-3">
        <span className="flex items-center gap-2 text-[13px] font-medium text-error">
          <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-error" /> Recording
        </span>
        <span className="font-mono text-[13px] text-secondary">
          {String(Math.floor(elapsed / 60)).padStart(2, '0')}:{String(elapsed % 60).padStart(2, '0')}
        </span>
        <div className="ml-auto flex gap-2">
          <Button onClick={stop}>Stop</Button>
          <Button variant="secondary" onClick={cancel}>
            Cancel
          </Button>
        </div>
      </div>
    )
  }
  if (stage === 'transcribing') {
    return (
      <div className="flex items-center gap-2.5 rounded-[var(--radius-panel)] border border-subtle bg-canvas p-3 text-[13px] text-secondary">
        <span className="bp-spin inline-block h-4 w-4 rounded-full border-2 border-action border-t-transparent" />
        Preparing your transcript…
      </div>
    )
  }
  if (stage === 'review') {
    return (
      <div className="space-y-2 rounded-[var(--radius-panel)] border border-subtle bg-canvas p-3">
        <TextArea
          label="Review your transcript before submitting"
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          className="min-h-[100px]"
        />
        <div className="flex gap-2">
          <Button
            onClick={() => {
              onTranscript(transcript)
              setStage('ready')
            }}
          >
            Use this transcript
          </Button>
          <Button variant="secondary" onClick={() => setStage('ready')}>
            Discard
          </Button>
        </div>
      </div>
    )
  }
  return (
    <InlineNotice kind="info">
      Microphone unavailable. You can type your answer instead.
      <button onClick={() => setStage('ready')} className="ml-2 text-action underline">
        Try recording again
      </button>
    </InlineNotice>
  )
}

function MicIcon() {
  return (
    <svg width={15} height={15} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="3" width="6" height="11" rx="3" />
      <path d="M6 11a6 6 0 0 0 12 0M12 17v4" />
    </svg>
  )
}

/* ==================================================================== *
 * Assessment receipt — C01 consent + C02 issuance (section 5).
 * ==================================================================== */
type ReceiptStep = 'consent' | 'issuing' | 'confirmed' | 'failed'

export function ReceiptFlow({ onClose, onOpenVerifier }: { onClose: () => void; onOpenVerifier: () => void }) {
  const [step, setStep] = useState<ReceiptStep>('consent')
  const [wallet, setWallet] = useState<'disconnected' | 'connected'>('disconnected')
  const [fail, setFail] = useState(false)

  const create = () => {
    setStep('issuing')
    window.setTimeout(() => setStep(fail ? 'failed' : 'confirmed'), 1800)
  }

  return (
    <Modal onClose={onClose} wide>
      {step === 'consent' && (
        <div className="space-y-4">
          <Header id="C01" title="Create verifiable receipt" onClose={onClose} />
          <p className="text-[13px] leading-5 text-secondary">
            Create an optional record that others can check for issuer and evidence integrity.{' '}
            <span className="text-primary">This does not independently prove skill mastery.</span>
          </p>

          <div className="rounded-[var(--radius-panel)] border border-subtle">
            <div className="border-b border-subtle px-3 py-2 text-[12px] font-medium uppercase tracking-wide text-secondary">
              Public record — cannot be reversed by deleting your history
            </div>
            <dl className="divide-y divide-[color:var(--border-subtle)]">
              {fx.RECEIPT_PUBLIC_FIELDS.map((f) => (
                <div key={f.label} className="flex justify-between gap-4 px-3 py-2 text-[13px]">
                  <dt className="text-secondary">{f.label}</dt>
                  <dd className="text-right text-primary">{f.value}</dd>
                </div>
              ))}
            </dl>
          </div>

          <div className="rounded-[var(--radius-panel)] border border-subtle bg-canvas">
            <div className="flex items-center gap-1.5 border-b border-subtle px-3 py-2 text-[12px] font-medium uppercase tracking-wide text-secondary">
              <Lock size={13} /> Stays private, off-chain
            </div>
            <dl className="divide-y divide-[color:var(--border-subtle)]">
              {fx.RECEIPT_PRIVATE_FIELDS.map((f) => (
                <div key={f.label} className="flex justify-between gap-4 px-3 py-2 text-[13px]">
                  <dt className="text-secondary">{f.label}</dt>
                  <dd className="text-right text-primary">{f.value}</dd>
                </div>
              ))}
            </dl>
          </div>

          <div className="flex items-center justify-between gap-3 rounded-[var(--radius-panel)] border border-subtle p-3">
            <span className="flex items-center gap-2 text-[13px]">
              <Plug size={15} className={wallet === 'connected' ? 'text-success' : 'text-secondary'} />
              {wallet === 'connected' ? `Demo wallet ${fx.DEMO_WALLET}` : 'Demo wallet not connected'}
            </span>
            {wallet === 'disconnected' ? (
              <Button variant="secondary" onClick={() => setWallet('connected')}>
                Connect demo wallet
              </Button>
            ) : (
              <StatusBadge kind="verified" label="Connected" />
            )}
          </div>

          <InlineNotice kind="pending">
            Wallet addresses and transaction metadata may be publicly visible on {fx.RECEIPT_NETWORK}. Your code
            and answers stay off-chain. Public publication cannot be undone.
          </InlineNotice>

          <label className="flex items-center gap-2 text-[12px] text-secondary">
            <input type="checkbox" checked={fail} onChange={(e) => setFail(e.target.checked)} className="accent-[var(--action-primary)]" />
            Simulate issuance failure (prototype)
          </label>

          <div className="flex gap-2">
            <Button onClick={create} disabled={wallet === 'disconnected'}>
              Create receipt
            </Button>
            <Button variant="secondary" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </div>
      )}

      {step === 'issuing' && (
        <div className="space-y-4">
          <Header id="C02" title="Issuing receipt" onClose={onClose} />
          <div className="flex items-center gap-3 text-[14px]">
            <span className="bp-spin inline-block h-4 w-4 rounded-full border-2 border-action border-t-transparent" />
            Submitting to {fx.RECEIPT_NETWORK}, pending confirmation…
          </div>
          <p className="text-[12px] text-secondary">Do not resubmit — this can take a moment on a demo network.</p>
        </div>
      )}

      {step === 'confirmed' && (
        <div className="space-y-4">
          <Header id="C02" title="Receipt confirmed" onClose={onClose} />
          <InlineNotice kind="success" title="Confirmed on demo network">
            Issuer and evidence integrity can now be checked independently. This is a receipt, not a currency or
            collectible.
          </InlineNotice>
          <div className="grid gap-2 sm:grid-cols-3">
            <Button onClick={onOpenVerifier}>Open verifier</Button>
            <Button variant="secondary">Export evidence package</Button>
            <Button variant="secondary">
              View transaction <ExternalLink size={13} />
            </Button>
          </div>
        </div>
      )}

      {step === 'failed' && (
        <div className="space-y-4">
          <Header id="C02" title="We couldn’t confirm this receipt yet" onClose={onClose} />
          <InlineNotice kind="error">
            Your checkpoint is still complete. The normal AI workflow stays available regardless of receipt outcome.
          </InlineNotice>
          <div className="flex gap-2">
            <Button onClick={() => setStep('consent')}>Check status</Button>
            <Button variant="secondary" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      )}
    </Modal>
  )
}

/* ==================================================================== *
 * C03 — Independent verifier (section 5). Its own page purpose.
 * ==================================================================== */
type VerifyResult = 'valid' | 'tampered'
export function VerifierPage({ onBack }: { onBack: () => void }) {
  const [result, setResult] = useState<VerifyResult | null>(null)
  const [checking, setChecking] = useState(false)
  const run = (r: VerifyResult) => {
    setChecking(true)
    setResult(null)
    window.setTimeout(() => {
      setResult(r)
      setChecking(false)
    }, 1200)
  }

  const rows =
    result === 'valid'
      ? [
          { label: 'Network & record confirmation', state: 'match', text: `Confirmed on ${fx.RECEIPT_NETWORK}` },
          { label: 'Issuer', state: 'match', text: `Trusted issuer verified — ${fx.RECEIPT_ISSUER}` },
          { label: 'Evidence integrity', state: 'match', text: 'Evidence matches the exported package' },
          { label: 'Subject wallet', state: 'unknown', text: 'Listed; control verified only after a fresh signed challenge' },
          { label: 'Expiry', state: 'match', text: 'No expiry set' },
          { label: 'Revocation', state: 'unsupported', text: 'Revocation not supported in this prototype' },
        ]
      : [
          { label: 'Network & record confirmation', state: 'match', text: `Confirmed on ${fx.RECEIPT_NETWORK}` },
          { label: 'Issuer', state: 'unknown', text: 'Unknown issuer — not in trusted list' },
          { label: 'Evidence integrity', state: 'mismatch', text: 'Evidence mismatch — package does not match the on-chain record' },
          { label: 'Subject wallet', state: 'unknown', text: 'Listed; control not verified' },
          { label: 'Expiry', state: 'match', text: 'No expiry set' },
          { label: 'Revocation', state: 'unsupported', text: 'Revocation not supported in this prototype' },
        ]

  return (
    <div className="min-h-full bg-canvas text-primary">
      <header className="border-b border-subtle bg-panel/85 px-6 py-3 backdrop-blur">
        <div className="mx-auto flex max-w-[900px] items-center justify-between">
          <Wordmark size="sm" />
          <button onClick={onBack} className="inline-flex items-center gap-1.5 text-[13px] text-secondary hover:text-primary">
            <ArrowLeft size={16} /> Back
          </button>
        </div>
      </header>
      <main className="mx-auto max-w-[900px] space-y-6 px-6 py-8">
        <div className="space-y-1.5">
          <h1 className="text-[28px] font-semibold leading-[36px]">Verify assessment receipt</h1>
          <p className="text-[14px] text-secondary">
            Check a receipt reference and exported evidence package. Private package content is processed locally;
            it is never automatically published. Receipt integrity is separate from educational accuracy.
          </p>
        </div>

        <div className="grid gap-3 sm:grid-cols-[1fr_auto]">
          <input
            defaultValue="beprogram:receipt:devnet:7xKq…9fR2#a3f19c2"
            className="rounded-[var(--radius-control)] border border-control bg-panel px-3 py-2 font-mono text-[13px] text-primary"
            aria-label="Receipt reference"
          />
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => run('valid')} loading={checking}>
              Verify valid package
            </Button>
            <Button variant="secondary" onClick={() => run('tampered')}>
              Verify tampered package
            </Button>
          </div>
        </div>

        {checking && (
          <InlineNotice kind="pending">Verification in progress… querying the demo network.</InlineNotice>
        )}

        {result && (
          <div className="overflow-hidden rounded-[var(--radius-panel)] border border-subtle">
            {rows.map((r) => (
              <div key={r.label} className="flex items-start gap-3 border-b border-subtle px-4 py-3 last:border-0">
                <VerifyMark state={r.state} />
                <div>
                  <div className="text-[13px] font-medium">{r.label}</div>
                  <div className="text-[13px] text-secondary">{r.text}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        <p className="text-[12px] text-secondary">
          On RPC failure the verifier shows “Verification temporarily unavailable,” not “Invalid.” There is no single
          universal “verified person” badge.
        </p>
      </main>
    </div>
  )
}

function VerifyMark({ state }: { state: string }) {
  const map: Record<string, { color: string; icon: React.ReactNode }> = {
    match: { color: 'var(--status-success)', icon: <Check size={16} /> },
    mismatch: { color: 'var(--status-error)', icon: <Alert size={16} /> },
    unknown: { color: 'var(--status-attention)', icon: <Info size={16} /> },
    unsupported: { color: 'var(--text-secondary)', icon: <Info size={16} /> },
  }
  const m = map[state] ?? map.unknown
  return (
    <span className="mt-0.5 shrink-0" style={{ color: m.color }}>
      {m.icon}
    </span>
  )
}

/* ==================================================================== *
 * ReceiptCard for W02 (section 4).
 * ==================================================================== */
export function ReceiptCard({ onCreate }: { onCreate: () => void }) {
  return (
    <div className="rounded-[var(--radius-panel)] border border-subtle bg-panel p-4">
      <div className="mb-1.5 text-[12px] font-medium uppercase tracking-wide text-secondary">Assessment receipt</div>
      <p className="text-[14px] leading-[22px] text-primary">
        Create an optional record that others can check for issuer and evidence integrity.
      </p>
      <p className="mt-1 text-[13px] text-secondary">This does not independently prove skill mastery.</p>
      <div className="mt-3 flex items-center gap-3">
        <Button variant="secondary" onClick={onCreate}>
          Create verifiable receipt
        </Button>
        <span className="text-[12px] text-secondary">{fx.RECEIPT_NETWORK}</span>
      </div>
    </div>
  )
}

/* ==================================================================== *
 * GitHub — G01 PR import + G02 summary preview/publish (section 6).
 * ==================================================================== */
export function PRImportDialog({ onClose, onImport }: { onClose: () => void; onImport: () => void }) {
  return (
    <Modal onClose={onClose} wide>
      <div className="space-y-4">
        <Header id="G01" title="Import a pull request" onClose={onClose} />
        <p className="text-[13px] text-secondary">
          Connect the authorized account and select one repository and PR. CodeProof does not scan all your
          repositories.
        </p>
        <div className="space-y-2 rounded-[var(--radius-panel)] border border-subtle bg-canvas p-3 text-[13px]">
          <Row label="Account" value={`@${fx.GITHUB_ACCOUNT}`} />
          <Row label="Repository" value={fx.GITHUB_REPO} mono />
          <Row label="Pull request" value={fx.GITHUB_PR} />
          <Row label="Head commit" value={fx.GITHUB_HEAD_SHA} mono />
        </div>
        <div className="rounded-[var(--radius-panel)] border border-subtle p-3">
          <div className="mb-1.5 text-[12px] font-medium uppercase tracking-wide text-secondary">Included files</div>
          <FilePath path={fx.CURRENT_FILE} />
        </div>
        <div className="flex gap-2">
          <Button onClick={onImport}>Review this PR</Button>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
        </div>
      </div>
    </Modal>
  )
}

type PubStep = 'ready' | 'publishing' | 'published' | 'stale'
export function PRSummaryDialog({ onClose }: { onClose: () => void }) {
  const [step, setStep] = useState<PubStep>('ready')
  const publish = () => {
    setStep('publishing')
    window.setTimeout(() => setStep('published'), 1600)
  }
  return (
    <Modal onClose={onClose} wide>
      <div className="space-y-4">
        <Header id="G02" title="Prepare PR summary" onClose={onClose} />
        <div className="space-y-1 text-[13px]">
          <Row label="Repository" value={fx.GITHUB_REPO} mono />
          <Row label="Pull request" value={fx.GITHUB_PR} />
          <Row label="Head SHA" value={fx.GITHUB_HEAD_SHA} mono />
        </div>

        {step === 'stale' && (
          <InlineNotice kind="pending">This PR has new commits. Refresh the review before publishing.</InlineNotice>
        )}

        <div>
          <div className="mb-1.5 text-[12px] font-medium uppercase tracking-wide text-secondary">
            Exact comment to publish
          </div>
          <pre className="bp-scroll max-h-[220px] overflow-auto whitespace-pre-wrap rounded-[var(--radius-panel)] border border-subtle bg-canvas p-3 font-mono text-[12px] leading-5 text-primary">
            {fx.PR_SUMMARY_COMMENT}
          </pre>
          <p className="mt-1.5 text-[12px] text-secondary">
            Private answers and retry history are excluded. A passed checkpoint does not auto-publish.
          </p>
        </div>

        {step === 'published' ? (
          <InlineNotice kind="success" title="Summary published">
            <a className="text-action underline" href="#">
              github.com/{fx.GITHUB_REPO}/pull/248#issuecomment-demo
            </a>
          </InlineNotice>
        ) : (
          <div className="flex flex-wrap gap-2">
            <Button onClick={publish} loading={step === 'publishing'} disabled={step === 'stale'}>
              Publish this summary
            </Button>
            <Button variant="secondary" onClick={() => setStep(step === 'stale' ? 'ready' : 'stale')}>
              {step === 'stale' ? 'Refresh review' : 'Simulate PR changed'}
            </Button>
            <Button variant="secondary" onClick={onClose}>
              Cancel
            </Button>
          </div>
        )}
      </div>
    </Modal>
  )
}

/* ------------------------------ helpers -------------------------------- */
function Header({ id, title, onClose }: { id: string; title: string; onClose: () => void }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <div className="flex items-center gap-2">
        <span className="rounded bg-raised px-1.5 py-0.5 font-mono text-[11px] font-medium text-action">{id}</span>
        <h2 className="text-[16px] font-semibold">{title}</h2>
      </div>
      <button onClick={onClose} aria-label="Close" className="text-secondary hover:text-primary">
        <X size={18} />
      </button>
    </div>
  )
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex justify-between gap-4">
      <span className="text-secondary">{label}</span>
      <span className={`text-right text-primary ${mono ? 'font-mono' : ''}`}>{value}</span>
    </div>
  )
}
