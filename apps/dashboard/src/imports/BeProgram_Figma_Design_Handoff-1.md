# BeProgram Figma UI Design Handoff

**Version:** 1.0  
**Date:** 18 September 2026  
**Source of truth:** BeProgram `PRD.md`, version 2.0  
**Deliverable:** Editable interface designs, reusable components, and a clickable prototype  
**Primary surface:** VS Code extension  
**Secondary surface:** A small learning-history website

## 1. Design assignment

Design the complete UI for **BeProgram**, a developer tool that helps programmers understand the code they build with AI. Meaningful code changes trigger contextual questions. A weak explanation receives a targeted follow-up. When the programmer demonstrates understanding, the next connected AI request becomes available and their learning history updates.

Make this sequence immediately understandable:

**Code changes → checkpoint → explanation → follow-up → understanding verified → continue coding → learning history.**

The design should feel credible inside a working developer’s editor: focused, restrained, technically literate, and easy to read. Its strongest visual moment is the transition from an unresolved question to clear evidence of understanding.

Use this brief as the detailed design specification and the PRD for product behavior. The proposed tokens, layouts, and frame dimensions here are design decisions, not previously validated user preferences.

### Required design outputs

1. A coherent visual system and reusable component library.
2. High-fidelity P0 screens for the extension and dashboard.
3. Loading, empty, error, paused, and connection states as component variants or frames.
4. A clickable prototype of the full hackathon demonstration.
5. Responsive versions of the checkpoint panel and learning-history page.
6. Clearly separated P1/P2 concepts, only after P0 is complete.
7. Developer annotations covering state transitions, spacing, responsive rules, and accessible behavior.

Do not turn the assignment into a landing-page-only design, generic chatbot, social network, or enterprise analytics dashboard. A marketing site, pricing page, and billing UI are outside this request’s product scope.

## 2. Product behavior that the design must preserve

- The extension is the main experience. The browser dashboard supports reflection and evidence review.
- Checkpoints follow meaningful changes; not every AI request or small edit requires a question.
- Questions refer to the user’s actual captured code.
- Only the next request through the connected AI workflow is paused. Editing, saving, debugging, and tests remain available.
- Closing a panel, pausing, ending a session, or encountering an error does not count as a pass.
- A successful answer can pass immediately. Follow-ups appear only where reasoning is missing.
- Store explanation evidence. Do not display made-up competence percentages or AI-authorship percentages.
- Private by default. Instructor and peer sharing are optional later features.
- Do not depict an unsupported integration as controlling unrelated AI assistants.

### Priority meanings

| Priority | Design expectation |
| --- | --- |
| P0 | Complete the working demo screens and their required states |
| P1 | Design after the complete P0 prototype works |
| P2 | Optional future concept explorations on a separate page |

## 3. Visual direction

Aim for a polished developer utility, with generous clarity around a small amount of information. Code and reasoning should dominate; decorative elements should be rare.

- **Dark-first:** Charcoal surfaces, readable neutral text, a restrained violet action color, and green only for successful outcomes.
- **Compact but comfortable:** Dense enough to belong in an editor, with enough spacing to read a question and write a thoughtful answer.
- **Evidence-led:** File path, code excerpt, question, answer, and feedback form a clear hierarchy.
- **Calm feedback:** Amber means a question needs attention. Reserve red for an operational failure or destructive action.
- **Subtle identity:** A simple bracket-and-check symbol beside the BeProgram wordmark is sufficient. Keep it editable as vector geometry.
- **No visual noise:** Avoid large gradients, glowing borders, glass effects, mascots, trophy illustrations, confetti, decorative charts, or excessive rounded cards.

The extension should inherit its host’s visual character. The website can use more whitespace, but should share the extension’s typography, status language, and components.

## 4. Proposed design tokens

### Color

Use semantic variable names, not raw hex values scattered across frames. Values below are a starting specification; verify final pairings after design changes.

| Token | Dark mode | Light mode | Role |
| --- | --- | --- | --- |
| `surface/canvas` | `#111318` | `#F7F8FA` | Main page background |
| `surface/panel` | `#191C23` | `#FFFFFF` | Panel and primary content surface |
| `surface/raised` | `#232833` | `#EEF1F5` | Hover, inset content, selected surfaces |
| `border/subtle` | `#343C4A` | `#D8DDE6` | Nonessential separators |
| `border/control` | `#778397` | `#68758A` | Input and control boundaries |
| `text/primary` | `#F2F4F8` | `#171B24` | Headings and body |
| `text/secondary` | `#B5BFCE` | `#4E5B70` | Supporting content |
| `action/primary` | `#B5A4FF` | `#5936C9` | Main CTA and selected control |
| `action/on-primary` | `#111318` | `#FFFFFF` | Primary button label |
| `status/success` | `#76E0B4` | `#176A47` | Verified outcome |
| `status/attention` | `#F0C578` | `#875500` | Follow-up or pending checkpoint |
| `status/error` | `#FF9CA9` | `#A7253D` | Failure and destructive action |
| `status/info` | `#93C5FD` | `#205DAB` | Connection and neutral guidance |

Use low-opacity status backgrounds with full-strength status text. Do not apply opacity to the entire component. Diff additions and removals need `+`/`−` markers and clear labels as well as color. Subtle borders cannot be the only visible boundary of an interactive input.

### Typography

| Role | Proposed type | Size / line height | Weight |
| --- | --- | --- | --- |
| Website page title | Inter or system sans | 28 / 36 px | 600 |
| Panel heading | System sans | 18 / 26 px | 600 |
| Question | System sans | 17 / 26 px | 500 |
| Body and answer field | System sans | 14 / 22 px | 400 |
| Control label | System sans | 13 / 20 px | 500 |
| Metadata | System sans | 12 / 18 px | 400 |
| Code | JetBrains Mono or system monospace | 13 / 20 px | 400 |

Use host fonts and semantic theme colors when implementing the extension. Do not put important explanations into tiny metadata text. Permit text resizing without clipped controls.

### Geometry and motion

- Spacing scale: 4, 8, 12, 16, 24, 32, 48 px.
- Extension panel padding: 20–24 px; compact sidebar padding: 16 px.
- Website main gutter: 32 px desktop, 24 px tablet, 16 px mobile.
- Border radius: 6 px controls, 8 px panels, 12 px dialogs. Pills only for short statuses.
- Standard control height: 36 px desktop; use at least 44 px for mobile primary controls.
- Icons: consistent 16 or 20 px outlined set; 1.5–2 px stroke.
- Focus: visible 2 px outline with 2 px offset.
- Motion: 120–180 ms for state changes; at most 240 ms for the success check. No layout-shifting celebration.
- Reduced motion: instant transitions and a static success icon.

## 5. Figma file organization

Organize the editable file into the following pages. Keep frame names stable for developer references.

| Page | Contents |
| --- | --- |
| `00 Brief` | Product summary, priorities, legend, and prototype starting links |
| `01 Foundations` | Colors, type, spacing, icons, dark/light theme examples |
| `02 Components` | Reusable components and state variants |
| `03 Extension P0` | Session setup and the complete checkpoint flow |
| `04 Dashboard P0` | Session overview and checkpoint evidence |
| `05 Recovery States` | Errors, empty states, pause, reconnect, and validation |
| `06 Prototype` | Connected core demo and recovery branches |
| `07 Future P1 P2` | Instructor sharing, hints, voice, and optional reflections |
| `08 Handoff` | Responsive behavior, interaction notes, and implementation mapping |

Use Auto Layout for application content, reusable components for repeated elements, and editable text/code. Define component properties for state, size, theme, and optional content. Avoid flattening application UI into screenshots.

The VS Code shell is presentation context. Label it **Host application — not part of BeProgram implementation** in the handoff. Developers should implement the extension surface, not recreate the entire IDE.

## 6. Frames and responsive layouts

| Surface | Reference frame | Adaptation |
| --- | --- | --- |
| VS Code contextual demo | 1440 × 900 px | Show explorer/editor and BeProgram together |
| Extension editor panel | 860 × 760 px | Code and question may sit side by side |
| Compact extension panel | 420 × 760 px | Stack code, question, and answer |
| Narrow sidebar check | 320 × 760 px | Collapsible code excerpt; full-width primary action |
| Website desktop | 1440 × 960 px | Main content max width 1120 px |
| Website tablet | 768 × 1024 px | Stack summary and evidence sections |
| Website mobile | 390 × 844 px | Single column with no page-level horizontal overflow |

The extension is desktop software. A narrow sidebar frame is not a mobile app design. The website can be read on a phone; starting an editor session there should explain that desktop VS Code is required.

For extension widths below 720 px, stack the code excerpt above the question. At 720 px and above, use approximately 44% code context and 56% explanation area. Allow independent code scrolling; do not create two competing full-height page scroll regions.

Use inline diff in narrow panels. A side-by-side diff is optional in wide evidence views. Long paths truncate in the middle with the full relative path available on focus/hover. Long code lines scroll within the code region. Answers wrap naturally.

## 7. Screen inventory

These identifiers describe product states, not separate navigation destinations. Reuse components to avoid designing a new app for every state.

| ID | Screen/state | Priority | Primary action |
| --- | --- | --- | --- |
| E01 | Welcome and connection | P0 | Connect account / continue |
| E02 | Project and context scope | P0 | Start session |
| E03 | Active session | P0 | Review current changes |
| E04 | Meaningful-change analysis | P0 | Wait; manual coding remains available |
| E05 | Initial checkpoint | P0 | Submit explanation |
| E06 | Evaluating explanation | P0 | Submission in progress |
| E07 | Targeted follow-up | P0 | Submit follow-up |
| E08 | Understanding verified | P0 | Continue coding |
| E09 | Next AI request paused | P0 | Open checkpoint |
| E10 | Paused checkpoint / session end | P0 | Resume checkpoint / end session |
| E11 | Evaluation unavailable | P0 | Retry |
| E12 | Integration disconnected | P0 | Reconnect |
| W01 | Today’s session | P0 | Open checkpoint evidence |
| W02 | Checkpoint evidence | P0 | Back to session |
| W03 | Empty / loading / error history | P0 | Contextual recovery action |
| S01 | Project scope and privacy settings | P0 | Save settings |
| F01 | Instructor report and access grant | P1 | Grant or revoke access |
| F02 | Hint and transfer question | P1 | Answer transfer question |
| F03 | Voice answer | P2 | Review transcript |
| F04 | Optional reflection and sharing | P2 | Save privately / share selected content |

## 8. Extension screen specifications

### E01 — Welcome and connection

**Purpose:** Establish the product promise and connected status without a lengthy onboarding tour.

Content order: BeProgram wordmark; heading **Understand what you build**; one sentence explaining contextual checkpoints; account connection; integration status; primary action.

Use **Connect account** for a disconnected account and **Continue** after pairing. Allow a browser sign-in step represented by an external-link annotation; return to a clear **Account connected** state. Do not invent a custom password or social-login flow unless implementation selects it. A seeded demo can start after this screen.

Integration variants:

- **Claude Code connected** — use only for a validated native integration.
- **BeProgram AI connected** — the app’s managed AI workflow.
- **Demo — external AI lock simulated** — persist this label during any simulated lock demonstration.

Do not show badges for unsupported assistants as if they were connected.

### E02 — Project and context scope

Heading: **Start a coding session**. Show selected project `campus-events`, language **TypeScript**, and local workspace status. Include an expandable source-file preview with relative paths.

Show **Included source files** and **Excluded files**; include `.env`, generated output, dependencies, and user-selected exclusions in the latter. Let users deselect eligible files. A concise disclosure reads: **Selected code excerpts and your explanations are sent to the configured AI service for review. Your history is private.** Show the actual configured provider when available; use an explicit placeholder in annotated design-only frames.

Primary action: **Start session**. Secondary: **Cancel**. Keep Start disabled until a project is selected and the account/integration state is usable. Provide inline messages for no open project, unsupported language, and untrusted workspace. Settings cannot silently expand scope after the session begins.

### E03 — Active session

Heading: **Session active**. Show project, elapsed time as quiet metadata, **Monitoring meaningful changes**, and a short list of recent demonstrated concepts. Primary contextual action: **Review current changes**. Secondary links: **Open learning history**, **Project settings**, and **End session**.

The status bar should read **BeProgram: monitoring**. An ordinary formatting change should not produce a modal or celebratory notification. A user-requested review with no suitable change returns **No meaningful changes to review yet**.

### E04 — Analyzing changes

Display **Reviewing your latest changes…** and the relevant file, with a small progress indicator. Do not show invented percentages. If the user requests more connected AI work before analysis completes, show **Checking this change before your next AI request**. Editing remains available.

Outcomes: no checkpoint needed returns to E03; a useful concept leads to a quiet notification and E05 on user action; a failure leads to E11. No surprise autofocus while the programmer is typing elsewhere.

### E05 — Initial checkpoint

This is the hero screen. Prioritize the question and answer field.

1. Eyebrow **Comprehension checkpoint**.
2. Concept heading **SQL parameterization** and status **Needs explanation**.
3. File `src/data/findUser.ts` and reason **Your latest change introduces a parameterized query**.
4. Captured code/diff with **Captured for this checkpoint** label and optional time.
5. Exact question from section 12.
6. Multiline answer field, minimum 140 px tall, label **Your explanation**, placeholder **Explain how this works in your own words.**
7. Primary button **Submit explanation**; secondary **Pause checkpoint**.
8. Status note **Your next connected AI request is paused. You can still edit and run your code.**

Empty input disables Submit. Whitespace-only input is empty. Do not impose an arbitrary minimum word count. Explain a selected implementation length limit with inline validation only if one is actually configured. Label **Ctrl/⌘ + Enter to submit** as a shortcut, not the only submission method.

### E06 — Evaluating explanation

Keep the submitted answer visible and prevent duplicate submissions. Change the primary action to **Checking explanation…**. Retain layout dimensions so feedback does not jump.

During evaluation, closing the panel preserves state. Reopening shows the current result or progress. A timeout becomes E11 and preserves the draft; it never becomes a failed comprehension result.

### E07 — Targeted follow-up

Heading: **One detail to clarify**. Keep the original question and submitted answer available in a collapsed **Previous answer** disclosure, expanded on demand.

Display specific feedback followed by the new question. Example feedback: **You identified the security goal. Explain how the query keeps the input separate from SQL instructions.** Avoid “Wrong,” “Failed,” or a red grade.

Use a fresh answer field and **Submit follow-up**. Status remains **Needs follow-up** and the connected AI request stays paused. Never show a success check before the evaluator passes the answer. After repeated unsuccessful answers, give **Pause checkpoint** equal visibility without suggesting it unlocks AI access.

### E08 — Understanding verified

Use a small green check icon and heading **Understanding verified**. Show concept, one sentence identifying the demonstrated reasoning, and **Saved to your learning history** only after persistence succeeds.

Primary action **Continue coding** returns to the editor. Secondary **View learning history** opens W01. Status reads **Connected AI assistance available** only after the gate is confirmed cleared. There is no automatic re-submission of a previously blocked AI prompt; the user can send it again.

If evaluation passed but saving is not yet confirmed, show **Saving your result…** and keep the gate status pending. If reconciliation fails, use E11 with a message that distinguishes saving from evaluating.

### E09 — Next AI request paused

Show this only when the user tries the connected AI action with an unresolved checkpoint. Use BeProgram-owned UI: **Explain this change to continue** with the concept and one short explanation.

Primary **Open checkpoint**; secondary **Keep editing**. Keep editing dismisses the notice and returns focus to the editor while leaving the gate unresolved. Do not overlay a large padlock across the IDE or dim unrelated editor controls.

Native integration feedback may appear in its actual supported notification surface. A managed **Ask AI** composer can show a paused send action with its reason. Design the chosen adapter clearly; do not fabricate native Claude Code interface behavior.

### E10 — Pause or end session

Pause preserves answers and shows **Checkpoint paused** with **Resume checkpoint**. Supporting copy: **Your explanation is saved. Your next connected AI request still needs this checkpoint.**

End-session confirmation appears only when needed to explain unresolved work. Heading **End this session?** Copy **Your history will be saved. This checkpoint will remain unresolved.** Actions: **End session** and **Keep session open**. Ending a session must not display a verified state or imply deletion of history.

### E11 — Evaluation or saving unavailable

Inline panel error: **We couldn’t check your explanation**. Supporting copy: **Your answer is saved here. Try again when the connection returns.** Actions **Retry** and **Keep editing**.

Use **We couldn’t confirm your saved result** for post-evaluation persistence/reconciliation failures. Do not blame the learner or mark the explanation incorrect. Only show “saved” if persistence is known; otherwise say **Your draft is still in this panel**.

### E12 — Integration disconnected

Heading **Reconnect your coding assistant**. Explain **BeProgram can’t confirm the connected AI workflow right now. Your checkpoint and draft are still available.** Primary **Reconnect**; secondary **Open checkpoint**.

Show connection and comprehension state separately. A disconnected adapter does not mean the user failed a checkpoint. Use neutral or amber connection treatment rather than a red learning status.

## 9. Website specifications

### W01 — Today’s session

Use a lightweight top navigation: BeProgram wordmark, project name, session date, and account menu. Avoid a permanent sidebar with empty product destinations.

Header: **Today’s session**; subtitle `campus-events · TypeScript`. Provide **Open in VS Code** and a quiet refresh control. If editor opening fails, show **Open the project in VS Code and choose Open learning history**; do not leave the user on a dead button.

Summary: **3 concepts demonstrated · 0 awaiting explanation** after the demo pass. These counts are evidence records in this session, not skill scores. The before-pass frame shows **2 demonstrated · 1 awaiting explanation**.

Main content: list grouped by file, with concept, status, time, and a chevron to evidence. Use broad rows with readable text rather than a dashboard full of charts. The current demo concept should be easy to find, but not permanently highlighted after normal use.

Optional footer context: **Private to you**. No share CTA in P0.

### W02 — Checkpoint evidence

Breadcrumb **Today’s session / SQL parameterization**. Show status, file, timestamp, and **This result covers the captured code shown below**.

Sections: captured code; initial question; initial answer; feedback and follow-up; follow-up answer; demonstrated reasoning. Use a structured evidence view, not an endless chat transcript with avatars.

At desktop widths, code can sit beside reasoning. On mobile, place the question and outcome first, then expandable code, then the answer sequence. Default answer text is readable without opening multiple disclosures.

If code has expired or been deleted, keep any permitted retained metadata clearly labeled **Code excerpt unavailable**. Do not render an empty code block as if the concept was fully reviewable. Back navigation returns to the prior list position.

### W03 — History variants

- **Empty:** “Your learning history starts with your first checkpoint.” CTA **Open VS Code**.
- **Loading:** Skeleton rows with stable dimensions. No invented completed counts.
- **No active session:** Keep past permitted history available; explain how to begin a session in the editor.
- **Request error:** “We couldn’t load this session.” CTA **Try again**.
- **Unavailable evidence:** “This record is unavailable.” Do not leak a private title to an unauthorized viewer.
- **Mobile:** “Start coding sessions in desktop VS Code. You can review your history here.”

### S01 — Project scope and privacy settings

Keep this compact and reachable from session setup and the account/project menu. Show included files, exclusion controls, provider disclosure, and private visibility. Save changes explicitly; cancel returns without changing the scope.

Expose project-history deletion behind a clearly named destructive action and confirmation. Show the project name and explain the evidence that will be removed. Deletion and ordinary session ending must be visually and verbally distinct.

## 10. Shared state model and copy

Connection state and checkpoint state are separate properties. Avoid a single badge that alternates ambiguously between “Offline,” “Failed,” and “Passed.”

| Product state | Visible label | Main action | Connected AI access |
| --- | --- | --- | --- |
| Monitoring | Monitoring meaningful changes | Review current changes | Available if no unresolved work |
| Analyzing | Reviewing changes… | None required | Temporarily pending |
| Pending checkpoint | Needs explanation | Submit explanation | Paused |
| Evaluating | Checking explanation… | Prevent duplicate submit | Paused |
| Partial explanation | Needs follow-up | Submit follow-up | Paused |
| Passed and persisted | Understanding verified | Continue coding | Available |
| Paused checkpoint | Checkpoint paused | Resume checkpoint | Paused |
| Operational error | Review unavailable | Retry | Unresolved; manual coding available |
| Adapter unavailable | Integration disconnected | Reconnect | Cannot claim external enforcement |

Show short, specific explanations. Prefer **Needs follow-up** to **Low understanding**. Do not display numeric confidence, a “smartness” score, an AI-use percentage, an academic grade, or a cheating accusation.

## 11. Component inventory

| Component | Required properties/variants |
| --- | --- |
| `Button` | Primary, secondary, text, destructive; default, hover, focus, disabled, loading |
| `IconButton` | Tooltip/accessibility label; default, hover, focus, disabled |
| `TextArea` | Empty, focused, filled, error, submitting; helper text and preserved draft |
| `StatusBadge` | Needs explanation, needs follow-up, verified, paused, unavailable |
| `ConnectionIndicator` | Connected, reconnecting, disconnected; separate from learning status |
| `IntegrationMode` | Native, managed, simulated-demo disclosure |
| `CodeExcerpt` | Inline diff, plain code, loading, unavailable; file and capture metadata |
| `QuestionBlock` | Initial question, follow-up, transfer question |
| `FeedbackBlock` | Gap identified, demonstrated reasoning, unavailable review |
| `AnswerHistory` | Expanded/collapsed previous question and answer |
| `ConceptRow` | Demonstrated, needs follow-up, not assessed; hover/focus/selected |
| `SessionSummary` | Empty, pending count, completed count, loading |
| `InlineNotice` | Informational, pending, success, operational error |
| `Toast` | Checkpoint available, connection restored; dismissible |
| `ConfirmDialog` | End session with unresolved work; delete history |
| `FileScopeList` | Selected, excluded, disabled by policy; expand/collapse |
| `EmptyState` | No history, no changes, no active session, unavailable record |

Make long labels and multi-paragraph feedback resize components vertically. Do not rely on a fixed height that clips translated, zoomed, or real model-generated text.

## 12. Canonical demo content

Use this fixture throughout the prototype so questions, answers, counters, and history agree. It is illustrative UI content, not a claim that BeProgram evaluated a real user.

**Project:** `campus-events`  
**Session date:** 18 September 2026  
**Current file:** `src/data/findUser.ts`  
**Concept:** SQL parameterization  
**Integration:** BeProgram AI connected, unless the team has validated a native adapter

Captured TypeScript code; assume a PostgreSQL client with parameterized-query support:

```typescript
export async function findUser(email: string) {
  const result = await pool.query(
    'SELECT id, name FROM users WHERE email = $1',
    [email]
  );
  return result.rows[0] ?? null;
}
```

**Initial question:** “Why does this query pass `email` separately instead of inserting it directly into the SQL string?”

**Weak answer:** “It makes the database safer.”

**Feedback:** “You identified the security goal. Explain how the query keeps the input separate from SQL instructions.”

**Follow-up:** “What role does `$1` play, and how is the value in `[email]` handled?”

**Passing answer:** “The SQL text contains a placeholder, and the email is supplied separately as the value for that placeholder. The database treats that value as data rather than part of the SQL instructions, so it cannot change the query’s structure.”

**Success feedback:** “You explained how parameter binding separates user input from SQL instructions.”

The prototype may use preset answers, but the resulting design must still support ordinary editable input. Annotate fixture shortcuts outside the application canvas rather than pretending the real evaluator always returns a predetermined result.

### Consistent history fixtures

| File | Concept | Before current checkpoint passes | After it passes |
| --- | --- | --- | --- |
| `src/services/events.ts` | Async error handling | Demonstrated at 2:10 PM | Unchanged |
| `src/utils/parseEvent.ts` | Input validation | Demonstrated at 2:18 PM | Unchanged |
| `src/data/findUser.ts` | SQL parameterization | Needs explanation at 2:24 PM | Demonstrated at 2:26 PM |

Before: 2 demonstrated and 1 awaiting explanation. After: 3 demonstrated and 0 awaiting explanation. W02 must display the same answer and timestamp represented by its W01 row.

## 13. Clickable prototype wiring

Create three named starting points: **Core demo**, **Setup**, and **Recovery**.

### Core demo

1. E03 active session → user starts the managed/connected AI feature request.
2. Show code changed → E04 analysis → **Checkpoint available** notification.
3. Select **Open checkpoint** → E05.
4. Enter/preset the weak answer → E06 → E07.
5. Optionally attempt the next connected AI request → E09 → **Open checkpoint** returns to E07 without losing text.
6. Submit the correct follow-up → E06 → E08.
7. Select **Continue coding** → editor state with connected AI available.
8. Select **View learning history** from the extension → W01 with updated counts.
9. Select **SQL parameterization** → W02 → back returns to W01.

Use brief prototype delays only to demonstrate asynchronous transitions. Annotate them as prototype timing, not promised production latency. Keep the same connection-mode disclosure throughout the entire route.

### Setup

E01 → account connected → E02 → review scope → start → E03. Include the no-project branch and a way back. Do not make a prototype-only sign-in dead end.

### Recovery

E05 with drafted text → E06 → E11 → retry → E07. Separate branch: E07 → pause → E10 → resume → E07. Reopening the panel restores the answer. A final branch demonstrates E12 reconnecting without changing checkpoint status.

Also include a direct-pass variant: a complete initial explanation goes from E06 to E08 without a forced follow-up.

## 14. Accessibility and interaction details

- Validate at least 4.5:1 contrast for normal text and 3:1 for large text and essential control/focus boundaries.
- Every status includes a text label; success and failure are never communicated by color alone.
- Define a logical keyboard order: header actions, code controls, question, answer, submit, secondary action.
- Do not automatically move focus when a checkpoint arrives. When the user opens it, focus its heading; let them move to the answer field.
- After explicit submission, announce the result and place focus on the new feedback/question when appropriate. Return focus to the invoking control when a dialog closes.
- Support keyboard scrolling of code regions. Code indentation should remain readable without forcing the whole page sideways.
- At 200% text zoom, controls reflow and text remains visible. Sticky footers must not cover the answer field or focused controls.
- Buttons have visible focus, full accessible names, and practical target spacing. Mobile actions are at least 44 px high.
- All tooltips also work on focus. Critical information appears inline instead of only in a tooltip.
- Motion has a reduced-motion alternative. No countdown timer pressures users into quick answers.

## 15. Optional P1 and P2 UI

Design these only after the P0 file and prototype are complete. Keep them off the core navigation until implemented.

### F01 — Instructor access and report, P1

Flow: owner selects evidence → chooses a specific instructor account → previews exactly what will be shared → grants access → instructor sees a read-only report. Include revoke access and unavailable-after-revocation states.

Report content: selected project/session, demonstrated concepts, unresolved checkpoints, and explanation evidence. Do not invent “34% AI-written,” class ranking, automatic grades, or universal teacher access. Label unassessed concepts clearly.

### F02 — Learning hint and transfer, P1

Show a short optional hint, followed by a new reasoning question. Reading the hint does not pass the checkpoint. A successful transfer answer receives **Demonstrated with help** in the evidence view; it does not masquerade as an unaided response.

### F03 — Voice explanation, P2

Variants: microphone permission, ready, recording, stopped, transcribing, editable transcript, failed transcription. Require a visible recording indicator and Stop/Cancel controls. Submit the reviewed text only after explicit confirmation. Text input remains available throughout.

### F04 — Reflection and sharing, P2

Optional notification: **What did you learn while coding today?** Let users save privately, dismiss, or preview a share with selected friends/classmates. Code is excluded by default; including a code excerpt requires preview. Provide revocation and an empty shared-history state.

Random reflections must not replace meaningful-change checkpoints. Public discovery, a full social feed, leaderboards, and streak pressure are outside this design’s implementation scope.

## 16. Developer handoff annotations

Annotate each P0 frame with: screen ID, entry condition, source state, primary action, resulting state, loading behavior, keyboard focus behavior, and responsive rule. Put annotations outside the application canvas.

Distinguish these state sources:

| UI element | Source of truth |
| --- | --- |
| Selected project and file scope | Local extension state plus saved project settings |
| Integration status | Adapter connection state |
| Checkpoint question and feedback | Backend checkpoint/evaluation response |
| Draft answer | Preserved local input until submitted |
| Verified state | Persisted backend evaluation result |
| Connected AI availability | Reconciled gate state |
| History counts | Actual session evidence records |

Do not reveal API routes, model prompt templates, snapshot hashes, or internal IDs in normal UI. Expose only details that help the user understand context, privacy, progress, or recovery.

For implementation, supply tokens and reusable components before individual one-off CSS values. Export only required vector icons or brand marks; keep interface text and layout editable.

## 17. Final design acceptance checklist

- [ ] The extension checkpoint is the visual center of the product.
- [ ] All P0 screens/states listed in section 7 are present.
- [ ] Core demo, setup, and recovery flows have working links and back paths.
- [ ] A weak explanation receives a code-specific follow-up.
- [ ] A strong initial answer can pass without an unnecessary follow-up.
- [ ] The connected AI request is visibly paused and later available; manual editing remains usable.
- [ ] Closing, pausing, ending a session, and connection failure never show a false pass.
- [ ] Native, managed, and simulated integration variants are labeled honestly.
- [ ] Dashboard counts, timestamps, code, and answer evidence match the canonical fixture.
- [ ] Empty, loading, unavailable, and retry states preserve context.
- [ ] Narrow extension panels and mobile website frames do not clip content.
- [ ] Color, focus, target size, text resizing, and reduced-motion behavior are documented.
- [ ] The file uses editable text, reusable components, variables, and Auto Layout.
- [ ] P1/P2 explorations are separated from P0 and do not expand the hackathon build by accident.

## 18. Short kickoff prompt

Use this opening instruction alongside the complete brief and `PRD.md`:

> Design BeProgram, a polished developer tool inside VS Code with a minimal learning-history website. Follow this handoff and the PRD. First build a reusable dark-first design system, then the P0 extension screens and website evidence views. The central prototype must show a meaningful AI code change, a contextual question, a weak answer, a targeted follow-up, a correct explanation, “Understanding verified,” the next connected AI request becoming available, and the new concept appearing in history. Use the supplied SQL parameterization fixture consistently. Include setup, pause, error, retry, disconnected, empty, and loading states. Keep the interface calm, readable, and credible inside VS Code. Make every screen editable and connect the prototype with reusable components. Keep social sharing, instructor reports, voice, and random reflections on a separate future page after P0. Do not add a marketing website, fabricated scores, unsupported integrations, or a generic analytics dashboard. Generate the checkpoint flow first, then expand to the remaining screens in this brief.
