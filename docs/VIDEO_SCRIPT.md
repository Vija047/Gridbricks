# Video script (≤ 10 minutes)

## Part 1 — Client pitch (≤ 5 min)

**Goal:** Impress the day-ahead procurement team with a focused January 2026 pilot.

1. **Hook (30s)** — “You buy power the day before delivery. Wind is weather-dependent. This portal shows the forecast you would have used at the gate, and how wrong it was historically.”
2. **Scope (30s)** — UK national wind only (Elexon FUELHH + WINDFOR), January 2026.
3. **Dashboard (60s)** — Open live app. Point to MAE, MAPE, % within ±500 MW, mean actual wind. Explain these are decision-relevant errors, not latest-after-the-fact.
4. **Decision forecasts (90s)** — Pick a delivery day. Show cutoff banner (11:00 Europe/London on D−1). Chart forecast vs actual. Scroll table; highlight large error periods.
5. **Accuracy (60s)** — Daily MAE chart, worst days table, half-hourly error profile. “Use this to size reserve / imbalance risk.”
6. **Close (30s)** — Pilot ready to extend to demand, other renewables, or portfolio views.

## Part 2 — Tech lead review (≤ 5 min)

**Goal:** Make architecture and knowledge transfer easy.

1. **Architecture (60s)** — React/Vite → FastAPI → SQLite; Elexon Insights API; Vercel + Render; Docker Compose for local.
2. **Selection logic (90s)** — For delivery day D, take WINDFOR rows with `publishTime ≤ cutoff(D−1 11:00 London)`, latest per settlement period. Actuals: latest FUELHH publish per `startTime`. Hourly WINDFOR expanded to both half-hours.
3. **Code tour (90s)** — `backend/app/clients/elexon.py`, `services/forecast_selection.py`, `metrics.py`, `store.py`; frontend pages under `src/pages`.
4. **Ops (60s)** — `scripts/sync_january_2026.py`, seed under `data/seed`, Docker, env vars (`DECISION_CUTOFF_*`, `VITE_API_URL`).
5. **Limits (30s)** — National wind only; configurable cutoff assumption; Render cold starts.

## Recording tips

- Use the deployed Vercel URL (incognito).
- Keep Part 1 customer language; Part 2 folder names and one diagram.
- Total hard cap: 10 minutes.
