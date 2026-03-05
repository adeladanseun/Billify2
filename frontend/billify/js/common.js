const domain = "http://localhost:8000/"

const page_header = document.getElementById("page_header");

function setDateObject(object) {
  if (object.date_created) {
    object.date_created = new Date(object.date_created);
  }
  if (object.last_modified) {
    object.last_modified = new Date(object.last_modified);
  }
  if (object.date) {
    object.date = new Date(object.date);
  }
}

async function getDashboardData() {
  const request = await fetch(`${domain}${dashboard_url}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("access_token")}`,
    },
  });

  // 1. Check if the response status is in the 200-299 range
  if (!request.ok) {
    console.error(`Request failed with status: ${request.status}`);

    // 1. Capture the current path and any existing query parameters
    const currentPath = window.location.pathname + window.location.search;

    // 2. Reroute to login with the 'next' parameter encoded
    window.location.href = `/auth/html/login.html?next=${encodeURIComponent(currentPath)}`;
    return;
  }

  const response = await request.json();
  console.log(response);

  const user_info = [...page_header.querySelector(".user-details").children];
  user_info.forEach((element) => {
    if (element.classList.contains("user-name")) {
      element.innerText = response.user.username;
    } else if (element.classList.contains("user-role")) {
      element.innerText = response.owner ? "Owner" : "Admin";
    }
  });
  if (response.events) {
    response.events.forEach(setDateObject);
  }
  if (response.products) {
    response.products.forEach(setDateObject);
  }
  if (response.purchases) {
    response.purchases.forEach(setDateObject);
  }
  if (response.event_transactions) {
    response.event_transactions.forEach(setDateObject);
  }
  if (response.product_transactions) {
    response.product_transactions.forEach(setDateObject);
  }
  if (response.upcoming_event) {
    response.upcoming_event.forEach(setDateObject);
  }

  populateDashboard(response);
  activateFilters();
}

function naturalise_id(id) {
  let id_str = id.toString();
  if (!transaction_id_length) {
    transaction_id_length = 5;
  }
  if (id_str.length < transaction_id_length) {
    id_str =
      (10 ** (transaction_id_length - id_str.length))
        .toString()
        .replace("1", "") + id_str;
  }
  return transaction_id_prefix + id_str;
}

function activateFilters() {
  const filters = [...document.getElementsByClassName('filter')]
  filters.forEach(filter => {
    filter.addEventListener('change', (e)=>{
      const controlled_table_children = [...document.getElementById(`${filter.dataset.id}`).children]
      controlled_table_children.forEach(row => {
        if (filter.value == 'all') {
          //show all the elements in the table
          row.classList.remove('hide')
        } else {
          if (!row.querySelector('.status').classList.contains(`status-${filter.value}`)) {
            row.classList.add('hide')
          } else {
            row.classList.remove('hide')
          }
        }
      })
    })
  })
}

getDashboardData()
