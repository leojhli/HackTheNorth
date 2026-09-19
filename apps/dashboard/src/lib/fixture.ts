// Canonical demo content (section 12). One source of truth so questions,
// answers, counters, and history always agree across surfaces.

export const PROJECT = 'campus-events'
export const LANGUAGE = 'TypeScript'
export const SESSION_DATE = '18 September 2026'
export const CURRENT_FILE = 'src/data/findUser.ts'
export const CONCEPT = 'SQL parameterization'
export const INTEGRATION_LABEL = 'CodeProof AI connected'

export const CAPTURED_CODE = `export async function findUser(email: string) {
  const result = await pool.query(
    'SELECT id, name FROM users WHERE email = $1',
    [email]
  );
  return result.rows[0] ?? null;
}`

// Diff view: the parameterized query replaced a string-concatenated one.
export type DiffLine = { kind: 'context' | 'add' | 'del'; text: string }
export const CAPTURED_DIFF: DiffLine[] = [
  { kind: 'context', text: 'export async function findUser(email: string) {' },
  { kind: 'del', text: '  const result = await pool.query(' },
  { kind: 'del', text: "    `SELECT id, name FROM users WHERE email = '${email}'`" },
  { kind: 'del', text: '  );' },
  { kind: 'add', text: '  const result = await pool.query(' },
  { kind: 'add', text: "    'SELECT id, name FROM users WHERE email = $1'," },
  { kind: 'add', text: '    [email]' },
  { kind: 'add', text: '  );' },
  { kind: 'context', text: '  return result.rows[0] ?? null;' },
  { kind: 'context', text: '}' },
]

export const INITIAL_QUESTION =
  'Why does this query pass `email` separately instead of inserting it directly into the SQL string?'

export const WEAK_ANSWER = 'It makes the database safer.'

export const FOLLOWUP_FEEDBACK =
  'You identified the security goal. Explain how the query keeps the input separate from SQL instructions.'

export const FOLLOWUP_QUESTION =
  'What role does `$1` play, and how is the value in `[email]` handled?'

export const PASSING_ANSWER =
  'The SQL text contains a placeholder, and the email is supplied separately as the value for that placeholder. The database treats that value as data rather than part of the SQL instructions, so it cannot change the query’s structure.'

export const SUCCESS_FEEDBACK =
  'You explained how parameter binding separates user input from SQL instructions.'

export type HistoryStatus = 'demonstrated' | 'needs-explanation'
export type HistoryRow = {
  file: string
  concept: string
  status: HistoryStatus
  time: string
  // Evidence, only populated for the demoable checkpoint.
  hasEvidence?: boolean
}

// Before the current checkpoint passes (section 12 fixtures).
export const HISTORY_BEFORE: HistoryRow[] = [
  { file: 'src/services/events.ts', concept: 'Async error handling', status: 'demonstrated', time: '2:10 PM' },
  { file: 'src/utils/parseEvent.ts', concept: 'Input validation', status: 'demonstrated', time: '2:18 PM' },
  { file: CURRENT_FILE, concept: CONCEPT, status: 'needs-explanation', time: '2:24 PM', hasEvidence: true },
]

// After it passes.
export const HISTORY_AFTER: HistoryRow[] = [
  { file: 'src/services/events.ts', concept: 'Async error handling', status: 'demonstrated', time: '2:10 PM' },
  { file: 'src/utils/parseEvent.ts', concept: 'Input validation', status: 'demonstrated', time: '2:18 PM' },
  { file: CURRENT_FILE, concept: CONCEPT, status: 'demonstrated', time: '2:26 PM', hasEvidence: true },
]

export const DEMONSTRATED_CONCEPTS = ['Async error handling', 'Input validation']

export const INCLUDED_FILES = [
  'src/data/findUser.ts',
  'src/services/events.ts',
  'src/utils/parseEvent.ts',
  'src/components/EventCard.tsx',
]
export const EXCLUDED_FILES = [
  { path: '.env', reason: 'Secrets' },
  { path: 'dist/', reason: 'Generated output' },
  { path: 'node_modules/', reason: 'Dependencies' },
  { path: 'src/legacy/import.ts', reason: 'Excluded by you' },
]

export const PROVIDER_DISCLOSURE =
  'Selected code excerpts and your explanations are sent to the configured AI service for review. Your history is private.'

/* ------------------------------------------------------------------ *
 * v3 delta fixtures (assessment receipt, GitHub PR, connected services).
 * Illustrative UI content only — not a claim of on-chain issuance.
 * ------------------------------------------------------------------ */
export const RECEIPT_NETWORK = 'Solana Devnet · Demo network'
export const RECEIPT_ISSUER = 'CodeProof (issuer.beprogram.dev)'
export const DEMO_WALLET = '7xKq…9fR2'
export const ASSISTANCE_LEVEL = 'Unaided explanation'

// Public vs private field split shown on the consent screen (C01, section 5).
export const RECEIPT_PUBLIC_FIELDS = [
  { label: 'Concept', value: CONCEPT },
  { label: 'Checkpoint time', value: '18 Sep 2026, 2:26 PM' },
  { label: 'Assistance level', value: ASSISTANCE_LEVEL },
  { label: 'Issuer', value: RECEIPT_ISSUER },
  { label: 'Network', value: RECEIPT_NETWORK },
]
export const RECEIPT_PRIVATE_FIELDS = [
  { label: 'Captured code', value: `${CURRENT_FILE} (kept off-chain)` },
  { label: 'Your explanations', value: 'Initial answer, follow-up answer (kept off-chain)' },
]

export const GITHUB_REPO = 'campus-collective/campus-events'
export const GITHUB_PR = '#248 · Parameterize user lookup query'
export const GITHUB_HEAD_SHA = 'a3f19c2'
export const GITHUB_ACCOUNT = 'ada-reyes'

// Exact comment previewed before publication (G02, section 6).
export const PR_SUMMARY_COMMENT = `### CodeProof comprehension summary

Concepts demonstrated on this PR:
- **SQL parameterization** — findUser now separates input from SQL instructions.

Coverage: 1 checkpoint on the changed data-access file. Private answers and retry history are excluded.

_Evidence receipt (optional): issuer + integrity checkable. This does not independently prove skill mastery._`
