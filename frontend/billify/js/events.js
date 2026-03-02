const dashboard_url = "event/dashboard/"
const event_record_delete_url = "event/delete/"

// Modal functionality
const createEventBtn = document.getElementById("createEventBtn");
const createEventModal = document.getElementById("createEventModal");
const closeModalBtn = document.getElementById("closeModalBtn");
const cancelBtn = document.getElementById("cancelBtn");
const saveEventBtn = document.getElementById("saveEventBtn");
const eventForm = document.getElementById("eventForm");
const template = document.getElementById("template").content;
const event_body_wrapper = document.getElementById("event_table_body");

const calender_wrapper = document.querySelector('.calendar-wrapper')
let global_events = null

// Open modal
createEventBtn.addEventListener("click", () => {
  createEventModal.style.display = "flex";
});

// Close modal
const closeModal = () => {
  createEventModal.style.display = "none";
  eventForm.reset();
};

closeModalBtn.addEventListener("click", closeModal);
cancelBtn.addEventListener("click", closeModal);

// Save event
saveEventBtn.addEventListener("click", (e) => {
  e.preventDefault();
  if (eventForm.checkValidity()) {
    alert("Event created successfully!");
    closeModal();
  } else {
    eventForm.reportValidity();
  }
});

// Select all checkboxes
const selectAllCheckbox = document.getElementById("selectAll");
const eventCheckboxes = document.querySelectorAll(".event-checkbox");
const eventSpecialButton = [...document.querySelectorAll('.event-special-button')]

selectAllCheckbox.addEventListener("change", function () {
  eventCheckboxes.forEach((checkbox) => {
    checkbox.checked = this.checked;
  });
});

// Generate tickets action
const ticketIcons = document.querySelectorAll(".fa-ticket-alt");
ticketIcons.forEach((icon) => {
  icon.addEventListener("click", function () {
    alert("Generating tickets for this event...");
    // Here you would integrate with your PDF ticket generator
  });
});

eventSpecialButton.forEach(s_button => {
  s_button.addEventListener('click', (e) => {
    e.preventDefault()
  })
})


// Filter events by status
/* const statusFilter = document.getElementById("statusFilter");
statusFilter.addEventListener("change", function () {
  const status = this.value;
  const rows = document.querySelectorAll(".data-table tbody tr");

  rows.forEach((row) => {
    if (status === "all") {
      row.style.display = "";
    } else {
      const rowStatus = row
        .querySelector(".event-status")
        .classList.contains(`status-${status}`);
      row.style.display = rowStatus ? "" : "none";
    }
  });
}); */



// Generate report
const generateReportBtn = document.getElementById("generateReportBtn");
generateReportBtn.addEventListener("click", () => {
  alert("Generating event report...");
  // Here you would generate and download the report
});

// Close modal when clicking outside
window.addEventListener("click", (e) => {
  if (e.target === createEventModal) {
    closeModal();
  }
});

function populateDashboard(response) {
  //append category data to creation modal
  const categorySelect = document.querySelector('.createEventCategory#eventType')
  categorySelect.innerHTML = ''
  response.categories.forEach(category => {
    const option = document.createElement('option')
    option.value = category.id
    option.innerText = category.category
    categorySelect.appendChild(option)
  })
  const count_details = {
	  upcoming_count : 0,
	  ungoing_count: 0,
	  completed_count: 0,
	  event_count_this_week: 0
  }

  currentDate = new Date();
  //counts the upcoming, ongoing and completed events and adds the status to the event object
  global_events = response.events
  response.events.forEach((event) => {
    if (event.date > currentDate) {
      count_details.upcoming_count += 1;
      event.status = "upcoming";
    } else if (event.date < currentDate) {
      count_details.completed_count += 1;
      event.status = "completed";
    } else {
      count_details.ungoing_count += 1;
      event.status = "ungoing";
    }
    //count the weekly events here

    //end weekly count
  });
  populateEventCards(count_details)
  populateEventTable(response.events);
  populateEventCalender()
  activateSpecialTags()
}

function activateSpecialTags() {
  // Delete selected events
  const deleteSelectedBtn = document.getElementById("deleteSelectedBtn");
  deleteSelectedBtn.addEventListener("click", async () => {
    const selectedEvents = document.querySelectorAll(".event-checkbox:checked");
    if (selectedEvents.length === 0) {
      alert("Please select at least one event to delete.");
      return;
    }

    if (
      confirm(
        `Are you sure you want to delete ${selectedEvents.length} selected event(s)?`
      )
    ) {
      const id_list = []
      const timeout_id = {}

      selectedEvents.forEach((checkbox) => {
        const row = checkbox.closest("tr");
        row.style.opacity = "0.5";

        id_list.push(parseInt(row.dataset.id))

        timeout_id[row.dataset.id] = setTimeout(() => {
          row.remove();
        }, 700);
      });
      let value = await deleteEventRequest(id_list)
      for (const data_id in timeout_id) {
        if (timeout_id.hasOwnProperty(data_id)) {
          if (!value.ids.includes(data_id)) {
            clearTimeout(data_id)
            document.querySelector(`#event_table_body tr[data-id="${data_id}"]`).style.opacity = "1";
          }
        }
      }
    }
  });

  // Delete event action
  const deleteIcons = document.querySelectorAll(".fa-trash");
  deleteIcons.forEach((icon) => {
    icon.addEventListener("click", async function () {
      if (confirm("Are you sure you want to delete this event?")) {
        const row = this.closest("tr");
        row.style.opacity = "0.5";
        let value = await deleteEventRequest(row.dataset.id)
        setTimeout(() => {
          row.remove();
        }, 500);
        
      }
    });
  });
}
function populateEventCalender() {
  const days_in_week = 7
  global_events.forEach(event => {
    const calender_wrapper_children = [...calender_wrapper.children]
    calender_wrapper_children.forEach(calender_child => {
      const section_year = calender_child.dataset.year
      const section_month = calender_child.dataset.month
      const section_gap = calender_child.dataset.gap

      if ((section_year == event.date.getFullYear()) && (section_month == event.date.getMonth())) {
        //this means the event exist in that particular calendar month
        const calender_child_children = calender_child.querySelector('.calendar-grid').children
        calender_child_children[days_in_week + event.date.getDate() + parseInt(section_gap) - 1 ].classList.add('event', `${event.status}`)
      }
    })
  })
}
function populateEventCards(count_details) {
	const upcoming_count_holder = document.getElementById('upcoming_events_count')
	const ongoing_count_holder = document.getElementById('ongoing_events_count')
	const completed_count_holder = document.getElementById('completed_events_count')

	upcoming_count_holder.innerText = count_details.upcoming_count
	ongoing_count_holder.innerText = count_details.ungoing_count 
	completed_count_holder.innerText = count_details.completed_count
}
function populateEventTable(events) {
  if (!events.length) {
    fake_row = document.createElement("tr");
    fake_row.innerHTML =
      "<td colSpan=7>Your company has no events. Create events</td>";
    event_body_wrapper.appendChild(fake_row);
    return;
  }
  events.forEach((event) => {
    const event_row_template = template
      .getElementById("event_row")
      .cloneNode(true);

    const event_name = event_row_template.querySelector(".event_name");
    const event_date = event_row_template.querySelector(".event_datetime");
    const event_location = event_row_template.querySelector(".event_location");
    const event_attendees =
      event_row_template.querySelector(".event_attendees");
    const event_status = event_row_template.querySelector(".event-status");
    const event_action = event_row_template.querySelector(".action-icons");

    event_name.innerText = event.name;
    event_date.innerText = `${event.date
      .toDateString()
      .split(" ")
      .slice(1)
      .join(" ")} * ${event.date.toLocaleTimeString()}`;
    event_location.innerText = event.location;
    event_attendees.innerText = `${event.interestedPeople}/${event.total_slot}`;
    event_status.innerText = event.status;
    event_status.classList.add(`status-${event.status}`);
    event_row_template.dataset.id = event.id
    event_body_wrapper.appendChild(event_row_template);
  });
}
async function deleteEventRequest(id) {
  const response = await fetch(`${domain}${event_record_delete_url}`, {
    method: "post",
    headers: {
      Authorization:
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY3MjcxNzk0LCJpYXQiOjE3NjU5NzU3OTQsImp0aSI6IjA3Nzk4YjE0M2E4ZjQyMDM4MGEwYjRiOTYyODAxOTc0IiwidXNlcl9pZCI6IjEifQ.4yBA5QFFk-lC3OYiUIpcxCgExW3Vs-SirL5IuPCZhRs",
    },
    body: JSON.stringify({
      id: id
    })
  });
  if (!response.ok) {
    return
  }
  const data = await response.json()
  console.log(data)
  return data
}