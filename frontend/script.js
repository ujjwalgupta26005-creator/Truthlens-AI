// Change this URL when your backend is deployed online.
const API_BASE = "http://127.0.0.1:8000";

const resultBox = document.getElementById("result");
const statusBox = document.getElementById("status");

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Request failed");
  return data;
}

function showResult(data) {
  resultBox.textContent = data.analysis || JSON.stringify(data, null, 2);
}

document.getElementById("textBtn").addEventListener("click", async () => {
  const text = document.getElementById("newsText").value.trim();
  if (text.length < 5) {
    statusBox.textContent = "Please enter at least 5 characters.";
    return;
  }
  const button = document.getElementById("textBtn");
  button.disabled = true;
  statusBox.textContent = "Analyzing...";
  try {
    const data = await request("/analyze-text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    showResult(data);
    statusBox.textContent = "Analysis complete";
    await loadHistory();
  } catch (error) {
    statusBox.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

document.getElementById("imageBtn").addEventListener("click", async () => {
  const file = document.getElementById("imageFile").files[0];
  if (!file) {
    statusBox.textContent = "Please choose an image first.";
    return;
  }
  const form = new FormData();
  form.append("file", file);
  const button = document.getElementById("imageBtn");
  button.disabled = true;
  statusBox.textContent = "Analyzing image...";
  try {
    const data = await request("/analyze-image", { method: "POST", body: form });
    showResult(data);
    statusBox.textContent = "Analysis complete";
    await loadHistory();
  } catch (error) {
    statusBox.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

async function loadHistory() {
  const target = document.getElementById("history");
  try {
    const data = await request("/history");
    target.innerHTML = "";
    if (!data.history.length) {
      target.textContent = "No saved analyses yet.";
      return;
    }
    data.history.forEach(item => {
      const card = document.createElement("article");
      card.className = "history-item";
      const title = document.createElement("strong");
      title.textContent = `${item.input_type.toUpperCase()} · ${item.input_preview}`;
      const date = document.createElement("small");
      date.textContent = item.created_at;
      const body = document.createElement("p");
      body.textContent = item.result;
      const del = document.createElement("button");
      del.className = "delete";
      del.textContent = "Delete";
      del.addEventListener("click", async () => {
        try {
          await request(`/history/${item.id}`, { method: "DELETE" });
          await loadHistory();
        } catch (error) {
          statusBox.textContent = error.message;
        }
      });
      card.append(title, document.createElement("br"), date, body, del);
      target.append(card);
    });
  } catch (error) {
    target.textContent = `Could not load history: ${error.message}`;
  }
}

document.getElementById("refreshBtn").addEventListener("click", loadHistory);
