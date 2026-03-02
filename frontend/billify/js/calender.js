// This tracks the "Middle" month of our 3-month view
let baseDate = new Date();

function renderThreeMonths() {
  const year = baseDate.getFullYear();
  const month = baseDate.getMonth();

  // Update the header label
  document.getElementById("view-label").innerText = `${baseDate.toLocaleString(
    "default",
    { month: "long" }
  )} ${year}`;

  // Render the three months
  generateCalendar("prev-month", new Date(year, month - 1, 1));
  generateCalendar("curr-month", new Date(year, month, 1));
  generateCalendar("next-month", new Date(year, month + 1, 1));
}
function changeViewForward() {
  changeView(1)
  if (populateEventCalender) {
    populateEventCalender()
  }
}
function changeViewBackward() {
  changeView(-1);
  if (populateEventCalender) {
    populateEventCalender();
  }
}
function changeView(direction) {
  // Moves the view by 3 months forward or backward
  baseDate.setMonth(baseDate.getMonth() + direction * 3);//changing the number 3 should after how many months your forward and backward change by
  renderThreeMonths();
}

function generateCalendar(targetId, date) {
  const container = document.getElementById(targetId);
  const year = date.getFullYear();
  const month = date.getMonth();
  const monthName = date.toLocaleString("default", { month: "long" });
  
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  
  container.dataset.year = year
  container.dataset.month = month
  container.dataset.gap = firstDay

  let html = `<div class="header">${monthName} ${year}</div>`;
  html += `<div class="calendar-grid">`;

  ["S", "M", "T", "W", "T", "F", "S"].forEach((d) => {
    html += `<div class="day-name">${d}</div>`;
  });

  for (let i = 0; i < firstDay; i++) {
    html += `<div class="day"></div>`;
  }

  const today = new Date();
  for (let day = 1; day <= daysInMonth; day++) {
    const isToday =
      today.getDate() === day &&
      today.getMonth() === month &&
      today.getFullYear() === year;
    html += `<div class="day ${isToday ? "today" : ""}">${day}</div>`;
  }

  html += `</div>`;
  container.innerHTML = html;
}

// Initial Call
renderThreeMonths();


//get previous and next calender view clickable and add event listener
const back = document.getElementById('calender-back')
const forward = document.getElementById('calender-forward')

back.addEventListener('click', changeViewBackward)
forward.addEventListener('click', changeViewForward)