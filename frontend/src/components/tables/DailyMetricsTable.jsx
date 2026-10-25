import { formatMw, formatPct } from "../../utils/format";

export default function DailyMetricsTable({ daily = [], onSelectDate }) {
  const sorted = [...daily].sort((a, b) => b.mae_mw - a.mae_mw);

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-3 py-2">Date</th>
            <th className="px-3 py-2 text-right">MAE</th>
            <th className="px-3 py-2 text-right">RMSE</th>
            <th className="px-3 py-2 text-right">MAPE</th>
            <th className="px-3 py-2 text-right">Bias</th>
            <th className="px-3 py-2 text-right">n</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((row) => (
            <tr
              key={row.settlement_date}
              className="border-t border-slate-100 hover:bg-sky-50/60 cursor-pointer"
              onClick={() => onSelectDate?.(row.settlement_date)}
            >
              <td className="px-3 py-2 font-medium text-wind-700">
                {row.settlement_date}
              </td>
              <td className="px-3 py-2 text-right tabular-nums">{formatMw(row.mae_mw, 0)}</td>
              <td className="px-3 py-2 text-right tabular-nums">{formatMw(row.rmse_mw, 0)}</td>
              <td className="px-3 py-2 text-right tabular-nums">{formatPct(row.mape_pct)}</td>
              <td className="px-3 py-2 text-right tabular-nums">{formatMw(row.bias_mw, 0)}</td>
              <td className="px-3 py-2 text-right tabular-nums">{row.n}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="border-t border-slate-100 px-3 py-2 text-xs text-slate-500">
        Sorted by MAE (worst first). Click a row to inspect that day.
      </p>
    </div>
  );
}
