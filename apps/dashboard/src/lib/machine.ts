// Shared product state model (section 10). Connection state and checkpoint
// state are SEPARATE properties — never collapsed into one ambiguous badge.

export type Phase =
  | 'welcome' // E01
  | 'scope' // E02
  | 'active' // E03
  | 'analyzing' // E04
  | 'checkpoint' // E05 (initial question)
  | 'evaluating' // E06
  | 'followup' // E07
  | 'followup-evaluating' // E06 for the follow-up
  | 'verified' // E08
  | 'paused' // E10 (checkpoint paused)
  | 'error' // E11
  | 'disconnected' // E12

export type ConnKind = 'connected' | 'reconnecting' | 'disconnected'
export type IntegrationKind = 'native' | 'managed' | 'simulated'

// Reconciled gate state (section 16): whether the next connected AI request runs.
export type GateState = 'available' | 'paused' | 'pending'

export type ErrorVariant = 'evaluation' | 'saving'

export type ExtensionState = {
  phase: Phase
  connection: ConnKind
  integration: IntegrationKind
  gate: GateState
  accountConnected: boolean
  initialDraft: string
  followupDraft: string
  errorVariant: ErrorVariant
  // Shows the E09 "next AI request paused" notice inside the active editor.
  showPausedRequestNotice: boolean
  // True once the checkpoint result is persisted to history.
  passed: boolean
}

export const initialExtensionState: ExtensionState = {
  phase: 'welcome',
  connection: 'connected',
  integration: 'managed',
  gate: 'available',
  accountConnected: false,
  initialDraft: '',
  followupDraft: '',
  errorVariant: 'evaluation',
  showPausedRequestNotice: false,
  passed: false,
}
