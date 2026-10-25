import { getAccuracySummary, getMeta } from "../api/client";
import DailyAccuracyChart from "../components/charts/DailyAccuracyChart";
import KpiCard from "../components/kpi/KpiCard";
import { useAsync } from "../hooks/useWindData";
import { formatDateTime, formatMw, formatPct } from "../utils/format";

export default function DashboardPage() {
  const meta = useAsync(() => getMeta(), []);
  const summary = useAsync(() => getAccuracySummary(), []);

  if (meta.loading || summary.loading) {
    return <p className="text-slate-600">Loading January 2026 summary…</p>;
  }
  if (meta.error || summary.error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
        {meta.error || summary.error}
      </div>
    );
  }

  const overall = summary.data.overall;
  const worst = [...(summary.data.daily || [])].sort((a, b) => b.mae_mw - a.mae_mw)[0];

  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-xl font-semibold text-ink-900">Pilot overview</h2>
        <p className="mt-1 max-w-3xl text-sm text-slate-600">
          For each delivery day in January 2026, we select the latest national wind
          forecast published at or before the day-ahead decision cutoff (
          {meta.data.decision_cutoff_local_time} {meta.data.decision_timezone} on D−1),
          then compare it to Elexon FUELHH wind outturn.
        </p>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Month MAE"
          value={formatMw(overall.mae_mw, 0)}
          hint={`${overall.n} half-hour intervals`}
          accent="sky"
        />
        <KpiCard
          label="Month MAPE"
          value={formatPct(overall.mape_pct)}
          hint="vs actual MW (ε = 1 MW floor)"
          accent="amber"
        />
        <KpiCard
          label="Mean actual wind"
          value={formatMw(overall.mean_actual_mw, 0)}
          hint="Average outturn across matched intervals"
          accent="green"
        />
        <KpiCard
          label="Within ±500 MW"
          value={formatPct(summary.data.pct_within_500_mw)}
          hint={
            worst
              ? `Worst day: ${worst.settlement_date} (MAE ${formatMw(worst.mae_mw)})`
              : undefined
          }
          accent="slate"
        />
      </section>

      <section className="rounded-xl border border-slate-200 bg-white/90 p-4 shadow-sm">
        <div className="mb-3 flex flex-wrap items-end justify-between gap-2">
          <div>
            <h3 className="font-semibold text-ink-900">Daily MAE &amp; bias</h3>
            <p className="text-xs text-slate-500">
              Coverage: {meta.data.forecast_days} forecast days · {meta.data.actuals_days}{" "}
              actual days
              {meta.data.last_sync_at
                ? ` · synced ${formatDateTime(meta.data.last_sync_at)}`
                : ""}
            </p>
          </div>
        </div>
        <DailyAccuracyChart daily={summary.data.daily} />
      </section>
    </div>
  );
}
