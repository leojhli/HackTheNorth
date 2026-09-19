# Assessment review worksheet

Actual local model results against 20 fixed synthetic explanations. Expected labels were authored by the coding agent before this run. This is not completed human review or a production accuracy estimate.

Reviewer: ______  Date: ______

For each case, independently judge the code/answer before considering the model feedback. Record pass, follow-up or unable-to-assess, whether feedback is correct, and whether it reveals too much. Disagreements stay visible.

## Run summary

```json
{
  "total": 20,
  "matching_agent_labels": 19,
  "false_passes": 0,
  "complete_answers_not_passed": 1,
  "operational_failures": 1,
  "evaluation_p95_seconds": 5.5,
  "human_review_completed": false
}
```

## nullish-complete

Before:
```javascript
export function volume(value) { return value || 50; }
```
After:
```javascript
export function volume(value) { return value ?? 50; }
```
**Question:** How does changing || to ?? affect the fallback, and what validation is still missing?

**Rubric:** Preserve explicit falsy values such as zero.; Nullish coalescing falls back only for null or undefined.; Explain a retained value or missing type/range validation.

**Explanation:** The change preserves a requested volume of zero instead of replacing it with 50. Nullish coalescing uses the fallback only for null or undefined; || uses it for any falsy value. It still accepts strings or out-of-range numbers, so this is not volume validation.

**Human decision / reason (fill in):** ______

**Agent label:** pass | **Model/server outcome:** operational_failure

**Feedback:** invalid_local_response

**Human feedback-quality notes (fill in):** ______

## nullish-paraphrase

Before:
```javascript
export function volume(value) { return value || 50; }
```
After:
```javascript
export function volume(value) { return value ?? 50; }
```
**Question:** How does changing || to ?? affect the fallback, and what validation is still missing?

**Rubric:** Preserve explicit falsy values such as zero.; Nullish coalescing falls back only for null or undefined.; Explain a retained value or missing type/range validation.

**Explanation:** An explicit 0 now stays 0, so muting works. Only a missing value, null or undefined, becomes 50. False and an empty string also survive now, so a numeric range check would still be needed.

**Human decision / reason (fill in):** ______

**Agent label:** pass | **Model/server outcome:** pass

**Feedback:** The change from || to ?? ensures that explicit falsy values like 0, false, or empty strings are preserved, while only null or undefined fall back to 50. This correctly preserves intent for zero as a valid input (e.g., muting), and avoids unintended fallbacks. However, the answer correctly identifies that numeric range validation is still missing—inputs like 'abc' or '1.5' may still be accepted without type or range checks, which is a critical gap in validation. The reasoning aligns with the rubric: falsy values are preserved, nullish coalescing is correctly applied, and a retained validation need is acknowledged.

**Human feedback-quality notes (fill in):** ______

## nullish-vague

Before:
```javascript
export function volume(value) { return value || 50; }
```
After:
```javascript
export function volume(value) { return value ?? 50; }
```
**Question:** How does changing || to ?? affect the fallback, and what validation is still missing?

**Rubric:** Preserve explicit falsy values such as zero.; Nullish coalescing falls back only for null or undefined.; Explain a retained value or missing type/range validation.

**Explanation:** The new operator handles the defaults better.

**Human decision / reason (fill in):** ______

**Agent label:** follow_up | **Model/server outcome:** follow_up

**Feedback:** The answer does not address the core requirements of the rubric. It fails to explain how the nullish coalescing operator (??) preserves explicit falsy values like zero, which is a key requirement. It also does not mention that nullish coalescing only falls back for null or undefined, not for falsy values like 0, false, or empty strings. Additionally, no validation is discussed for input types or ranges. The statement 'handles the defaults better' is vague and lacks specificity about behavior or constraints. A correct explanation must explicitly contrast || and ?? in terms of falsy value handling and acknowledge missing validation for input types or ranges.

**Human feedback-quality notes (fill in):** ______

## nullish-misconception

Before:
```javascript
export function volume(value) { return value || 50; }
```
After:
```javascript
export function volume(value) { return value ?? 50; }
```
**Question:** How does changing || to ?? affect the fallback, and what validation is still missing?

**Rubric:** Preserve explicit falsy values such as zero.; Nullish coalescing falls back only for null or undefined.; Explain a retained value or missing type/range validation.

**Explanation:** The new operator rejects all falsy inputs, including zero and false, and replaces them with 50. It also validates that volume is between 0 and 100.

**Human decision / reason (fill in):** ______

**Agent label:** follow_up | **Model/server outcome:** follow_up

**Feedback:** The answer incorrectly claims that the nullish coalescing operator (??) rejects all falsy inputs, including zero and false. In reality, ?? only falls back to 50 when the value is null or undefined, not when it is zero or false. Zero is a falsy value but is not nullish, so it would pass through unchanged. The claim that the operator 'rejects all falsy inputs' is therefore false. Additionally, the answer states that validation occurs 'between 0 and 100', but there is no such validation in the code. This assertion is unsupported and introduces a missing validation that was not present in the original or modified code. The answer fails to correctly explain the behavior of ?? and misses the core distinction between nullish and falsy values.

**Human feedback-quality notes (fill in):** ______

## await-complete

Before:
```javascript
export async function saveThenNotify(save, notify) { save(); notify(); }
```
After:
```javascript
export async function saveThenNotify(save, notify) { await save(); notify(); }
```
**Question:** What ordering does await establish here, and what happens if saving fails?

**Rubric:** Notify after save completes successfully.; Await suspends this async function until the returned promise settles without blocking the thread.; A rejected save propagates and prevents notify unless handled.

**Explanation:** Notification now happens after successful saving. Await pauses this async function until the promise returned by save fulfills; other work can still run on the event loop. If save rejects, the function rejects and notify is skipped because there is no catch.

**Human decision / reason (fill in):** ______

**Agent label:** pass | **Model/server outcome:** pass

**Feedback:** The answer correctly identifies that notify occurs only after save completes successfully. It accurately explains that await suspends execution until save's promise settles, allowing other async work to proceed on the event loop. It also correctly notes that if save rejects, the function rejects and notify is skipped due to the absence of error handling. This aligns fully with the behavior described in the rubric and the visible code change.

**Human feedback-quality notes (fill in):** ______

## await-paraphrase

Before:
```javascript
export async function saveThenNotify(save, notify) { save(); notify(); }
```
After:
```javascript
export async function saveThenNotify(save, notify) { await save(); notify(); }
```
**Question:** What ordering does await establish here, and what happens if saving fails?

**Rubric:** Notify after save completes successfully.; Await suspends this async function until the returned promise settles without blocking the thread.; A rejected save propagates and prevents notify unless handled.

**Explanation:** We stop racing the notification against the save operation: the continuation runs when the save promise resolves. This yields control rather than freezing the whole JavaScript thread. A save rejection escapes to the caller and this code never reaches notify in that case.

**Human decision / reason (fill in):** ______

**Agent label:** pass | **Model/server outcome:** pass

**Feedback:** The use of `await` ensures that `notify` is only called after `save` completes successfully, establishing a clear ordering where the save operation must finish before the notification proceeds. It suspends execution until the save promise settles, avoiding thread blocking and enabling non-blocking async behavior. If `save` fails (i.e., returns a rejected promise), the error propagates to the caller and `notify` is never invoked, which correctly handles error cases without silent failures. This aligns with the rubric's requirements for proper async ordering, suspension behavior, and error propagation.

**Human feedback-quality notes (fill in):** ______

## await-vague

Before:
```javascript
export async function saveThenNotify(save, notify) { save(); notify(); }
```
After:
```javascript
export async function saveThenNotify(save, notify) { await save(); notify(); }
```
**Question:** What ordering does await establish here, and what happens if saving fails?

**Rubric:** Notify after save completes successfully.; Await suspends this async function until the returned promise settles without blocking the thread.; A rejected save propagates and prevents notify unless handled.

**Explanation:** Await makes the asynchronous part work properly.

**Human decision / reason (fill in):** ______

**Agent label:** follow_up | **Model/server outcome:** follow_up

**Feedback:** The answer does not address the key aspects of the behavior required by the rubric. It fails to explain the ordering established by `await`, how the function suspends execution until `save` completes, or what happens if `save` fails. The statement 'Await makes the asynchronous part work properly' is vague and does not specify the actual operational behavior or error handling. It also omits the critical point that a rejected promise from `save` would propagate and prevent `notify` from being called unless handled. A correct explanation must explicitly describe the sequence of execution and error propagation.

**Human feedback-quality notes (fill in):** ______

## await-misconception

Before:
```javascript
export async function saveThenNotify(save, notify) { save(); notify(); }
```
After:
```javascript
export async function saveThenNotify(save, notify) { await save(); notify(); }
```
**Question:** What ordering does await establish here, and what happens if saving fails?

**Rubric:** Notify after save completes successfully.; Await suspends this async function until the returned promise settles without blocking the thread.; A rejected save propagates and prevents notify unless handled.

**Explanation:** Await blocks the entire JavaScript thread until save finishes. Notify runs even if the save promise rejects because await automatically catches errors.

**Human decision / reason (fill in):** ______

**Agent label:** follow_up | **Model/server outcome:** follow_up

**Feedback:** The explanation incorrectly claims that 'await automatically catches errors' and that 'Notify runs even if the save promise rejects'. In JavaScript, await does not automatically catch errors — if a promise rejects, the function will throw an unhandled error and terminate immediately, preventing notify from running. The behavior described in the answer contradicts the actual behavior of async/await. The correct behavior is that if save fails (rejects), the function exits with an unhandled rejection, and notify is never called. This is a central contradiction to the actual runtime semantics of async/await. The answer must clarify that a rejected save promise will cause the function to terminate, and notify will not run unless the error is caught with a try-catch block.

**Human feedback-quality notes (fill in):** ______

## filter-complete

Before:
```javascript
export function activeUsers(users) { return users.find(user => user.active); }
```
After:
```javascript
export function activeUsers(users) { return users.filter(user => user.active); }
```
**Question:** How do the return value and no-match case change when find becomes filter?

**Rubric:** Return all active matches rather than one.; Filter builds a new array of every element whose predicate is truthy.; No matches returns an empty array; returned objects remain shared references.

**Explanation:** The function now returns all active users instead of only the first one. Filter runs the predicate and builds an array containing every match. With no matches it returns [], whereas find returned undefined. The result array is new, but its user objects are not cloned.

**Human decision / reason (fill in):** ______

**Agent label:** pass | **Model/server outcome:** pass

**Feedback:** The answer correctly identifies that filter returns all matching elements instead of just the first (as find does), explains that filter builds a new array with every truthy match, and notes that no matches result in an empty array rather than undefined. It also correctly states that while the array is new, the user objects inside are shared references, which is consistent with JavaScript's behavior. All three rubric points are addressed without contradiction.

**Human feedback-quality notes (fill in):** ______

## filter-paraphrase

Before:
```javascript
export function activeUsers(users) { return users.find(user => user.active); }
```
After:
```javascript
export function activeUsers(users) { return users.filter(user => user.active); }
```
**Question:** How do the return value and no-match case change when find becomes filter?

**Rubric:** Return all active matches rather than one.; Filter builds a new array of every element whose predicate is truthy.; No matches returns an empty array; returned objects remain shared references.

**Explanation:** Every entry with a truthy active property is collected into a fresh array, instead of stopping at the first matching user. Zero matches produces an empty array, so callers must now handle a collection. Editing an object inside that array still edits the same object referenced by the original users array.

**Human decision / reason (fill in):** ______

**Agent label:** pass | **Model/server outcome:** pass

**Feedback:** The change from find to filter shifts behavior: instead of returning the first matching user, it returns all active users in a new array. This means all matching entries are collected, not just one. When no matches exist, it returns an empty array rather than undefined. The returned objects are still shared references to the original array, so modifications to elements in the result affect the original data. This change improves consistency in handling multiple matches but requires callers to manage empty arrays and shared references.

**Human feedback-quality notes (fill in):** ______

## filter-vague

Before:
```javascript
export function activeUsers(users) { return users.find(user => user.active); }
```
After:
```javascript
export function activeUsers(users) { return users.filter(user => user.active); }
```
**Question:** How do the return value and no-match case change when find becomes filter?

**Rubric:** Return all active matches rather than one.; Filter builds a new array of every element whose predicate is truthy.; No matches returns an empty array; returned objects remain shared references.

**Explanation:** It filters the users more effectively.

**Human decision / reason (fill in):** ______

**Agent label:** follow_up | **Model/server outcome:** follow_up

**Feedback:** The answer 'It filters the users more effectively' does not address the specific changes in return value, no-match case, or array mutation behavior as required by the rubric. It lacks explicit explanation of how the behavior differs from find (e.g., returning all matches instead of one, returning an empty array on no matches, or preserving shared references). The mechanism of filter versus find is not explained, and no mention is made of array construction or shared references. A correct response must describe these observable behavioral differences.

**Human feedback-quality notes (fill in):** ______

## filter-misconception

Before:
```javascript
export function activeUsers(users) { return users.find(user => user.active); }
```
After:
```javascript
export function activeUsers(users) { return users.filter(user => user.active); }
```
**Question:** How do the return value and no-match case change when find becomes filter?

**Rubric:** Return all active matches rather than one.; Filter builds a new array of every element whose predicate is truthy.; No matches returns an empty array; returned objects remain shared references.

**Explanation:** Filter removes inactive users directly from the original array and returns the first remaining user. With no match it returns undefined just like find.

**Human decision / reason (fill in):** ______

**Agent label:** follow_up | **Model/server outcome:** follow_up

**Feedback:** The answer incorrectly states that filter removes elements from the original array and returns the first remaining user, which is false. filter does not modify the original array and does not return the first match—it returns all matching elements. Additionally, it incorrectly claims that no match returns undefined, when in fact filter returns an empty array. The correct behavior is that filter returns all active users as a new array, and if no users are active, it returns an empty array. The answer fails to address the core behavior changes in return value and no-match case as required by the rubric.

**Human feedback-quality notes (fill in):** ______

## url-complete

Before:
```javascript
export function searchUrl(term) { return "/search?q=" + term; }
```
After:
```javascript
export function searchUrl(term) { return "/search?q=" + encodeURIComponent(term); }
```
**Question:** Why encode term as a URI component, and what protection does that not provide?

**Rubric:** Keep special characters within one query value.; Encode reserved characters such as ampersand so they cannot delimit extra parameters.; Encoding is not encryption, authentication or server input validation.

**Explanation:** Encoding keeps the search term within the q parameter. For example an ampersand in the term becomes %26 instead of starting another query parameter. This is reversible URL encoding, not encryption or authorization; the server still needs its own input validation.

**Human decision / reason (fill in):** ______

**Agent label:** pass | **Model/server outcome:** pass

**Feedback:** The answer correctly explains that encoding the term prevents reserved characters like ampersands from being interpreted as parameter delimiters, ensuring the query stays within the q parameter. It accurately identifies that URL encoding is reversible and does not provide encryption, authentication, or server input validation—aligning with the rubric. The explanation is clear, focused, and addresses both the mechanism and the limitations of encoding as requested.

**Human feedback-quality notes (fill in):** ______

## url-paraphrase

Before:
```javascript
export function searchUrl(term) { return "/search?q=" + term; }
```
After:
```javascript
export function searchUrl(term) { return "/search?q=" + encodeURIComponent(term); }
```
**Question:** Why encode term as a URI component, and what protection does that not provide?

**Rubric:** Keep special characters within one query value.; Encode reserved characters such as ampersand so they cannot delimit extra parameters.; Encoding is not encryption, authentication or server input validation.

**Explanation:** User text containing & or = should be carried as data in one URL value. encodeURIComponent escapes those characters before concatenation so they do not change the query structure. It does not make the content trusted or secret, so backend validation remains necessary.

**Human decision / reason (fill in):** ______

**Agent label:** pass | **Model/server outcome:** pass

**Feedback:** The answer correctly identifies that encoding the term with encodeURIComponent prevents reserved characters like & and = from being interpreted as query delimiters, preserving the structure of the URL. It accurately explains that encoding ensures special characters are safely included in a single query value without altering the URL's parsing behavior. The answer also correctly notes that encoding does not provide authentication, encryption, or input validation—emphasizing that backend validation is still necessary. This aligns fully with the rubric requirements.

**Human feedback-quality notes (fill in):** ______

## url-vague

Before:
```javascript
export function searchUrl(term) { return "/search?q=" + term; }
```
After:
```javascript
export function searchUrl(term) { return "/search?q=" + encodeURIComponent(term); }
```
**Question:** Why encode term as a URI component, and what protection does that not provide?

**Rubric:** Keep special characters within one query value.; Encode reserved characters such as ampersand so they cannot delimit extra parameters.; Encoding is not encryption, authentication or server input validation.

**Explanation:** It makes the URL safe and cleaner.

**Human decision / reason (fill in):** ______

**Agent label:** follow_up | **Model/server outcome:** follow_up

**Feedback:** The answer 'It makes the URL safe and cleaner' is vague and does not address the specific requirements in the rubric. It fails to explain how encoding protects against reserved characters like ampersand or how it maintains query integrity. It also does not acknowledge that encoding is not encryption, authentication, or server input validation. A correct explanation must explicitly connect encoding to URI safety, prevent parameter delimitation, and clarify the limitations of encoding. Without addressing these points, the reasoning is incomplete.

**Human feedback-quality notes (fill in):** ______

## url-misconception

Before:
```javascript
export function searchUrl(term) { return "/search?q=" + term; }
```
After:
```javascript
export function searchUrl(term) { return "/search?q=" + encodeURIComponent(term); }
```
**Question:** Why encode term as a URI component, and what protection does that not provide?

**Rubric:** Keep special characters within one query value.; Encode reserved characters such as ampersand so they cannot delimit extra parameters.; Encoding is not encryption, authentication or server input validation.

**Explanation:** Encoding encrypts the search term so only the server can read it. It makes all user input trusted and removes the need for server validation.

**Human decision / reason (fill in):** ______

**Agent label:** follow_up | **Model/server outcome:** follow_up

**Feedback:** The answer incorrectly claims encoding encrypts the search term and that it makes user input 'trusted' and removes the need for server validation. URI encoding does not encrypt data or provide authentication. It only ensures special characters are properly represented in a URL. The correct purpose is to prevent malformed URLs by safely including characters like spaces or ampersands. The answer fails to address the rubric points: it does not explain how encoding keeps special characters within a query value or prevents delimitation by reserved characters. It also falsely claims encoding replaces server input validation, which is a central misconception. Encoding is not encryption or input validation; it is a formatting step for safe transmission.

**Human feedback-quality notes (fill in):** ______

## set-complete

Before:
```javascript
export function uniqueTags(tags) { return [...tags]; }
```
After:
```javascript
export function uniqueTags(tags) { return [...new Set(tags)]; }
```
**Question:** How does the Set change this returned array, including ordering and a limitation?

**Rubric:** Remove duplicate values rather than just copy.; Set keeps unique values in first-insertion order and spread returns an array.; Case-sensitive strings or object identity still matter; no normalization/deep equality.

**Explanation:** The Set removes repeated tag values, then spread converts the Set back into an array. It preserves the first occurrence order rather than sorting, and does not mutate tags. String equality is case-sensitive, so Bug and bug stay distinct unless we normalize them.

**Human decision / reason (fill in):** ______

**Agent label:** pass | **Model/server outcome:** pass

**Feedback:** The Set ensures duplicate values are removed while preserving the first insertion order, and the spread operator converts the Set back into an array. This maintains order without sorting. However, string equality is case-sensitive, so 'Bug' and 'bug' are treated as distinct values—no normalization or deep equality is applied. This behavior correctly addresses the core requirement of removing duplicates while preserving order, but has a limitation in handling case-sensitive string comparisons.

**Human feedback-quality notes (fill in):** ______

## set-paraphrase

Before:
```javascript
export function uniqueTags(tags) { return [...tags]; }
```
After:
```javascript
export function uniqueTags(tags) { return [...new Set(tags)]; }
```
**Question:** How does the Set change this returned array, including ordering and a limitation?

**Rubric:** Remove duplicate values rather than just copy.; Set keeps unique values in first-insertion order and spread returns an array.; Case-sensitive strings or object identity still matter; no normalization/deep equality.

**Explanation:** Previously this just copied the list. Now each repeated primitive value is kept once, in the order it first appeared, and the result is a new array. Separate objects with equal-looking properties remain distinct because Set compares their identities; it is not deep deduplication.

**Human decision / reason (fill in):** ______

**Agent label:** pass | **Model/server outcome:** pass

**Feedback:** The change uses a Set to remove duplicates, preserving the order of first insertion, which means repeated primitive values are kept only once and in the order they first appear. The result is a new array. However, Set does not perform deep equality checks—objects with identical properties are still considered distinct if they are different references, so this is not a deep deduplication mechanism. This behavior correctly addresses the removal of duplicates for primitives but has a limitation when dealing with objects or complex data structures.

**Human feedback-quality notes (fill in):** ______

## set-vague

Before:
```javascript
export function uniqueTags(tags) { return [...tags]; }
```
After:
```javascript
export function uniqueTags(tags) { return [...new Set(tags)]; }
```
**Question:** How does the Set change this returned array, including ordering and a limitation?

**Rubric:** Remove duplicate values rather than just copy.; Set keeps unique values in first-insertion order and spread returns an array.; Case-sensitive strings or object identity still matter; no normalization/deep equality.

**Explanation:** The Set makes the collection better.

**Human decision / reason (fill in):** ______

**Agent label:** follow_up | **Model/server outcome:** follow_up

**Feedback:** The statement 'The Set makes the collection better' is vague and does not address the specific requirements of the question, such as how duplicates are removed, whether ordering is preserved, or what limitations exist. It fails to explain the mechanism (e.g., first-insertion order in Set) or any limitations (e.g., case sensitivity, no deep equality). A correct response must explicitly describe the behavior and constraints of using a Set to deduplicate primitive values.

**Human feedback-quality notes (fill in):** ______

## set-misconception

Before:
```javascript
export function uniqueTags(tags) { return [...tags]; }
```
After:
```javascript
export function uniqueTags(tags) { return [...new Set(tags)]; }
```
**Question:** How does the Set change this returned array, including ordering and a limitation?

**Rubric:** Remove duplicate values rather than just copy.; Set keeps unique values in first-insertion order and spread returns an array.; Case-sensitive strings or object identity still matter; no normalization/deep equality.

**Explanation:** Set sorts tags alphabetically and merges strings regardless of case. It also recursively compares object properties to remove every deep duplicate.

**Human decision / reason (fill in):** ______

**Agent label:** follow_up | **Model/server outcome:** follow_up

**Feedback:** The answer incorrectly claims that Set sorts tags alphabetically and merges strings regardless of case, which is not true. Sets in JavaScript maintain insertion order but do not sort or normalize strings by case. Additionally, the claim about recursively comparing object properties to remove deep duplicates is false—Set does not perform deep equality comparisons or recursive property checks. The actual behavior is that Set removes duplicates based on value equality, preserving insertion order, and does not alter string case or perform deep object comparisons. These statements contradict the documented behavior of JavaScript Sets.

**Human feedback-quality notes (fill in):** ______
