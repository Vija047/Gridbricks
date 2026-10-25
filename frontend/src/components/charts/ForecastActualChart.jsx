import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatMw, formatTime } from "../../utils/format";
import { spLabel } from "../../utils/settlement";

export default function ForecastActualChart({ intervals = [] }) {
  const data = intervals.map((row) => ({
    sp: spLabel(row.settlement_period),
    forecast: row.forecast_mw,
    actual: row.actual_mw,
    time: formatTime(row.start_time),
  }));

  return (
    <div className="h-80 w-full">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="sp" tick={{ fontSize: 11 }} interval={3} />
          <YAxis
            tick={{ fontSize: 11 }}
            tickFormatter={(v) => `${Math.round(v / 1000)}k`}
            width={48}
          />
          <Tooltip
            formatter={(value, name) => [formatMw(value, 0), name]}
            labelFormatter={(label, payload) => {
              const time = payload?.[0]?.payload?.time;
              return time ? `${label} · ${time} London` : label;
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="forecast"
            name="Decision forecast"
            stroke="#0284c7"
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="actual"
            name="Actual outturn"
            stroke="#059669"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
