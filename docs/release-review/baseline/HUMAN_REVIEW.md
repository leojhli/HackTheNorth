# Assessment review worksheet

Actual local model results against 20 fixed synthetic explanations. Expected labels were authored by the coding agent before this run. This is not completed human review or a production accuracy estimate.

Reviewer: ______  Date: ______

For each case, independently judge the code/answer before considering the model feedback. Record pass, follow-up or unable-to-assess, whether feedback is correct, and whether it reveals too much. Disagreements stay visible.

## Run summary

```json
{
  "total": 20,
  "matching_agent_labels": 19,
  "false_passes": 1,
  "complete_answers_not_passed": 0,
  "operational_failures": 0,
  "evaluation_p95_seconds": 4.453,
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

**Feedback:** Your explanation correctly identifies that the change preserves zero and distinguishes between nullish coalescing and the logical OR operator. You also correctly note that the function still accepts strings or out-of-range numbers, which is not volume validation. This is a complete and accurate explanation.

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

**Feedback:** Your explanation correctly identifies that the nullish coalescing operator (??) preserves explicit falsy values like 0, and that a numeric range check would still be needed. This addresses both the intent and mechanism of the change.

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

**Feedback:** The answer is vague and does not provide the necessary details. It should explain how the new operator handles defaults better and address the validation that is still missing.

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

**Agent label:** follow_up | **Model/server outcome:** pass

**Feedback:** Your explanation is clear and correct. You correctly identified that the new operator rejects all falsy inputs, including zero and false, and replaces them with 50. Additionally, you noted that the code does not include validation that the volume is between 0 and 100, which is a valid point.

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

**Feedback:** Your explanation accurately captures the behavior of the code, including the ordering of operations and the handling of errors. You correctly identified that await ensures the save operation completes before notify is called, and that a rejected save prevents notify from executing.

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

**Feedback:** Your explanation correctly captures the intent, mechanism, and reasoning behind the code change. You've explained that await ensures the save operation completes before notifying, and that a rejected save propagates and prevents notify. This aligns with the rubric and evidence provided.

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

**Feedback:** The answer is too vague and does not explain the mechanism or the intended behavior of the code. It should clarify that await ensures the save operation completes before notify is called, and that a rejected save prevents notify from executing unless handled.

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

**Feedback:** The answer does not correctly explain the intent, mechanism, and behavior of the code. It incorrectly states that notify runs even if the save promise rejects, which contradicts the behavior of await. Please provide a correct explanation of how await works in this context and what happens if saving fails.

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

**Feedback:** Your explanation accurately captures the changes in behavior when `find` is replaced with `filter`. You correctly identified that `filter` returns all matching elements, builds a new array, and handles no matches by returning an empty array. Your reasoning is clear and aligns with the provided evidence.

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

**Feedback:** Your explanation correctly captures the key changes in behavior when `find` is replaced with `filter`. You accurately describe how all matching elements are collected into a new array and how zero matches result in an empty array. Your reasoning is clear and aligns with the provided evidence.

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

**Feedback:** The answer does not address how the return value and no-match case change when using filter instead of find. It only states that filter is more effective, which is not relevant to the question asked.

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

**Feedback:** The answer incorrectly states that filter removes inactive users directly from the original array and returns the first remaining user. This is not accurate. Filter does not modify the original array; it returns a new array. Additionally, the answer does not address how the return value and no-match case change when using filter instead of find.

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

**Feedback:** Your explanation correctly identifies the purpose of URI encoding and the mechanism used. You also correctly note that encoding is not encryption, authentication, or server input validation. This is a comprehensive and accurate explanation.

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

**Feedback:** Your explanation correctly identifies the purpose of encoding the query term and the limitations of encoding alone. You've explained that encoding prevents special characters from altering the query structure and that backend validation is still necessary. This is a comprehensive and accurate explanation.

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

**Feedback:** The answer is vague and does not address the specific reasons for encoding the query term as a URI component. It also does not explain the protection provided by encoding.

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

**Feedback:** Encoding a URI component ensures that special characters are properly escaped, preventing them from delimiting extra parameters. It does not encrypt or validate the input; it merely prepares it for safe use in a URL.

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

**Feedback:** Your explanation accurately captures the behavior of the Set and how it affects the returned array. You correctly identified that it removes duplicates, preserves order, and does not mutate the input. You also correctly noted that string equality is case-sensitive. Good job!

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

**Feedback:** Your explanation accurately captures the behavior of using a Set to remove duplicates while preserving order and handling primitive values. You correctly noted that separate objects with equal-looking properties remain distinct, which is a key limitation of this approach.

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

**Feedback:** The answer is too vague and does not address the specific changes made by the Set, such as removing duplicates, maintaining order, and the limitation of case-sensitive strings or object identity.

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

**Feedback:** The answer contains several inaccuracies. Set does not sort tags alphabetically or merge strings regardless of case. It also does not recursively compare object properties. Please provide a correct explanation of how Set changes the returned array, including ordering and limitations.

**Human feedback-quality notes (fill in):** ______
