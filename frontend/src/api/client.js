const BASE = "/api";

async function getJSON(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  overview: () => getJSON("/overview"),
  skillDemand: () => getJSON("/skill-demand"),
  salaryByRole: () => getJSON("/salary/by-role"),
  salaryByLocation: () => getJSON("/salary/by-location"),
  salaryByExperience: () => getJSON("/salary/by-experience"),
  options: () => getJSON("/options"),
  modelComparison: () => getJSON("/model-comparison"),
  predict: async (payload) => {
    const res = await fetch(`${BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `Request failed: ${res.status}`);
    }
    return res.json();
  },
};
