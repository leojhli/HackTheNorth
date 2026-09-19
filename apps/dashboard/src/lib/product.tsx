import { createContext, useContext } from 'react'
import type { Checkpoint, Project, Session, Config } from './api'
import { passed, dateTime } from './api'
import type { DiffLine } from './fixture'

export function productData(project: Project | null, session: Session | null, cp: Checkpoint | null, history: Checkpoint[], config: Config | null) {
  const file = cp?.snapshot.files?.[0]
  const evaluations = cp?.attempts.filter(a => a.evaluation && (!cp.practice_started_version || a.version >= cp.practice_started_version)).map(a => a.evaluation!) || []
  const diff: DiffLine[] = file?.edits.flatMap(e => [
    ...e.removed.map(text => ({ kind: 'del' as const, text })), ...e.added.map(text => ({ kind: 'add' as const, text }))]) || []
  return { PROJECT: project?.name || 'Select a project', LANGUAGE: 'TypeScript / JavaScript',
    CURRENT_FILE: file?.path || 'Saved source', CONCEPT: cp?.question?.concept || 'Code understanding',
    CAPTURED_CODE: file?.lines.map(l => `${l.number}  ${l.text}`).join('\n') || '', CAPTURED_DIFF: diff,
    LEARNING_EXPLANATION: cp?.learning_explanation || '',
    PRACTICE_ACTIVE: !!cp?.practice_question, PRACTICE_REQUIRED: !!cp?.explanation_viewed && !cp.practice_question && !passed(cp),
    PASSED_WITH_HELP: cp?.status === 'passed_with_help',
    INITIAL_QUESTION: cp?.practice_question?.question || cp?.question?.question || '', FOLLOWUP_QUESTION: cp?.current_question || '',
    FOLLOWUP_FEEDBACK: evaluations.at(-1)?.feedback || '', SUCCESS_FEEDBACK: evaluations.at(-1)?.feedback || '',
    REASON: cp?.question?.reason || '', CAPTURED_AT: cp ? new Date(cp.created*1000).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}) : '',
    DEMONSTRATED_CONCEPTS: [...new Set(history.filter(passed).map(c => c.question?.concept || 'Understanding'))],
    INCLUDED_FILES: project?.scope || [], EXCLUDED_FILES: [{ path: '.env / secrets', reason: 'Always excluded' }, { path: 'node_modules / generated output', reason: 'Always excluded' }, ...(project?.exclusions || []).map(path => ({path, reason: 'Excluded by you'}))],
    PROVIDER_DISCLOSURE: 'Approved saved code and reviewed explanations are assessed by a model on this computer. No AI API credits or subscriptions are used. History stays in the local database; raw context expires when the retention job runs.',
    INTEGRATION_LABEL: 'CodeProof managed AI', SESSION_STARTED: session?.created || 0,
    ACCOUNT_CONNECT_HINT: 'Connect your account to keep your learning history private.',
    VOICE_ENABLED: !!config?.capabilities.voice, RECEIPTS_ENABLED: !!config?.capabilities.receipts,
    CHECKPOINT_ID: cp?.id || '', PARTIAL: !!cp?.snapshot.partial, PROVENANCE: cp?.snapshot.provenance || 'unknown',
  }
}
export const ProductContext = createContext<ReturnType<typeof productData>>(productData(null, null, null, [], null))
export const useProduct = () => useContext(ProductContext)
