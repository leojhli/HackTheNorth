import type { Phase } from '../lib/machine'

type Mood = 'idle' | 'focused' | 'working' | 'celebrate' | 'paused' | 'alert'

function presentation(phase: Phase, practiceRequired: boolean): { mood: Mood; message: string; activity: string } {
  if (phase === 'completed') return { mood: 'idle', message: 'Question closed. You can keep coding.', activity: 'Completed' }
  if (phase === 'analyzing') return { mood: 'working', message: 'I’m reading the approved code change.', activity: 'Scanning' }
  if (phase === 'evaluating' || phase === 'followup-evaluating') return { mood: 'working', message: 'I’m checking your explanation against the code.', activity: 'Thinking' }
  if (phase === 'verified') return { mood: 'celebrate', message: 'Checkpoint complete. Nice work explaining your thinking!', activity: 'Checkpoint cleared' }
  if (practiceRequired) return { mood: 'focused', message: 'Let’s try a fresh example together.', activity: 'Practice ready' }
  if (phase === 'checkpoint' || phase === 'followup') return { mood: 'focused', message: 'Take your time—explain what the code actually does.', activity: 'Listening' }
  if (phase === 'paused') return { mood: 'paused', message: 'Your checkpoint is safe. Come back when you’re ready.', activity: 'Resting' }
  if (phase === 'error') return { mood: 'alert', message: 'I kept your work. Let’s retry when the service is ready.', activity: 'Needs attention' }
  if (phase === 'disconnected') return { mood: 'alert', message: 'I’m waiting for the local backend to reconnect.', activity: 'Offline' }
  if (phase === 'scope') return { mood: 'focused', message: 'Choose the small part of your project we should review.', activity: 'Choosing scope' }
  if (phase === 'active') return { mood: 'idle', message: 'Save a meaningful change when you’re ready.', activity: 'Ready' }
  return { mood: 'idle', message: 'I’m Patch, your code-understanding companion.', activity: 'Hello' }
}

export function PatchMascot({ phase, practiceRequired = false }: { phase: Phase; practiceRequired?: boolean }) {
  const { mood, message, activity } = presentation(phase, practiceRequired)
  const mouth = mood === 'celebrate'
    ? 'M29 43 Q40 54 51 43'
    : mood === 'alert'
      ? 'M31 49 Q40 41 49 49'
      : mood === 'paused'
        ? 'M35 47 H45'
        : 'M32 45 Q40 50 48 45'
  return (
    <aside
      aria-label="Patch companion"
      aria-live="polite"
      data-mood={mood}
      className="bp-patch-strip mx-4 mt-3 flex items-center gap-3 rounded-[var(--radius-panel)] border border-subtle bg-canvas px-3 py-2.5"
    >
      <div className={`bp-patch-character bp-patch-${mood} relative shrink-0`} aria-hidden="true">
        <span className="bp-patch-orbit" />
        <span className="bp-patch-confetti bp-patch-confetti-a" />
        <span className="bp-patch-confetti bp-patch-confetti-b" />
        <span className="bp-patch-confetti bp-patch-confetti-c" />
        <svg viewBox="0 0 80 80" className="h-[58px] w-[58px] overflow-visible">
          <path className="bp-patch-arm bp-patch-arm-left" d="M19 39 C10 35 9 29 12 24" />
          <path className="bp-patch-arm bp-patch-arm-right" d="M61 39 C70 35 71 29 68 24" />
          <path className="bp-patch-body" d="M18 14 Q40 6 62 14 V38 Q62 60 40 70 Q18 60 18 38 Z" />
          <path d="M27 17 Q40 12 53 17" fill="none" stroke="var(--action-on-primary)" strokeWidth="3" strokeLinecap="round" opacity=".42" />
          <g className="bp-patch-eyes">
            <ellipse cx="32" cy="34" rx="3.6" ry="4.5" fill="var(--action-on-primary)" />
            <ellipse cx="48" cy="34" rx="3.6" ry="4.5" fill="var(--action-on-primary)" />
          </g>
          <path d={mouth} fill="none" stroke="var(--action-on-primary)" strokeWidth="3" strokeLinecap="round" />
          <path d="M35 59 L39 63 L47 55" fill="none" stroke="var(--action-on-primary)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" opacity=".72" />
        </svg>
      </div>
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
          <span className="text-[13px] font-semibold text-primary">Patch</span>
          <span className="rounded-full bg-raised px-2 py-0.5 font-mono text-[10px] text-secondary">{activity}</span>
        </div>
        <p className="mt-0.5 text-[12px] leading-[18px] text-secondary">{message}</p>
      </div>
    </aside>
  )
}
