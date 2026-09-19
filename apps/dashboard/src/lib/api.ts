export type Config = { ai?: {available:boolean;provider:string;model:string;message:string}; cost_mode?:string; auth_mode: 'supabase' | 'local'; supabase_url: string; supabase_publishable_key: string; capabilities: { assessment: boolean; managed_ai: boolean; voice: boolean; receipts: boolean; github: boolean } }
export type Project = { id: string; name: string; scope: string[]; exclusions: string[]; scope_hash: string }
export type Session = { id: string; project_id: string; status: string; created: number }
export type Evaluation = { model?: string; decision: 'pass' | 'follow_up' | 'unable_to_assess'; feedback: string; next_question: string | null; gaps: string[] }
export type Attempt = { id: string; key: string; answer: string; modality: string; state: string; evaluation: Evaluation | null; version: number }
export type SourceFile = { path: string; edits: { before_start: number; after_start: number; removed: string[]; added: string[] }[]; lines: { number: number; text: string }[] }
export type CheckpointQuestion = { decision: string; concept: string; question: string; reason: string; rubric: string[] }
export type Checkpoint = { explanation_viewed?: boolean; learning_explanation?: string | null; id: string; project_id: string; session_id: string; status: string; version: number; snapshot_hash: string;
  snapshot: { files: SourceFile[]; partial: boolean; provenance: string; pr_import_id?: string; expired?: boolean };
  question: CheckpointQuestion | null; current_question: string | null;
  practice_question?: CheckpointQuestion | null; practice_started_version?: number | null;
  attempts: Attempt[]; created: number; passed_at: number | null; model: string; last_error: string | null; can_pause: boolean }
export type Gate = { available: boolean; checkpoint_id: string | null; reason: string }

let bearer = ''
export function setToken(value: string) { bearer = value }
export class ApiError extends Error { constructor(public code: string, message: string, public retryable: boolean) { super(message) } }
export async function api<T = any>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const form = body instanceof FormData
  const response = await fetch(path, { method, headers: { ...(bearer ? { Authorization: `Bearer ${bearer}` } : {}), ...(!form && body !== undefined ? { 'Content-Type': 'application/json' } : {}) },
    body: body === undefined ? undefined : form ? body : JSON.stringify(body), signal: AbortSignal.timeout(135000) })
  if (!response.ok) { const error = await response.json().catch(() => ({})); throw new ApiError(error.code || 'unavailable', error.message || 'The request failed. Refresh to reconcile saved state.', !!error.retryable) }
  if (response.headers.get('Content-Type')?.startsWith('audio/')) return await response.blob() as T
  return await response.json() as T
}
export const passed = (c: Checkpoint) => ['passed', 'passed_with_help'].includes(c.status)
export const dateTime = (value: number) => new Date(value * 1000).toLocaleString()
