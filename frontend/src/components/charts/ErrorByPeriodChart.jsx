import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatMw } from "../../utils/format";
import { spLabel } from "../../utils/settlement";

export default function ErrorByPeriodChart({ intervals = [] }) {
  const data = intervals.map((row) => ({
    sp: spLabel(row.settlement_period),
    error: row.error_mw,
  }));

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="sp" tick={{ fontSize: 11 }} interval={3} />
          <YAxis tick={{ fontSize: 11 }} width={52} />
          <Tooltip formatter={(v) => [formatMw(v, 0), "Error (F−A)"]} />
          <ReferenceLine y={0} stroke="#64748b" />
          <Bar dataKey="error" name="Error MW" fill="#0ea5e9" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
