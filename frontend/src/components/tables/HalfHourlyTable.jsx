import { formatMw, formatTime } from "../../utils/format";
import { spLabel } from "../../utils/settlement";

export default function HalfHourlyTable({ intervals = [] }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-3 py-2">SP</th>
            <th className="px-3 py-2">Start (London)</th>
            <th className="px-3 py-2 text-right">Forecast</th>
            <th className="px-3 py-2 text-right">Actual</th>
            <th className="px-3 py-2 text-right">Error</th>
          </tr>
        </thead>
        <tbody>
          {intervals.map((row) => (
            <tr
              key={`${row.settlement_date}-${row.settlement_period}`}
              className="border-t border-slate-100"
            >
              <td className="px-3 py-2 font-medium">{spLabel(row.settlement_period)}</td>
              <td className="px-3 py-2 text-slate-600">{formatTime(row.start_time)}</td>
              <td className="px-3 py-2 text-right tabular-nums">
                {formatMw(row.forecast_mw)}
              </td>
              <td className="px-3 py-2 text-right tabular-nums">
                {formatMw(row.actual_mw)}
              </td>
              <td
                className={`px-3 py-2 text-right tabular-nums ${
                  row.error_mw != null && Math.abs(row.error_mw) > 500
                    ? "text-amber-700 font-medium"
                    : ""
                }`}
              >
                {formatMw(row.error_mw)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
