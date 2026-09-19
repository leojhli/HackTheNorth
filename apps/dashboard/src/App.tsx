import { useEffect, useReducer, useRef, useState } from 'react'
import { ExtensionPanel, type ExtActions } from './components/ExtensionPanel'
import { VSCodeShell } from './components/VSCodeShell'
import { Website } from './components/Website'
import { ReceiptFlow, VerifierPage, PRImportDialog, PRSummaryDialog } from './components/v3'
import { Button, Wordmark } from './components/ui'
import { initialExtensionState, type ExtensionState, type Phase } from './lib/machine'
import { Sparkle, X, Check, Plug, Sun, Moon } from './lib/icons'
import * as fx from './lib/fixture'

type Surface = 'ide' | 'panel' | 'web' | 'verifier'
type Flow = 'core' | 'setup' | 'recovery' | 'voice' | 'receipt' | 'pr'

// A few extra orchestration fields layered on ExtensionState.
type S = ExtensionState & {
  stage: 'initial' | 'followup' // which checkpoint question is active
  pausedFrom: Phase // where a pause was triggered from, for Resume
  simulateFail: boolean // next evaluation returns an operational error (E11)
}
type Action =
  | { type: 'patch'; patch: Partial<S> }
  | { type: 'reset' }

const init: S = { ...initialExtensionState, stage: 'initial', pausedFrom: 'checkpoint', simulateFail: false }

function reducer(s: S, a: Action): S {
  if (a.type === 'reset') return init
  return { ...s, ...a.patch }
}

export default function App() {
  const [dark, setDark] = useState(true)
  const [surface, setSurface] = useState<Surface>('ide')
  const [s, dispatch] = useReducer(reducer, init)
  const [toast, setToast] = useState<{ icon: 'check' | 'plug'; text: string } | null>(null)
  const [aiPaused, setAiPaused] = useState(false)
  const [confirmEnd, setConfirmEnd] = useState(false)
  const [receiptOpen, setReceiptOpen] = useState(false)
  const [prImportOpen, setPrImportOpen] = useState(false)
  const [prSummaryOpen, setPrSummaryOpen] = useState(false)
  const timers = useRef<number[]>([])

  const set = (patch: Partial<S>) => dispatch({ type: 'patch', patch })
  const later = (ms: number, fn: () => void) => {
    const id = window.setTimeout(fn, ms)
    timers.current.push(id)
  }
  useEffect(() => () => timers.current.forEach(clearTimeout), [])

  const showToast = (icon: 'check' | 'plug', text: string) => {
    setToast({ icon, text })
    later(3200, () => setToast(null))
  }

  const unresolved =
    s.gate === 'paused' ||
    ['checkpoint', 'evaluating', 'followup', 'followup-evaluating', 'paused', 'error'].includes(s.phase)

  const a: ExtActions = {
    connectAccount: () => {
      showToast('check', 'Opening browser sign-in…')
      later(900, () => {
        set({ accountConnected: true })
        showToast('check', 'Account connected')
      })
    },
    continueSetup: () => set({ phase: 'scope' }),
    startSession: () => set({ phase: 'active' }),
    cancelSetup: () => set({ phase: 'welcome' }),

    // E03 → E04 → checkpoint-available (core demo entry via managed AI request).
    triggerAiRequest: () => {
      if (unresolved) {
        setAiPaused(true)
        return
      }
      set({ gate: 'pending', phase: 'analyzing', showPausedRequestNotice: false })
      later(1600, () => {
        set({ phase: 'active', gate: 'paused', showPausedRequestNotice: true, stage: 'initial' })
        showToast('plug', 'Checkpoint available')
      })
    },
    // E03 primary: manual review → analysis → E05.
    reviewChanges: () => {
      set({ phase: 'analyzing', gate: 'paused', stage: 'initial' })
      later(1500, () => set({ phase: 'checkpoint' }))
    },
    openCheckpoint: () => {
      setAiPaused(false)
      set({ phase: s.stage === 'followup' ? 'followup' : 'checkpoint', showPausedRequestNotice: false })
    },
    keepEditing: () => {
      setAiPaused(false)
      set({ phase: 'active', showPausedRequestNotice: false })
    },

    submitInitial: () => {
      set({ phase: 'evaluating' })
      later(1600, () => {
        if (s.simulateFail) {
          set({ phase: 'error', errorVariant: 'evaluation' })
          return
        }
        // Direct-pass branch: a complete, specific initial explanation can pass.
        const strong =
          s.initialDraft.trim().length > 90 &&
          /(placeholder|separate|binding|data|instruction)/i.test(s.initialDraft)
        if (strong) {
          passAndPersist()
        } else {
          set({ phase: 'followup', stage: 'followup' })
        }
      })
    },
    submitFollowup: () => {
      set({ phase: 'followup-evaluating' })
      later(1600, () => {
        if (s.simulateFail) {
          set({ phase: 'error', errorVariant: 'evaluation' })
          return
        }
        passAndPersist()
      })
    },
    continueCoding: () => set({ phase: 'active', showPausedRequestNotice: false }),

    pauseCheckpoint: () =>
      set({ phase: 'paused', pausedFrom: s.stage === 'followup' ? 'followup' : 'checkpoint' }),
    resumeCheckpoint: () => set({ phase: s.pausedFrom }),
    endSession: () => setConfirmEnd(true),

    retry: () => {
      // Re-run the evaluation that failed; clear the injected failure.
      const from = s.stage === 'followup' ? 'followup-evaluating' : 'evaluating'
      set({ phase: from, simulateFail: false })
      later(1400, () => {
        if (s.stage === 'followup') passAndPersist()
        else set({ phase: 'followup', stage: 'followup' })
      })
    },
    reconnect: () => {
      set({ connection: 'reconnecting' })
      showToast('plug', 'Reconnecting to coding assistant…')
      later(1400, () => {
        set({ connection: 'connected', phase: s.stage === 'followup' ? 'followup' : 'checkpoint' })
        showToast('check', 'Connection restored')
      })
    },

    setInitialDraft: (v) => set({ initialDraft: v }),
    setFollowupDraft: (v) => set({ followupDraft: v }),
    openHistory: () => setSurface('web'),
    openSettings: () => setSurface('web'),
    createReceipt: () => setReceiptOpen(true),
  }

  // E08 persistence: verified first with gate pending, then reconciled available.
  function passAndPersist() {
    set({ phase: 'verified', gate: 'pending' })
    later(1000, () => {
      set({ gate: 'available', passed: true })
      showToast('check', 'Connected AI assistance available')
    })
  }

  const panel = <ExtensionPanel s={s} a={a} />

  return (
    <div className={dark ? 'dark' : 'light'}>
      <div className="flex min-h-screen flex-col bg-canvas text-primary">
        <ControlRail
          surface={surface}
          setSurface={setSurface}
          dark={dark}
          setDark={setDark}
          onFlow={(flow) => {
            timers.current.forEach(clearTimeout)
            timers.current = []
            setAiPaused(false)
            setConfirmEnd(false)
            setReceiptOpen(false)
            setPrImportOpen(false)
            setPrSummaryOpen(false)
            if (flow === 'core') {
              dispatch({ type: 'patch', patch: { ...init, accountConnected: true, phase: 'active' } })
              setSurface('ide')
            } else if (flow === 'setup') {
              dispatch({ type: 'reset' })
              setSurface('ide')
            } else if (flow === 'recovery') {
              // land in the checkpoint with a drafted weak answer + fail armed
              dispatch({
                type: 'patch',
                patch: {
                  ...init,
                  accountConnected: true,
                  phase: 'checkpoint',
                  gate: 'paused',
                  initialDraft: fx.WEAK_ANSWER,
                  simulateFail: true,
                },
              })
              setSurface('panel')
            } else if (flow === 'voice') {
              // E07 with a weak initial answer recorded; try Listen/Record here.
              dispatch({
                type: 'patch',
                patch: {
                  ...init,
                  accountConnected: true,
                  phase: 'followup',
                  stage: 'followup',
                  gate: 'paused',
                  initialDraft: fx.WEAK_ANSWER,
                },
              })
              setSurface('panel')
            } else if (flow === 'receipt') {
              // Receipt branch begins from a passed checkpoint on W02.
              dispatch({ type: 'patch', patch: { ...init, accountConnected: true, phase: 'active', passed: true } })
              setSurface('web')
              setReceiptOpen(true)
            } else if (flow === 'pr') {
              dispatch({ type: 'patch', patch: { ...init, accountConnected: true, phase: 'active' } })
              setSurface('ide')
              setPrImportOpen(true)
            }
          }}
          onArmFail={() => set({ simulateFail: !s.simulateFail })}
          armed={s.simulateFail}
          onDisconnect={() => {
            set({ connection: 'disconnected', phase: 'disconnected', stage: s.stage })
            setSurface(surface === 'web' ? 'panel' : surface)
          }}
        />

        <main className="flex-1 p-3 sm:p-5">
          {surface === 'ide' && (
            <div className="mx-auto h-[calc(100vh-136px)] max-w-[1440px]">
              <VSCodeShell panel={panel} onAiRequest={a.triggerAiRequest} />
              <p className="mt-2 text-center font-mono text-[11px] text-secondary">
                Host application — not part of BeProgram implementation
              </p>
            </div>
          )}

          {surface === 'panel' && (
            <div className="mx-auto flex max-w-[880px] flex-col items-center gap-3">
              <div className="h-[calc(100vh-160px)] w-full max-w-[860px] overflow-hidden rounded-[var(--radius-dialog)] border border-subtle shadow-2xl">
                {panel}
              </div>
              <p className="font-mono text-[11px] text-secondary">
                Extension editor panel — resize the window to see the ≥720px side-by-side and compact stacked layouts
              </p>
            </div>
          )}

          {surface === 'web' && (
            <div className="mx-auto max-w-[1200px] overflow-hidden rounded-[var(--radius-dialog)] border border-subtle">
              <Website
                passed={s.passed}
                onOpenVSCode={() => setSurface('ide')}
                cb={{
                  onCreateReceipt: () => setReceiptOpen(true),
                  onPreparePR: () => setPrSummaryOpen(true),
                  onImportPR: () => setPrImportOpen(true),
                }}
              />
            </div>
          )}

          {surface === 'verifier' && (
            <div className="mx-auto max-w-[1200px] overflow-hidden rounded-[var(--radius-dialog)] border border-subtle">
              <VerifierPage onBack={() => setSurface('web')} />
            </div>
          )}
        </main>

        {/* Toast (section 11) */}
        {toast && (
          <div className="bp-enter fixed bottom-5 left-1/2 z-50 -translate-x-1/2">
            <div className="flex items-center gap-2.5 rounded-[var(--radius-panel)] border border-subtle bg-panel px-4 py-2.5 text-[13px] shadow-2xl">
              <span className={toast.icon === 'check' ? 'text-success' : 'text-info'}>
                {toast.icon === 'check' ? <Check size={16} /> : <Plug size={16} />}
              </span>
              {toast.text}
              <button onClick={() => setToast(null)} className="ml-1 text-secondary hover:text-primary">
                <X size={14} />
              </button>
            </div>
          </div>
        )}

        {/* E09 — Next AI request paused (BeProgram-owned modal, no IDE padlock) */}
        {aiPaused && (
          <Overlay onClose={a.keepEditing}>
            <div className="flex items-center gap-2">
              <Plug size={18} className="text-attention" />
              <h2 className="text-[16px] font-semibold">Explain this change to continue</h2>
            </div>
            <p className="mt-2 text-[13px] leading-5 text-secondary">
              Your next connected AI request is paused until you explain{' '}
              <span className="text-primary">{fx.CONCEPT}</span> in{' '}
              <span className="font-mono text-primary">{fx.CURRENT_FILE}</span>. Editing, saving, and tests
              stay available.
            </p>
            <div className="mt-4 flex gap-2">
              <Button onClick={a.openCheckpoint}>Open checkpoint</Button>
              <Button variant="secondary" onClick={a.keepEditing}>
                Keep editing
              </Button>
            </div>
          </Overlay>
        )}

        {/* v3 — Assessment receipt flow (C01/C02) */}
        {receiptOpen && (
          <ReceiptFlow
            onClose={() => setReceiptOpen(false)}
            onOpenVerifier={() => {
              setReceiptOpen(false)
              setSurface('verifier')
            }}
          />
        )}

        {/* v3 — GitHub PR import (G01) */}
        {prImportOpen && (
          <PRImportDialog
            onClose={() => setPrImportOpen(false)}
            onImport={() => {
              setPrImportOpen(false)
              set({ phase: 'checkpoint', gate: 'paused', stage: 'initial' })
              setSurface('panel')
              showToast('check', 'PR imported — checkpoint ready')
            }}
          />
        )}

        {/* v3 — GitHub PR summary preview + publish (G02) */}
        {prSummaryOpen && <PRSummaryDialog onClose={() => setPrSummaryOpen(false)} />}

        {/* E10 — End session confirmation */}
        {confirmEnd && (
          <Overlay onClose={() => setConfirmEnd(false)}>
            <h2 className="text-[16px] font-semibold">End this session?</h2>
            <p className="mt-2 text-[13px] leading-5 text-secondary">
              Your history will be saved. This checkpoint will remain unresolved.
            </p>
            <div className="mt-4 flex gap-2">
              <Button
                variant="destructive"
                onClick={() => {
                  setConfirmEnd(false)
                  set({ phase: 'welcome', gate: 'available', showPausedRequestNotice: false })
                }}
              >
                End session
              </Button>
              <Button variant="secondary" onClick={() => setConfirmEnd(false)}>
                Keep session open
              </Button>
            </div>
          </Overlay>
        )}
      </div>
    </div>
  )
}

/* ------------------------------ Control rail --------------------------- */
function ControlRail({
  surface,
  setSurface,
  dark,
  setDark,
  onFlow,
  onArmFail,
  armed,
  onDisconnect,
}: {
  surface: Surface
  setSurface: (s: Surface) => void
  dark: boolean
  setDark: (d: boolean) => void
  onFlow: (f: Flow) => void
  onArmFail: () => void
  armed: boolean
  onDisconnect: () => void
}) {
  const surfaces: { id: Surface; label: string }[] = [
    { id: 'ide', label: 'VS Code demo' },
    { id: 'panel', label: 'Extension panel' },
    { id: 'web', label: 'Website' },
  ]
  return (
    <header className="sticky top-0 z-40 border-b border-subtle bg-panel/85 px-4 py-2.5 backdrop-blur">
      <div className="mx-auto flex max-w-[1440px] flex-wrap items-center gap-x-4 gap-y-2">
        <Wordmark size="sm" />
        <span className="hidden font-mono text-[11px] text-secondary sm:inline">Prototype</span>

        <div className="flex items-center gap-1 rounded-full bg-canvas p-0.5">
          {surfaces.map((sf) => (
            <button
              key={sf.id}
              onClick={() => setSurface(sf.id)}
              className={`rounded-full px-3 py-1 text-[12px] transition-colors ${
                surface === sf.id ? 'bg-action text-on-action' : 'text-secondary hover:text-primary'
              }`}
            >
              {sf.label}
            </button>
          ))}
        </div>

        <div className="ml-auto flex flex-wrap items-center gap-1.5">
          <span className="hidden font-mono text-[11px] text-secondary md:inline">Flows:</span>
          <RailBtn onClick={() => onFlow('core')}>
            <Sparkle size={13} /> Core demo
          </RailBtn>
          <RailBtn onClick={() => onFlow('setup')}>Setup</RailBtn>
          <RailBtn onClick={() => onFlow('recovery')}>Recovery</RailBtn>
          <RailBtn onClick={() => onFlow('voice')}>Voice</RailBtn>
          <RailBtn onClick={() => onFlow('receipt')}>Receipt</RailBtn>
          <RailBtn onClick={() => onFlow('pr')}>PR</RailBtn>

          <span className="mx-1 hidden h-4 w-px bg-subtle md:inline-block" />
          <RailBtn onClick={onArmFail} active={armed}>
            {armed ? 'Fail armed' : 'Arm error'}
          </RailBtn>
          <RailBtn onClick={onDisconnect}>Disconnect</RailBtn>

          <button
            onClick={() => setDark(!dark)}
            aria-label="Toggle theme"
            className="ml-1 flex h-7 w-7 items-center justify-center rounded-full border border-subtle text-secondary hover:text-primary"
          >
            {dark ? <Sun size={15} /> : <Moon size={15} />}
          </button>
        </div>
      </div>
    </header>
  )
}

function RailBtn({
  children,
  onClick,
  active,
}: {
  children: React.ReactNode
  onClick: () => void
  active?: boolean
}) {
  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[12px] transition-colors ${
        active
          ? 'border-transparent bg-attention/20 text-attention'
          : 'border-subtle text-secondary hover:bg-raised hover:text-primary'
      }`}
    >
      {children}
    </button>
  )
}

function Overlay({ children, onClose }: { children: React.ReactNode; onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
      role="presentation"
    >
      <div
        role="dialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
        className="bp-enter w-full max-w-[420px] rounded-[var(--radius-dialog)] border border-subtle bg-panel p-5 shadow-2xl"
      >
        {children}
      </div>
    </div>
  )
}
