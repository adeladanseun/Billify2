async function logoutFunction() {
  const token = localStorage.getItem("access_token");
  const refresh = localStorage.getItem("refresh_token");
  const logoutUrl = `${DOMAIN}/api/logout/`; // Assuming standard API pathing

  try {
    if (!token && !refresh) {
      console.error("You don't have complete login credentials");
      return null;
    }
    const payload = {
      refresh: refresh,
    };
    // 1. Send the request to the backend with the current refresh token
    const response = await fetch(logoutUrl, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      console.warn(
        "Backend session could not be invalidated, proceeding with local logout.",
      );
    }
  } catch (error) {
    console.error("Network error during logout:", error);
  } finally {
    // 2. Always delete the local token regardless of server response
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    // 3. Redirect to the login page
    window.location.href = "/auth/html/login.html";
  }
}

const logout_button = document.getElementById("logout_button");
if(logout_button) {
  logout_button.addEventListener("click", (e) => {
    e.preventDefault();
    logoutFunction();
  });
}