import { januaryDates } from "../../utils/format";

export default function DeliveryDatePicker({ value, onChange, label = "Delivery date" }) {
  const dates = januaryDates();
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="font-medium text-slate-600">{label}</span>
      <select
        className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm focus:border-wind-500 focus:outline-none focus:ring-2 focus:ring-wind-500/30"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {dates.map((d) => (
          <option key={d} value={d}>
            {d}
          </option>
        ))}
      </select>
    </label>
  );
}
