const form = document.getElementById("admin-form");
const urlInput = document.getElementById("admin-url");
const statusDiv = document.getElementById("status");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const url = urlInput.value.trim();
  statusDiv.hidden = false;
  statusDiv.classList.remove("error");

  if (!url) {
    statusDiv.textContent = "Please enter a URL.";
    statusDiv.classList.add("error");
    return;
  }

  statusDiv.textContent = "Sending URL to admin...";

  try {
    const response = await fetch("/api/admin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.error || "Request failed.");
    }

    statusDiv.textContent = "Admin visit queued.";
    form.reset();
  } catch (err) {
    statusDiv.textContent = err.message;
    statusDiv.classList.add("error");
  }
});
