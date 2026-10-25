const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(
  /\/$/,
  ""
);

async function request(path) {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return res.json();
}

export function getMeta() {
  return request("/api/v1/meta");
}

export function getDecisionForecast(deliveryDate) {
  return request(`/api/v1/forecasts/decision?delivery_date=${deliveryDate}`);
}

export function getActuals(from, to) {
  return request(`/api/v1/actuals?from=${from}&to=${to}`);
}

export function getAccuracySummary(from = "2026-01-01", to = "2026-01-31") {
  return request(`/api/v1/accuracy/summary?from=${from}&to=${to}`);
}

export function getAccuracySeries(deliveryDate) {
  return request(`/api/v1/accuracy/series?delivery_date=${deliveryDate}`);
}

export { API_URL };
