// Presentation context only — the host IDE. Labeled "Host application — not
// part of CodeProof implementation" (section 5). Developers build the panel,
// not the editor.
import type { ReactNode } from 'react'
import { File, Search, Settings, Sparkle } from '../lib/icons'
import * as fx from '../lib/fixture'

const CODE_LINES = fx.CAPTURED_CODE.split('\n')

export function VSCodeShell({ panel, onAiRequest }: { panel: ReactNode; onAiRequest: () => void }) {
  return (
    <div className="flex h-full flex-col overflow-hidden rounded-[var(--radius-dialog)] border border-subtle bg-canvas text-primary">
      {/* Title bar */}
      <div className="flex h-9 shrink-0 items-center gap-2 border-b border-subtle bg-panel px-3">
        <span className="flex gap-1.5">
          <i className="h-3 w-3 rounded-full bg-[#ff5f57]" />
          <i className="h-3 w-3 rounded-full bg-[#febc2e]" />
          <i className="h-3 w-3 rounded-full bg-[#28c840]" />
        </span>
        <span className="mx-auto font-mono text-[12px] text-secondary">
          {fx.PROJECT} — {fx.CURRENT_FILE}
        </span>
      </div>

      <div className="flex min-h-0 flex-1">
        {/* Activity bar */}
        <nav className="hidden w-11 shrink-0 flex-col items-center gap-4 border-r border-subtle bg-panel py-3 text-secondary sm:flex">
          <File size={20} className="text-primary" />
          <Search size={20} />
          <Sparkle size={20} className="text-action" />
          <Settings size={20} className="mt-auto" />
        </nav>

        {/* Explorer */}
        <aside className="hidden w-48 shrink-0 flex-col border-r border-subtle bg-panel/60 lg:flex">
          <div className="px-3 py-2 text-[11px] font-medium uppercase tracking-wide text-secondary">Explorer</div>
          <ul className="px-1 text-[13px]">
            {['src/data/findUser.ts', 'src/services/events.ts', 'src/utils/parseEvent.ts', 'src/components/EventCard.tsx'].map(
              (f) => {
                const name = f.split('/').pop()
                const active = f === fx.CURRENT_FILE
                return (
                  <li
                    key={f}
                    className={`flex items-center gap-1.5 rounded px-2 py-1 ${
                      active ? 'bg-raised text-primary' : 'text-secondary'
                    }`}
                  >
                    <File size={14} /> {name}
                  </li>
                )
              },
            )}
          </ul>
        </aside>

        {/* Editor */}
        <div className="flex min-w-0 flex-1 flex-col">
          <div className="flex h-9 shrink-0 items-center border-b border-subtle bg-panel/40">
            <span className="flex h-full items-center gap-1.5 border-r border-subtle bg-canvas px-3 text-[13px]">
              <File size={13} className="text-action" /> findUser.ts
            </span>
          </div>
          <div className="bp-scroll relative min-h-0 flex-1 overflow-auto p-3">
            <pre className="font-mono text-[13px] leading-5">
              {CODE_LINES.map((line, i) => (
                <div key={i} className="flex">
                  <span className="w-8 shrink-0 select-none pr-3 text-right text-secondary/60">{i + 1}</span>
                  <code className="whitespace-pre text-secondary">{line}</code>
                </div>
              ))}
            </pre>
            {/* Managed "Ask AI" composer with a paused send action (section 8). */}
            <div className="mt-6 max-w-[420px] rounded-[var(--radius-panel)] border border-subtle bg-panel p-3">
              <div className="mb-2 flex items-center gap-1.5 text-[12px] font-medium text-secondary">
                <Sparkle size={13} className="text-action" /> Ask AI · {fx.INTEGRATION_LABEL}
              </div>
              <div className="flex items-center gap-2">
                <input
                  readOnly
                  value="Refactor findUser to add pagination"
                  className="min-w-0 flex-1 rounded-[var(--radius-control)] border border-control bg-canvas px-2.5 py-1.5 font-sans text-[13px] text-primary"
                />
                <button
                  onClick={onAiRequest}
                  className="rounded-[var(--radius-control)] bg-action px-3 py-1.5 text-[13px] font-medium text-on-action hover:brightness-110"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
          {/* Status bar — inherits host character; reads CodeProof state. */}
          <div className="flex h-6 shrink-0 items-center gap-3 border-t border-subtle bg-action px-3 text-[11px] font-medium text-on-action">
            <span>main*</span>
            <span className="ml-auto font-mono">TypeScript</span>
          </div>
        </div>

        {/* Docked CodeProof panel */}
        <div className="hidden w-[420px] shrink-0 border-l border-subtle xl:block">{panel}</div>
      </div>
    </div>
  )
}
