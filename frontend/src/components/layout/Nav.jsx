import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/decision", label: "Decision forecasts" },
  { to: "/accuracy", label: "Accuracy" },
];

export default function Nav() {
  return (
    <nav className="flex flex-wrap gap-2">
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          end={link.end}
          className={({ isActive }) =>
            [
              "rounded-md px-3 py-2 text-sm font-medium transition",
              isActive
                ? "bg-wind-600 text-white"
                : "bg-white/10 text-slate-200 hover:bg-white/15",
            ].join(" ")
          }
        >
          {link.label}
        </NavLink>
      ))}
    </nav>
  );
}
