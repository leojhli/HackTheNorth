import { useState } from 'react'
import type { Project } from '../lib/api'
import { Button, InlineNotice, Modal } from './ui'

export function ProjectsPage({ projects, activeId, busy, onCreate, onDelete }: {
  projects: Project[]; activeId?: string; busy: boolean;
  onCreate: () => void; onDelete: (project: Project) => Promise<boolean>;
}) {
  const [target, setTarget] = useState<Project | null>(null)
  const [failed, setFailed] = useState(false)
  return <section className="mx-auto max-w-[860px] space-y-5">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div><h1 className="text-[28px] font-semibold">Manage projects</h1>
        <p className="mt-1 text-[14px] text-secondary">Your saved CodeProof projects and learning history.</p></div>
      <Button disabled={busy} onClick={onCreate}>New project</Button>
    </div>
    <InlineNotice kind="info">Projects organize your learning history. Creating or deleting one here does not create or delete folders on your computer.</InlineNotice>
    {!projects.length && <p className="rounded-[var(--radius-panel)] border border-subtle bg-panel p-6 text-secondary">No projects yet. Create one to get started.</p>}
    <div className="space-y-3">{projects.map(project => <article key={project.id} aria-label={project.name} className="flex flex-wrap items-center justify-between gap-4 rounded-[var(--radius-panel)] border border-subtle bg-panel p-5">
      <div className="min-w-0 flex-1"><h2 className="break-words text-[16px] font-semibold">{project.name}</h2>
        <p className="mt-1 break-words text-[13px] text-secondary">Included paths: {project.scope.join(', ')}</p>
        {activeId === project.id && <p className="mt-1 text-[12px] text-secondary">Session active</p>}
      </div>
      <Button variant="destructive" disabled={busy} onClick={() => { setFailed(false); setTarget(project) }}>Delete project</Button>
    </article>)}</div>
    {target && <Modal onClose={() => { if (!busy) setTarget(null) }}>
      <h2 className="break-words text-[20px] font-semibold">Delete {target.name}?</h2>
      <p className="my-4 text-[14px] leading-6 text-secondary">This permanently removes this project's saved sessions, questions, answers, and learning history from CodeProof. Any active session for this project will end. Your code files and folders stay on your computer.</p>
      {failed && <div role="alert" className="mb-4"><InlineNotice kind="error">Could not confirm deletion. Cancel to check the error message, or retry.</InlineNotice></div>}
      <div className="flex flex-wrap gap-3"><Button variant="secondary" disabled={busy} onClick={() => setTarget(null)}>Cancel</Button>
        <Button variant="destructive" loading={busy} onClick={async () => { setFailed(false); if (await onDelete(target)) setTarget(null); else setFailed(true) }}>Permanently delete project</Button></div>
    </Modal>}
  </section>
}
