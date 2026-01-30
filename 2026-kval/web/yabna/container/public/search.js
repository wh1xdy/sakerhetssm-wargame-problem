const params = new URLSearchParams(window.location.search);
const query = (params.get("q") || "").trim();
const access = (params.get("access") || "").trim();
const status = document.getElementById("status");
const results = document.getElementById("results");

const setResults = (html) => {
  results.innerHTML = html;
};

const renderItems = (items) => {
  results.innerHTML = "";
  for (const item of items) {
    const tile = document.createElement("div");
    tile.className = "tile";

    const title = document.createElement("h2");
    title.textContent = item.id;

    const frame = document.createElement("iframe");
    frame.src = `/notes#${encodeURIComponent(item.id)}`;
    frame.loading = "lazy";

    tile.appendChild(title);
    tile.appendChild(frame);
    results.appendChild(tile);
  }
};

if (!query) {
  status.textContent = "No query provided.";
  setResults('<div class="empty">Nothing to search yet.</div>');
} else if (query.length < 3) {
  status.textContent = "Query must be at least 3 characters.";
  setResults('<div class="empty">Search term is too short.</div>');
} else {
  (async () => {
    try {
      const accessParam = access ? `&access=${encodeURIComponent(access)}` : "";
      const response = await fetch(
        `/api/notes/search?q=${encodeURIComponent(query)}${accessParam}`,
      );
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || "Search failed.");
      }
      const items = data.results || [];
      status.textContent = `${items.length} note(s) found.`;
      if (!items.length) {
        setResults('<div class="empty">No notes matched that query.</div>');
        return;
      }
      renderItems(items);
    } catch (err) {
      status.textContent = "Unable to load search results.";
      setResults(`<div class="empty">${err.message}</div>`);
    }
  })();
}
