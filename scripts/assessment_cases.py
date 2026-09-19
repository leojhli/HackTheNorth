"""Frozen synthetic evaluation set v1. Expected labels are agent-authored, not human review.

Each group has a complete answer, a paraphrase, a vague answer and a central misconception.
These changes were not in the initial SQL/null-guard/sort smoke checks.
"""
CASES = [
    dict(id='nullish', concept='Preserving falsy values',
         before='export function volume(value) { return value || 50; }',
         after='export function volume(value) { return value ?? 50; }',
         question='How does changing || to ?? affect the fallback, and what validation is still missing?',
         rubric=['Preserve explicit falsy values such as zero.', 'Nullish coalescing falls back only for null or undefined.', 'Explain a retained value or missing type/range validation.'],
         answers=[
             ('complete', 'pass', 'The change preserves a requested volume of zero instead of replacing it with 50. Nullish coalescing uses the fallback only for null or undefined; || uses it for any falsy value. It still accepts strings or out-of-range numbers, so this is not volume validation.'),
             ('paraphrase', 'pass', 'An explicit 0 now stays 0, so muting works. Only a missing value, null or undefined, becomes 50. False and an empty string also survive now, so a numeric range check would still be needed.'),
             ('vague', 'follow_up', 'The new operator handles the defaults better.'),
             ('misconception', 'follow_up', 'The new operator rejects all falsy inputs, including zero and false, and replaces them with 50. It also validates that volume is between 0 and 100.'),
         ]),
    dict(id='await', concept='Waiting for asynchronous completion',
         before='export async function saveThenNotify(save, notify) { save(); notify(); }',
         after='export async function saveThenNotify(save, notify) { await save(); notify(); }',
         question='What ordering does await establish here, and what happens if saving fails?',
         rubric=['Notify after save completes successfully.', 'Await suspends this async function until the returned promise settles without blocking the thread.', 'A rejected save propagates and prevents notify unless handled.'],
         answers=[
             ('complete', 'pass', 'Notification now happens after successful saving. Await pauses this async function until the promise returned by save fulfills; other work can still run on the event loop. If save rejects, the function rejects and notify is skipped because there is no catch.'),
             ('paraphrase', 'pass', 'We stop racing the notification against the save operation: the continuation runs when the save promise resolves. This yields control rather than freezing the whole JavaScript thread. A save rejection escapes to the caller and this code never reaches notify in that case.'),
             ('vague', 'follow_up', 'Await makes the asynchronous part work properly.'),
             ('misconception', 'follow_up', 'Await blocks the entire JavaScript thread until save finishes. Notify runs even if the save promise rejects because await automatically catches errors.'),
         ]),
    dict(id='filter', concept='Keeping all matching elements',
         before='export function activeUsers(users) { return users.find(user => user.active); }',
         after='export function activeUsers(users) { return users.filter(user => user.active); }',
         question='How do the return value and no-match case change when find becomes filter?',
         rubric=['Return all active matches rather than one.', 'Filter builds a new array of every element whose predicate is truthy.', 'No matches returns an empty array; returned objects remain shared references.'],
         answers=[
             ('complete', 'pass', 'The function now returns all active users instead of only the first one. Filter runs the predicate and builds an array containing every match. With no matches it returns [], whereas find returned undefined. The result array is new, but its user objects are not cloned.'),
             ('paraphrase', 'pass', 'Every entry with a truthy active property is collected into a fresh array, instead of stopping at the first matching user. Zero matches produces an empty array, so callers must now handle a collection. Editing an object inside that array still edits the same object referenced by the original users array.'),
             ('vague', 'follow_up', 'It filters the users more effectively.'),
             ('misconception', 'follow_up', 'Filter removes inactive users directly from the original array and returns the first remaining user. With no match it returns undefined just like find.'),
         ]),
    dict(id='url', concept='Encoding a query value',
         before='export function searchUrl(term) { return "/search?q=" + term; }',
         after='export function searchUrl(term) { return "/search?q=" + encodeURIComponent(term); }',
         question='Why encode term as a URI component, and what protection does that not provide?',
         rubric=['Keep special characters within one query value.', 'Encode reserved characters such as ampersand so they cannot delimit extra parameters.', 'Encoding is not encryption, authentication or server input validation.'],
         answers=[
             ('complete', 'pass', 'Encoding keeps the search term within the q parameter. For example an ampersand in the term becomes %26 instead of starting another query parameter. This is reversible URL encoding, not encryption or authorization; the server still needs its own input validation.'),
             ('paraphrase', 'pass', 'User text containing & or = should be carried as data in one URL value. encodeURIComponent escapes those characters before concatenation so they do not change the query structure. It does not make the content trusted or secret, so backend validation remains necessary.'),
             ('vague', 'follow_up', 'It makes the URL safe and cleaner.'),
             ('misconception', 'follow_up', 'Encoding encrypts the search term so only the server can read it. It makes all user input trusted and removes the need for server validation.'),
         ]),
    dict(id='set', concept='Removing duplicate primitive values',
         before='export function uniqueTags(tags) { return [...tags]; }',
         after='export function uniqueTags(tags) { return [...new Set(tags)]; }',
         question='How does the Set change this returned array, including ordering and a limitation?',
         rubric=['Remove duplicate values rather than just copy.', 'Set keeps unique values in first-insertion order and spread returns an array.', 'Case-sensitive strings or object identity still matter; no normalization/deep equality.'],
         answers=[
             ('complete', 'pass', 'The Set removes repeated tag values, then spread converts the Set back into an array. It preserves the first occurrence order rather than sorting, and does not mutate tags. String equality is case-sensitive, so Bug and bug stay distinct unless we normalize them.'),
             ('paraphrase', 'pass', 'Previously this just copied the list. Now each repeated primitive value is kept once, in the order it first appeared, and the result is a new array. Separate objects with equal-looking properties remain distinct because Set compares their identities; it is not deep deduplication.'),
             ('vague', 'follow_up', 'The Set makes the collection better.'),
             ('misconception', 'follow_up', 'Set sorts tags alphabetically and merges strings regardless of case. It also recursively compares object properties to remove every deep duplicate.'),
         ]),
]
