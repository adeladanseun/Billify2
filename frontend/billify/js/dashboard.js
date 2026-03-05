const dashboard_url = "user/dashboard/"

// Simple JavaScript for interactivity

const dashboard_cards = document.getElementById("dashboard_cards"); //contains the summary id for receipts, transactions, events, products
const transactions_body_table = document.getElementById("transactions");
const upcoming_events = document.getElementById("upcoming_events");
const transaction_id_length = 5;
const transaction_id_prefix = "#TR-";



function transaction_row_generator(data, company) {
  //<td><span class="status status-completed">Completed</span></td>
  const transaction_row = document.createElement("tr");
  const transaction_id = document.createElement("td");
  transaction_id.innerText = naturalise_id(data.id);
  transaction_row.appendChild(transaction_id);

  const transaction_name = document.createElement("td");
  transaction_name.innerText = data.name;
  transaction_row.appendChild(transaction_name);

  const transaction_date = document.createElement("td");
  transaction_date.innerText = new Date(data.last_modified)
    .toDateString()
    .split(" ")
    .slice(1)
    .join(" ");
  transaction_row.appendChild(transaction_date);

  const transaction_value = document.createElement("td");
  transaction_value.innerText = `${parseFloat(data.price).toLocaleString()}${
    company.currency
  }`;
  transaction_row.appendChild(transaction_value);

  const transaction_status = document.createElement("td");
  const transaction_status_span = document.createElement("span");
  const data_status_string = data.status.toLowerCase();
  transaction_status.appendChild(transaction_status_span);
  transaction_status_span.classList.add("status");
  transaction_status_span.classList.add(
    `status-${data_status_string.startsWith("pend") ? "pending" : "completed"}`
  );
  transaction_status_span.innerText = data_status_string.startsWith("pend")
    ? "Pending"
    : "Completed";
  transaction_row.appendChild(transaction_status);

  return transaction_row;
}
function upcoming_event_row_generator(upcoming_event) {
  const row = document.createElement("tr");

  const name = document.createElement("td");
  name.innerText = upcoming_event.name;
  row.appendChild(name);

  const date = document.createElement("td");
  date.innerText = upcoming_event.date.toDateString().split(" ").slice(1).join(" ");
  row.appendChild(date);

  const location = document.createElement("td");
  location.innerText = upcoming_event.location;
  row.appendChild(location);

  const attendees = document.createElement("td");
  attendees.innerText = upcoming_event.interestedPeople;
  row.appendChild(attendees);

  return row;
}
// Card hover effect
/* const cards = document.querySelectorAll(".card");
cards.forEach((card) => {
  card.addEventListener("mouseenter", () => {
    card.style.transform = "translateY(-5px)";
  });
  card.addEventListener("mouseleave", () => {
    card.style.transform = "translateY(0)";
  });
}); */

// Navigation active state
const navItems = document.querySelectorAll(".nav-item");
navItems.forEach((item) => {
  item.addEventListener("click", function (e) {
    //e.preventDefault();
    navItems.forEach((nav) => nav.classList.remove("active"));
    this.classList.add("active");
  });
});
//fetch data from backend


function populateDashboard(response) {
  

  const transactions = [
    ...response.event_transactions,
    ...response.product_transactions,
  ];
  const dashboard_cards_children = [...dashboard_cards.children];
  dashboard_cards_children.forEach((element) => {
    let count = element.querySelector(".count");
    if (element.classList.contains("receipts")) {
      count.innerText = response.receipt_ticket_count;
    } else if (element.classList.contains("transactions")) {
      let total_amount = 0;
      transactions.forEach((event_purchase) => {
        total_amount += parseFloat(event_purchase.price);
      });
      count.innerText = `${total_amount.toLocaleString()}${
        response.company.currency
      }`;
    } else if (element.classList.contains("events")) {
      count.innerText = response.events_count;
    } else if (element.classList.contains("products")) {
      count.innerText = response.products_count;
    } else {
      console.log(
        `${element} present but not used to store data from dashboard api`
      );
    }
  });

  transactions.forEach((transaction) => {
    transactions_body_table.appendChild(
      transaction_row_generator(transaction, response.company)
    );
  });
  response.upcoming_event.forEach((event) => {
    upcoming_events.appendChild(upcoming_event_row_generator(event));
  });
}
