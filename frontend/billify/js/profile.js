// Fetch user profile info from API
  fetch(`${DOMAIN}/user/api/profile/`)
    .then((response) => response.json())
    .then((data) => {
      // Set user info
      document.getElementById("profile_name").textContent = data.username || "";
      document.getElementById("profile_email").textContent = data.email || "";
      document.getElementById("profile_fullname").textContent =
        `${data.first_name || ""} ${data.last_name || ""}`.trim();
      // Avatar
      let avatarText =
        data.username && data.username.length > 0
          ? data.username[0].toUpperCase()
          : "U";
      document.getElementById("profile_avatar").textContent = avatarText;
      // Companies
      const memberships = Array.isArray(data.companies) ? data.companies : [];
      const container = document.getElementById("company_memberships");
      container.innerHTML = "";
      if (memberships.length === 0) {
        container.innerHTML =
          '<p style="color:var(--danger)">No company memberships found.</p>';
      } else {
        memberships.forEach((company) => {
          const div = document.createElement("div");
          div.className = "company-card";
          div.innerHTML = `
            <div class="company-title">${company.company_name}</div>
            <div class="company-meta">Currency: ${company.currency} | Phone: ${company.phone_number}</div>
            <div class="company-meta">Address: ${company.address || "N/A"} | Zip: ${company.zip || "N/A"}</div>
            <div class="company-status">${company.is_owner ? "Owner" : company.is_staff ? "Staff" : "Member"}</div>
          `;
          container.appendChild(div);
        });
      }
    })
    .catch((err) => {
      document.getElementById("profile_name").textContent =
        "Error loading profile";
      document.getElementById("company_memberships").innerHTML =
        '<p style="color:var(--danger)">Could not load company info.</p>';
    });
