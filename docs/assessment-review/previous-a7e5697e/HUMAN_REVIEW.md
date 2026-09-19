# Assessment review worksheet

Actual local model results against 20 fixed synthetic explanations. Expected labels were authored by the coding agent before this run. This is not completed human review or a production accuracy estimate.

Reviewer: ______  Date: ______

For each case, independently judge the code/answer before considering the model feedback. Record pass, follow-up or unable-to-assess, whether feedback is correct, and whether it reveals too much. Disagreements stay visible.

## Run summary

```json
{
  "total": 20,
  "matching_agent_labels": 16,
  "false_passes": 0,
  "complete_answers_not_passed": 1,
  "operational_failures": 4,
  "evaluation_p95_seconds": 31.11,
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

**Feedback:** Your explanation is clear and correct. You accurately described how the change preserves zero and the difference between nullish coalescing and the old OR operator. You also correctly identified that the function still accepts invalid types or values, which is a limitation.

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

**Feedback:** Your explanation is clear and correct. You accurately described how the nullish coalescing operator ?? affects the fallback value and identified that a numeric range check is still needed to validate the input.

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

**Feedback:** The answer does not provide a clear explanation of how the new operator handles defaults better or address the preservation of explicit falsy values. It also does not explain the difference between || and ??.

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

**Feedback:** The answer is incorrect. The nullish coalescing operator (??) does not reject falsy inputs like zero and false. It only falls back to the default value when the input is null or undefined. The answer also mentions a missing validation for the volume range, which is not addressed in the code change.

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

**Feedback:** Your explanation accurately captures the behavior of the code, including the ordering of operations, the role of await, and the handling of rejections. Well done!

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

**Feedback:** Your explanation accurately captures the intent, mechanism, and limitation of the code. You correctly describe how await ensures that notify runs only after save completes successfully, and how a rejected save prevents notify from running. Your reasoning is clear and consistent with the code's behavior.

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

**Feedback:** The answer is too vague and does not address the key aspects of the question. It should explain the ordering established by await, what happens if saving fails, and how await prevents the thread from blocking.

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

**Feedback:** The explanation contradicts the behavior of await and error handling. Await does not block the thread, and notify does not run if save rejects without proper error handling.

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

**Feedback:** Your explanation accurately captures the changes in behavior when `find` is replaced with `filter`. You correctly identified that `filter` returns all matching elements, builds a new array, and handles no matches by returning an empty array. Your reasoning is clear and consistent with the provided evidence.

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

**Feedback:** Your explanation accurately captures the behavior change from using `find` to `filter`. You correctly identified that `filter` collects all matching elements into a new array, handles zero matches by returning an empty array, and maintains shared references to objects. This explanation is clear and comprehensive.

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

**Agent label:** follow_up | **Model/server outcome:** operational_failure

**Feedback:** invalid_local_response

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

**Feedback:** The intent, mechanism, and reasoning provided are incorrect. Filter does not remove elements from the original array, and it does not return the first remaining user. The return value and no-match case do not match the behavior of find.

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

**Feedback:** Your explanation correctly identifies the purpose of encoding the search term as a URI component, the mechanism of using `encodeURIComponent`, and the limitation that encoding alone does not provide encryption, authentication, or server input validation. This is a complete and accurate answer.

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

**Feedback:** The answer is vague and does not address the specific reasons for encoding the query term as a URI component. It also fails to mention the protection against reserved characters and the fact that encoding is not encryption, authentication, or server input validation.

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

**Feedback:** The answer contains a central contradiction. Encoding does not encrypt the search term; it ensures that special characters are correctly interpreted by the server. The answer also does not explain the protection provided by encoding.

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

**Feedback:** Your explanation accurately captures the purpose, mechanism, and limitation of using a Set to remove duplicate values while preserving order and case-sensitive string equality. Well done!

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

**Agent label:** pass | **Model/server outcome:** operational_failure

**Feedback:** ungrounded_local_pass

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

**Agent label:** follow_up | **Model/server outcome:** operational_failure

**Feedback:** invalid_local_response

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

**Agent label:** follow_up | **Model/server outcome:** operational_failure

**Feedback:** invalid_local_response

**Human feedback-quality notes (fill in):** ______
