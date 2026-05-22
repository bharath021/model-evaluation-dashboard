const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

export async function fetchModels() {
  return request("/models");
}

export async function fetchHistory() {
  return request("/history");
}

export async function runEvaluation(prompt) {
  return request("/run-eval", {
    method: "POST",
    body: JSON.stringify({ prompt }),
  });
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail || `API request failed with ${response.status}.`);
  }

  return response.json();
}
