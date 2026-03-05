const token = localStorage.getItem("access_token");
const logoutUrl = `${domain}api/logout/`; // Assuming standard API pathing

try {
  // 1. Send the request to the backend with the current token
  const response = await fetch(logoutUrl, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
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

  // 3. Redirect to the login page
  window.location.href = "login.html";
}
