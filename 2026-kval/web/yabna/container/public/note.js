const noteId = window.location.hash.slice(1);
const noteBody = document.getElementById("note-body");
const statusDiv = document.getElementById("status");
const accessInput = document.getElementById("access");

const loadNote = async () => {
  try {
    const accessToken = accessInput?.value.trim() || "";
    const accessQuery = accessToken
      ? `?access=${encodeURIComponent(accessToken)}`
      : "";
    const response = await fetch(
      `/api/notes/${encodeURIComponent(noteId)}${accessQuery}`,
    );
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.error || "Note not found.");
    }
    const data = await response.json();
    noteBody.innerHTML =
      data.note.length > 500 ? data.note.substring(0, 500) + "..." : data.note;
  } catch (err) {
    noteBody.innerHTML = "";
    statusDiv.classList.add("error");
    statusDiv.hidden = false;
    statusDiv.textContent = err.message;
  }
};

accessInput.addEventListener("input", () => {
  loadNote();
});

loadNote();
