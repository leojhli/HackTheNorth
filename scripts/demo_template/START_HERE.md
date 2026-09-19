# Your first CodeProof demo

This is a small event signup website. You do not need to understand every file.
It has five available spots. You can add or remove guests using the buttons.
It is a practice app, not a real booking service; refreshing starts over.

## 1. See the website

Open a terminal in this folder and run:

```powershell
./start-demo.ps1
```

Then visit http://127.0.0.1:8010. This preview is separate from CodeProof on
port 8000. Keep its terminal open. Press Add one guest five times: the button
stops at five. Remove a guest and you can add someone again.

## 2. Find the one change

Open `src/canJoin.js`. This is the only file with an uncommitted change.
VS Code's Source Control view shows the old and new versions:

```javascript
// Before: everyone is allowed, even if the event is full.
return true;

// After: say no if the event is full.
if (guestCount >= capacity) return false;
return true;
```

In everyday language: "If the room is full, say no. Otherwise, say yes."

- `guestCount` is how many people have signed up.
- `capacity` is the maximum number of people (five here).
- `>=` means "greater than or equal to".
- `if` checks whether something is true.
- `return` gives the answer back and stops this function.
- `true` means yes; `false` means no.
- Before the fix, the function always said yes, even when the room was full.
- After the fix, five or more guests means no. Fewer than five means yes.
- This helper only answers yes/no. The button code in `main.js` adds the guest.

| Current guests | Maximum | Can another guest join after the fix? |
| --- | --- | --- |
| 0 | 5 | Yes |
| 4 | 5 | Yes: the next guest takes the last spot |
| 5 | 5 | No: already full |

## 3. Start CodeProof

With this folder open as the VS Code workspace:

1. Run **CodeProof: Connect and start scoped session** from Ctrl+Shift+P.
2. Enter your local token from the main CodeProof project's `.env`.
3. Select **Create project**, accept the folder name, and enter scope `src`.
4. Click **Start session**.
5. Run **CodeProof: Review saved changes** and approve the preview.
6. Open **CodeProof: Open checkpoint** and answer in your own words.

There is no need to make another edit or commit the prepared change.

## 4. Practice simple questions

These are practice examples, not canned model questions:

- What problem does the change fix?
- What does the `if` check do when the event is full?
- Can another guest join when there are already five guests?
- What happens when only four guests have signed up?

A plain-language explanation you can study, then put into your own words:

"This stops us adding more people when the event is full. If the number is
five or more, it returns false, which means no. With four guests the check
is false, so it reaches return true and someone can join. This function only
checks for room; the button code actually adds the person."

No advanced JavaScript knowledge is needed to explain that change. The model
still generates the real question and may ask a follow-up. If it asks about
unrelated advanced topics or gives incorrect feedback, that is a product
quality issue, not something you are expected to know for this exercise.

## What the other files do

| File | Job |
| --- | --- |
| `index.html` | Page text and buttons |
| `styles.css` | Colors, spacing and phone layout |
| `src/event.js` | Event name and five-person capacity |
| `src/main.js` | Connect buttons to the counter |
| `src/canJoin.js` | The tiny yes/no check you will explain |
| `serve.py` / `start-demo.ps1` | Start the local website preview |

The other files are already committed, so the checkpoint captures only the
small changed helper. Nothing is sent automatically and no passing history
has been created for you. Each generator run makes a separate practice folder.
