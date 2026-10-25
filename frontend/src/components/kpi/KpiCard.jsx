export default function KpiCard({ label, value, hint, accent = "sky" }) {
  const accents = {
    sky: "border-wind-500/40",
    green: "border-actual-500/40",
    amber: "border-warn-500/40",
    slate: "border-slate-300",
  };
  return (
    <div
      className={`rounded-xl border bg-white/90 p-4 shadow-sm backdrop-blur ${accents[accent] || accents.slate}`}
    >
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-2 text-2xl font-semibold text-ink-900">{value}</p>
      {hint ? <p className="mt-1 text-xs text-slate-500">{hint}</p> : null}
    </div>
  );
}
