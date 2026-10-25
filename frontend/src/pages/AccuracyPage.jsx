import { useState } from "react";
import { getAccuracySeries, getAccuracySummary } from "../api/client";
import DailyAccuracyChart from "../components/charts/DailyAccuracyChart";
import ErrorByPeriodChart from "../components/charts/ErrorByPeriodChart";
import DeliveryDatePicker from "../components/filters/DeliveryDatePicker";
import KpiCard from "../components/kpi/KpiCard";
import DailyMetricsTable from "../components/tables/DailyMetricsTable";
import { useAsync } from "../hooks/useWindData";
import { formatMw, formatPct } from "../utils/format";

export default function AccuracyPage() {
  const [date, setDate] = useState("2026-01-15");
  const summary = useAsync(() => getAccuracySummary(), []);
  const series = useAsync(() => getAccuracySeries(date), [date]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-ink-900">Forecast accuracy</h2>
        <p className="mt-1 max-w-2xl text-sm text-slate-600">
          Quantified error of decision-relevant forecasts versus FUELHH wind outturn —
          so procurement can size risk around day-ahead wind uncertainty.
        </p>
      </div>

      {summary.loading && <p className="text-slate-600">Loading accuracy summary…</p>}
      {summary.error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
          {summary.error}
        </div>
      )}

      {summary.data && (
        <>
          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KpiCard label="MAE" value={formatMw(summary.data.overall.mae_mw)} accent="sky" />
            <KpiCard label="RMSE" value={formatMw(summary.data.overall.rmse_mw)} />
            <KpiCard label="MAPE" value={formatPct(summary.data.overall.mape_pct)} accent="amber" />
            <KpiCard
              label="Bias (F−A)"
              value={formatMw(summary.data.overall.bias_mw)}
              hint="Positive = over-forecast"
              accent="green"
            />
          </section>

          <section className="rounded-xl border border-slate-200 bg-white/90 p-4 shadow-sm">
            <h3 className="mb-2 font-semibold">Daily MAE &amp; bias</h3>
            <DailyAccuracyChart daily={summary.data.daily} />
          </section>

          <section>
            <h3 className="mb-2 font-semibold">Daily metrics</h3>
            <DailyMetricsTable
              daily={summary.data.daily}
              onSelectDate={(d) => setDate(String(d))}
            />
          </section>
        </>
      )}

      <section className="space-y-4">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <h3 className="font-semibold">Half-hourly error profile</h3>
          <DeliveryDatePicker value={date} onChange={setDate} label="Inspect day" />
        </div>
        {series.loading && <p className="text-slate-600">Loading series…</p>}
        {series.error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
            {series.error}
          </div>
        )}
        {series.data && (
          <div className="rounded-xl border border-slate-200 bg-white/90 p-4 shadow-sm">
            <p className="mb-2 text-sm text-slate-600">
              Day MAE {formatMw(series.data.mae_mw)} · MAPE {formatPct(series.data.mape_pct)}{" "}
              · Bias {formatMw(series.data.bias_mw)}
            </p>
            <ErrorByPeriodChart intervals={series.data.intervals} />
          </div>
        )}
      </section>
    </div>
  );
}
