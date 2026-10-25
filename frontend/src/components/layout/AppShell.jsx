import Nav from "./Nav";

export default function AppShell({ children }) {
  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200/80 bg-ink-950 text-white shadow-sm">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-wind-400">
              UK Day-Ahead Procurement
            </p>
            <h1 className="mt-1 text-2xl font-semibold tracking-tight">
              Wind Decision Portal
            </h1>
            <p className="mt-1 max-w-xl text-sm text-slate-300">
              National wind forecast vs outturn — January 2026 pilot (Elexon)
            </p>
          </div>
          <Nav />
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">{children}</main>
      <footer className="border-t border-slate-200 bg-white/70 py-4 text-center text-xs text-slate-500">
        Data: Elexon BMRS FUELHH (WIND) &amp; WINDFOR · Decision cutoff default 11:00
        Europe/London on D−1
      </footer>
    </div>
  );
}
