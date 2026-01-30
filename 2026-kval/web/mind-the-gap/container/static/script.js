const form = document.getElementById("searchForm");
const input = document.getElementById("query");
const error = document.getElementById("error");
const results = document.getElementById("results");
const FRONTEND_RE = /^[A-Za-z0-9 ]*$/;
function showError(msg) {
  error.textContent = "Error: " + msg;
  error.style.display = "block";
  results.innerHTML = "";
}
function hideError() {
  error.style.display = "none";
  error.textContent = "";
}
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = String(text);
  return div.innerHTML;
}
async function getToken() {
  const res = await fetch("/api/token");
  const data = await res.json().catch(() => ({}));
  return data.token || null;
}
async function validate(query) {
  const res = await fetch("/api/validate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  const data = await res.json().catch(() => ({}));
  return { valid: !!data.valid };
}
async function search(query, token) {
  const res = await fetch("/api/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": token,
    },
    body: JSON.stringify({ query }),
  });
  const data = await res.json().catch(() => ({}));
  return { status: res.status, data };
}
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = input.value.trim();
  hideError();
  if (query.length === 0) {
    showError("Please enter a search term.");
    return;
  }
  if (!FRONTEND_RE.test(query)) {
    showError("Only letters and numbers are allowed.");
    return;
  }
  const v = await validate(query);
  if (!v.valid) {
    showError("Only letters and numbers are allowed.");
    return;
  }
  const token = await getToken();
  const { status, data } = await search(query, token);
  if (data && data.error) {
    showError(data.error);
    return;
  }
  if (!Array.isArray(data) || data.length === 0) {
    results.innerHTML = `<p class="muted">No results found.</p>`;
    return;
  }
  results.innerHTML = data
    .map(
      (faq) => `
        <article class="faq">
          <h2>${escapeHtml(faq.question)}</h2>
          <p>${escapeHtml(faq.answer)}</p>
        </article>
      `
    )
    .join("");
});
