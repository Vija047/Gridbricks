import { useState } from "react";
import { getDecisionForecast } from "../api/client";
import ForecastActualChart from "../components/charts/ForecastActualChart";
import DeliveryDatePicker from "../components/filters/DeliveryDatePicker";
import HalfHourlyTable from "../components/tables/HalfHourlyTable";
import { useAsync } from "../hooks/useWindData";
import { formatDateTime } from "../utils/format";

export default function DecisionForecastsPage() {
  const [date, setDate] = useState("2026-01-15");
  const { data, loading, error } = useAsync(() => getDecisionForecast(date), [date]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-ink-900">Decision forecasts</h2>
          <p className="mt-1 max-w-2xl text-sm text-slate-600">
            The curve a trader would have seen at the day-ahead gate for the selected
            delivery day — latest WINDFOR publish at or before the cutoff.
          </p>
        </div>
        <DeliveryDatePicker value={date} onChange={setDate} />
      </div>

      {loading && <p className="text-slate-600">Loading forecast…</p>}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
          {error}
        </div>
      )}

      {data && (
        <>
          <div className="rounded-lg border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-950">
            <p>
              <span className="font-semibold">Cutoff:</span> {data.cutoff_local}
            </p>
            <p className="mt-1">
              <span className="font-semibold">Latest publish used:</span>{" "}
              {formatDateTime(data.latest_publish_time)}
            </p>
          </div>

          <section className="rounded-xl border border-slate-200 bg-white/90 p-4 shadow-sm">
            <h3 className="mb-2 font-semibold">Forecast vs actual (MW)</h3>
            <ForecastActualChart intervals={data.intervals} />
          </section>

          <section>
            <h3 className="mb-2 font-semibold">Half-hourly detail</h3>
            <HalfHourlyTable intervals={data.intervals} />
          </section>
        </>
      )}
    </div>
  );
}
