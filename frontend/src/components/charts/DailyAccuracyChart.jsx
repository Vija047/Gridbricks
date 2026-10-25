import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatMw } from "../../utils/format";

export default function DailyAccuracyChart({ daily = [] }) {
  const data = daily.map((row) => ({
    date: String(row.settlement_date).slice(5),
    mae: row.mae_mw,
    bias: row.bias_mw,
  }));

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} interval={2} />
          <YAxis tick={{ fontSize: 11 }} width={48} />
          <Tooltip
            formatter={(value, name) => [formatMw(value, 1), name === "mae" ? "MAE" : "Bias"]}
          />
          <Line
            type="monotone"
            dataKey="mae"
            name="MAE"
            stroke="#0284c7"
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="bias"
            name="Bias"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
