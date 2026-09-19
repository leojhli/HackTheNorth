# Assessment review worksheet

Actual local model results against 20 fixed synthetic explanations. Expected labels were authored by the coding agent before this run. This is not completed human review or a production accuracy estimate.

Reviewer: ______  Date: ______

For each case, independently judge the code/answer before considering the model feedback. Record pass, follow-up or unable-to-assess, whether feedback is correct, and whether it reveals too much. Disagreements stay visible.

## Run summary

```json
{
  "total": 20,
  "matching_agent_labels": 15,
  "false_passes": 0,
  "complete_answers_not_passed": 1,
  "operational_failures": 4,
  "evaluation_p95_seconds": 5.672,
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

**Agent label:** pass | **Model/server outcome:** pass

**Feedback:** Your explanation is correct. You accurately identified that `??` preserves zero while `||` would not, and you correctly noted the lack of input validation.

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

**Feedback:** Your explanation is correct. You accurately identified how `??` preserves explicit falsy values like 0 and correctly noted that additional validation for non-numeric types would be needed.

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

**Agent label:** follow_up | **Model/server outcome:** operational_failure

**Feedback:** invalid_local_response

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

**Agent label:** follow_up | **Model/server outcome:** operational_failure

**Feedback:** invalid_local_response

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

**Feedback:** Your explanation correctly identifies the ordering established by `await` and the consequence of a failed save. The code will indeed skip `notify` if `save` rejects because there is no `try-catch` block to handle the error.

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

**Feedback:** Your explanation correctly identifies the ordering established by 'await' and the consequence of a failed save. The code ensures notify only runs after save completes successfully, and any rejection stops execution before reaching notify.

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

**Agent label:** follow_up | **Model/server outcome:** operational_failure

**Feedback:** invalid_local_response

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

**Feedback:** Your statement that 'await automatically catches errors' is incorrect. In JavaScript, `await` does not catch errors; if the awaited promise rejects, it throws an exception that halts execution unless wrapped in a try-catch block. Consequently, `notify()` will NOT run if `save()` fails because the function stops before reaching that line. To ensure `notify` runs even on failure, you would need to wrap both calls in a try-catch block or use Promise.all with error handling.

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

**Feedback:** Your explanation correctly covers the return value differences between `find` and `filter`, including the no-match case. You have accurately described the mechanism of building a new array while preserving object references. This is a complete and correct assessment.

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

**Feedback:** Your explanation is accurate and covers the key differences between `find` and `filter`. You correctly identified that `filter` returns all matching elements, handles zero matches by returning an empty array, and maintains object references. No further questions needed.

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

**Feedback:** Your answer is too vague. To pass, you must explain that `find` returns only the first matching user (or undefined if none), whereas `filter` returns a new array containing all users who match the condition. Specifically, mention what happens when there are no active users.

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

**Feedback:** Your explanation contains a central contradiction: you claim `filter` returns `undefined` like `find`, but `filter` actually returns an empty array `[]` when no elements match. Additionally, you stated it returns 'the first remaining user', whereas `filter` returns an array containing ALL users that match the condition, not just the first one.

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

**Feedback:** Your explanation accurately covers the purpose of URI component encoding, the specific protection it offers against parameter splitting, and its limitations regarding security. You have correctly identified all key aspects of the concept without gaps.

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

**Agent label:** pass | **Model/server outcome:** follow_up

**Feedback:** Your explanation correctly identifies that `encodeURIComponent` prevents special characters like `&` and `=` from splitting the query string. However, you did not explicitly state the specific limitation regarding what it fails to protect against (e.g., that it does not prevent injection if the backend blindly trusts the encoded string). Please explain exactly which type of protection is missing.

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

**Agent label:** follow_up | **Model/server outcome:** operational_failure

**Feedback:** invalid_local_response

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

**Feedback:** Your answer contains several critical misconceptions. First, `encodeURIComponent` does not encrypt data; it simply transforms characters to be safe for URLs. Second, it does not make user input 'trusted'; you still need to validate inputs on the server regardless of encoding. Third, without encoding, special characters like `&` or `/` would break the URL structure by creating new parameters or paths instead of being part of the query value. Please explain how encoding handles reserved characters and why it is not a substitute for input validation.

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

**Feedback:** Your explanation correctly identifies that `Set` removes duplicates while preserving insertion order and that string comparison is case-sensitive. You have addressed all rubric dimensions: the deduplication mechanism, the ordering behavior, and the limitation regarding case sensitivity.

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

**Feedback:** Your explanation is accurate and covers all required dimensions: the removal of duplicates, preservation of insertion order, and the distinction between primitive deduplication and object identity. You have successfully explained the behavior and its limitations.

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

**Feedback:** Your answer is too vague. To pass, you must explain exactly how `Set` removes duplicates compared to a simple array spread, mention that it preserves the order of first insertion, and note any limitations (like case sensitivity or object identity).

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

**Feedback:** Your explanation contains several incorrect claims. First, a Set does not sort values alphabetically; it maintains the order in which elements are added. Second, for primitive values like strings, comparisons are case-sensitive (e.g., 'a' and 'A' are different). Third, a Set only checks reference equality for objects, not deep property comparison. Please explain how the code actually handles duplicates and ordering.

**Human feedback-quality notes (fill in):** ______
