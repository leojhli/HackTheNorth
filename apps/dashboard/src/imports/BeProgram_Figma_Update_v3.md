# BeProgram Figma Update for PRD v3

**Date:** 19 September 2026  
**Apply to:** Existing BeProgram Figma designs based on `BeProgram_Figma_Design_Handoff.md`  
**Product source:** `BeProgram_PRD_v3.md`  
**Purpose:** Extend the current design without rebuilding the core screens

## 1. Compatibility decision

The existing checkpoint, follow-up, success, session, and history designs remain compatible with the new PRD. Preserve their visual system, layout, navigation, and core prototype. The actual Figma-generated file has not been inspected, so this is a design-contract assessment rather than a visual review of that file.

Keep the original frame IDs E01–E12, W01–W03, and S01. Keep the current typography, dark/light themes, code excerpt component, buttons, badges, and responsive behavior. New provider-specific features are secondary actions or optional variants. Do not add a sponsor dashboard or replace the editor-centered experience.

## 2. Change map

| Existing frame | Change | Priority |
| --- | --- | --- |
| E01 connection | Continue showing only the actual coding-assistant integration mode | P0 |
| E02 scope | Update provider/data-use disclosure for enabled services only | P0 |
| E05 initial question | Add optional Listen and Record answer actions | P1 |
| E06 evaluation | Same existing state; voice transcript is ordinary reviewed text | P0 |
| E07 follow-up | Reuse Listen/Record actions and transcript state | P1 |
| E08 success | Keep Continue coding first; add quiet Create verifiable receipt link | P1 |
| W01 history | Optional small Receipt available indicator; do not change concept counts | P1 |
| W02 evidence | Add receipt card and selected PR summary action | P1 |
| S01 settings | Connected services, scopes, unlink, and privacy disclosures | P1 |
| F03 voice future frame | Promote from P2 to P1; reuse its existing states | P1 |
| Optional source disclosure | Related code/docs with commit-specific citations | P2 |

OpenAI evaluation, Sentry instrumentation, and hosting do not require new product screens. Sentry is operated in the team’s debugging tools. Keep implementation details out of the normal learning journey.

## 3. Voice controls and states

Add a small speaker button next to the question with accessible label **Listen to question**. During playback, change it to **Stop playback**. Do not autoplay in the editor.

Place **Record answer** beside the existing text input without removing or narrowing the usable text area. States:

1. Ready: Record answer.
2. Permission requested: explain microphone use.
3. Recording: visible indicator, elapsed time, Stop, Cancel.
4. Transcribing: spinner and **Preparing your transcript…**.
5. Review: editable text and **Review your transcript before submitting**.
6. Error/denied: **You can type your answer instead**.

The normal Submit explanation/follow-up button sends only the reviewed transcript. Do not automatically submit audio, grade accent, or add a separate chat persona. Reuse E06–E08 after submission. No animation should imply a pass before assessment.

If microphone capture needs a browser companion in the real implementation, link to that view explicitly. Do not show a native-extension recording capability that only exists in the mockup.

## 4. Assessment receipt entry points

On E08, keep **Continue coding** as the primary action and **View learning history** as the existing secondary action. Place **Create verifiable receipt** as a low-emphasis link, or make it available only on W02 if the screen becomes crowded.

On W02, add an **Assessment receipt** card after the explanation evidence. Copy: **Create an optional record that others can check for issuer and evidence integrity.** Add **This does not independently prove skill mastery.** Show **Solana Devnet · Demo network** when applicable.

A receipt is not a currency, asset marketplace item, or collectible. Do not add prices, trading, rarity, leaderboards, or token balances. Do not require a wallet to use checkpoints or history.

## 5. New receipt frames

### C01 — Preview and consent

Content: concept, checkpoint time, assistance level, selected subject wallet, issuer, demo network, and a clear preview of public fields. Group the private evidence separately from the public record.

Use **Connect demo wallet** only at this optional stage. Explain that wallet addresses/transaction metadata may be publicly visible and that code and answers stay off-chain. Public publication cannot be reversed by deleting the app’s history.

Primary **Create receipt**, secondary **Cancel**. Include wallet rejection, wrong network, expired challenge, and ineligible/unpassed checkpoint variants. Cancel returns to W02 without changing the learning pass.

### C02 — Issuance status

States: preparing, awaiting approval, submitting, pending confirmation, confirmed, failed, and uncertain confirmation. Avoid “Minted” unless the implementation truly issues that kind of asset; the selected product is a receipt.

Confirmed actions: **Open verifier**, **Export evidence package**, and **View transaction**. A transaction link exists only when a real reference is available. During uncertainty, use **Check status**; do not encourage duplicate issuance.

Error copy: **Your checkpoint is still complete. We couldn’t confirm this receipt yet.** The normal AI workflow stays available regardless of receipt outcome.

### C03 — Independent verifier

Use the same visual system with a separate page purpose: **Verify assessment receipt**. Accept a receipt reference and exported evidence package. Private-package content should be processed locally where feasible; never imply it is automatically published.

Display separate result rows:

- Network and record confirmation.
- Trusted issuer verified / unknown issuer.
- Evidence matches / evidence mismatch.
- Subject wallet listed / wallet control verified only after a fresh signed challenge.
- Expiry if included.
- Revocation status only when the implemented route supports it.

For the Memo fallback, display **Revocation not supported in this prototype**. For RPC failure, show **Verification temporarily unavailable**, not Invalid. Always distinguish receipt integrity from educational accuracy.

Include a tampered-package result in the prototype. Do not use one universal green “Verified person” badge.

## 6. GitHub connection and review frames

### G01 — Selected PR import

From S01 or a contextual Review PR action, connect GitHub, select an authorized repository and PR, and preview included files and commit SHA. Primary **Review this PR**; secondary Cancel.

Show the actual account/repository/PR prominently. Do not imply scanning all repositories. Include insufficient permissions, no PRs, disconnected account, and missing context states. Imported checkpoints reuse the original E05–E08 components with a PR context label.

### G02 — Summary preview and publication

From W02 or the session view, select **Prepare PR summary**. Preview the exact comment and target repository/PR/head SHA. Include concepts demonstrated, coverage limits, and only the owner-approved evidence references. Private answers and retry history are excluded by default.

Primary **Publish this summary**. Secondary **Cancel**. A passed checkpoint does not auto-publish.

States: preparing preview, ready, publishing, published with returned URL, failed, unknown outcome/checking status, and PR changed. If the head changed, show **This PR has new commits. Refresh the review before publishing.** Do not show Merge or Approve PR actions.

## 7. Optional retrieval disclosure

If Elasticsearch retrieval is implemented, add **Context used** under the code excerpt. Expand to show approved source snippets with file, source type, and commit/reference. A conflict notice can read **The project notes differ from this code. This question uses the captured implementation.**

This is a disclosure, not a new search application. Do not add global repository browsing or implied access to unapproved code.

## 8. Components to add

| Component | Variants |
| --- | --- |
| SpeechPlayback | Ready, playing, unavailable |
| VoiceAnswer | Permission, recording, transcribing, transcript review, error |
| ReceiptCard | Not requested, processing, confirmed, failed |
| PublicDisclosure | Exact field preview, consent, canceled |
| WalletConnection | Disconnected, connected, rejected, wrong network |
| VerificationRow | Match, mismatch, unknown, unavailable, unsupported |
| PRContext | Repo/PR/head, stale, unavailable |
| PublicationPreview | Ready, approving, sending, published, uncertain, failed |

Use the existing button/input/dialog/notice components. Learning state, connection state, publication state, and receipt state remain separate properties. Dark and light variants and keyboard behavior remain required.

## 9. Prototype changes

Keep **Core demo** unchanged: meaningful change → explanation → follow-up → pass/unlock → history. Preserve the original SQL parameterization fixture and the count transition from 2 demonstrated/1 pending to 3 demonstrated/0 pending.

Add three optional branches rather than forcing them into every user session:

1. **Receipt branch:** W02 → C01 → C02 → C03 → altered package → mismatch.
2. **Voice branch:** E07 → Listen → Record → review/edit transcript → E06 → E08.
3. **PR branch:** G01 → normal checkpoint flow → G02 preview → explicit publish → returned PR URL.

Add error branches demonstrating that receipt and publication failures do not undo the learning pass. Hide unavailable features in the implementation; label future concept frames outside the product canvas.

## 10. Handoff prompt for Figma

> Update the existing BeProgram design using PRD v3 and this delta brief. Preserve the current visual system, frame IDs, checkpoint flow, follow-up screen, success state, and learning history. Add optional Listen/Record controls using the already planned voice states; keep editable text and explicit submission. Add secondary assessment-receipt controls, a publication-preview dialog, issuance states, and an independent verifier that separates issuer, evidence integrity, subject control, expiry, and supported revocation status. Label Devnet and any simulated integration honestly. Add selected GitHub PR import and exact-comment preview with explicit publishing approval. Reuse existing components and keep all new flows optional after the core interaction. Do not redesign the app, add a wallet requirement to ordinary coding, or add sponsor logos, scores, trading, or a new analytics dashboard. Keep the existing core prototype and add separate receipt, voice, and PR branches with recovery states.

## 11. Completion criteria

- Core navigation and prototype remain intact.
- New actions are optional and correctly prioritized.
- Learning success never depends on chain, speech, or GitHub availability.
- No false issuer, mastery, privacy, or integration claims appear in UI.
- Exact PR target and public receipt disclosure are shown before publication.
- Status variants have readable text, keyboard focus, and recovery paths.
- Existing code/answer fixtures and history counts remain consistent.
- The final file distinguishes implemented screens from future concepts.
