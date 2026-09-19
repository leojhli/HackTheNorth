import { event } from "./event.js";
import { canJoin } from "./canJoin.js";

let guestCount = 0;

const count = document.querySelector("#guest-count");
const status = document.querySelector("#status");
const join = document.querySelector("#join");
const leave = document.querySelector("#leave");

document.querySelector("#event-title").textContent = event.name;
document.querySelector("#capacity").textContent = event.capacity;

function updatePage() {
  count.textContent = guestCount;
  join.disabled = !canJoin(guestCount, event.capacity);
  leave.disabled = guestCount === 0;
  status.textContent = canJoin(guestCount, event.capacity)
    ? "There is room for another guest."
    : "All spots are taken!";
}

join.addEventListener("click", () => {
  if (canJoin(guestCount, event.capacity)) {
    guestCount = guestCount + 1;
    updatePage();
  }
});

leave.addEventListener("click", () => {
  if (guestCount > 0) {
    guestCount = guestCount - 1;
    updatePage();
  }
});

document.querySelector("#reset").addEventListener("click", () => {
  guestCount = 0;
  updatePage();
});

updatePage();
