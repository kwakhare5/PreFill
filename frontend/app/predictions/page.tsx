/* ─────────────────────────────────────────────────────────
   Predictions — Demo Scene 2
   "Click on Cooking Oil. Show the consumption model.
    87% confidence. Estimated depletion: May 24.
    Show the last 5 predictions vs actual reorder dates."
   — CLAUDE.md Part 7
───────────────────────────────────────────────────────── */

const ITEMS = [
  {
    id:       "INS_001",
    name:     "Amul Taza Milk 1L",
    category: "Dairy",
    days:     1,
    conf:     76,
    avg:      "1.1 L/day",
    cycle:    "2.1 days",
    depletes: "May 18, 2026",
    lastBuy:  "May 17",
    qty:      "1 L",
    history: [
      { predicted: "Apr 15", actual: "Apr 15", error: 0  },
      { predicted: "Apr 17", actual: "Apr 18", error: 1  },
      { predicted: "Apr 20", actual: "Apr 19", error: -1 },
      { predicted: "Apr 22", actual: "Apr 23", error: 1  },
      { predicted: "Apr 25", actual: "Apr 24", error: -1 },
    ],
  },
  {
    id:       "INS_003",
    name:     "Fortune Sunflower Oil 1L",
    category: "Staples",
    days:     2,
    conf:     87,
    avg:      "68 ml/day",
    cycle:    "14.7 days",
    depletes: "May 19, 2026",
    lastBuy:  "May 5",
    qty:      "1 L",
    history: [
      { predicted: "Mar 20", actual: "Mar 21", error: 1  },
      { predicted: "Apr 3",  actual: "Apr 4",  error: 1  },
      { predicted: "Apr 18", actual: "Apr 17", error: -1 },
      { predicted: "May 2",  actual: "May 3",  error: 1  },
      { predicted: "May 18", actual: "—",      error: 0  },
    ],
  },
  {
    id:       "INS_005",
    name:     "Nandini Eggs — Pack of 12",
    category: "Protein",
    days:     4,
    conf:     88,
    avg:      "2.3 pcs/day",
    cycle:    "6.2 days",
    depletes: "May 21, 2026",
    lastBuy:  "May 13",
    qty:      "12 pcs",
    history: [
      { predicted: "Apr 27", actual: "Apr 28", error: 1  },
      { predicted: "May 3",  actual: "May 3",  error: 0  },
      { predicted: "May 9",  actual: "May 10", error: 1  },
      { predicted: "May 15", actual: "May 14", error: -1 },
      { predicted: "May 21", actual: "—",      error: 0  },
    ],
  },
  {
    id:       "INS_002",
    name:     "Aashirvaad Atta 5kg",
    category: "Staples",
    days:     12,
    conf:     68,
    avg:      "280 g/day",
    cycle:    "17 days",
    depletes: "May 29, 2026",
    lastBuy:  "Apr 30",
    qty:      "5 kg",
    history: [
      { predicted: "Jan 17", actual: "Jan 18", error: 1  },
      { predicted: "Feb 3",  actual: "Feb 4",  error: 1  },
      { predicted: "Feb 21", actual: "Feb 20", error: -1 },
      { predicted: "Mar 9",  actual: "Mar 11", error: 2  },
      { predicted: "Mar 28", actual: "Mar 27", error: -1 },
    ],
  },
  {
    id:       "INS_004",
    name:     "India Gate Basmati Rice 5kg",
    category: "Staples",
    days:     19,
    conf:     71,
    avg:      "200 g/day",
    cycle:    "25 days",
    depletes: "Jun 5, 2026",
    lastBuy:  "Apr 15",
    qty:      "5 kg",
    history: [
      { predicted: "Mar 11", actual: "Mar 12", error: 1  },
      { predicted: "Apr 5",  actual: "Apr 5",  error: 0  },
      { predicted: "Apr 30", actual: "May 2",  error: 2  },
      { predicted: "May 27", actual: "—",      error: 0  },
      { predicted: "Jun 21", actual: "—",      error: 0  },
    ],
  },
];

function urgencyStyle(days: number) {
  if (days <= 2) return { pill: "pill-danger",  bar: "#dc2626", label: "CRITICAL" };
  if (days <= 5) return { pill: "pill-warning", bar: "#d97706", label: "LOW"      };
  return             { pill: "pill-muted",    bar: "#6b6560", label: "OK"       };
}

export default function PredictionsPage() {
  return (
    <div className="flex flex-col gap-12">

      {/* ── Header ──────────────────────────────────────────── */}
      <div className="flex flex-col gap-3">
        <div className="font-data text-accent text-[10px] tracking-widest uppercase">
          M-02 · Depletion Predictions
        </div>
        <h1 className="text-5xl font-light tracking-tight uppercase leading-none">
          Depletion<br />
          <span className="font-black">Timeline</span>
        </h1>
        <p className="font-data text-sm text-muted max-w-lg">
          Facebook Prophet time-series forecasting per item.
          Confidence derived from purchase regularity + data depth.
        </p>
      </div>

      {/* ── Accuracy Banner ─────────────────────────────────── */}
      <div className="grid grid-cols-3 gap-px bg-border">
        {[
          { value: "±1.4d",  label: "Mean Prediction Error",    sub: "last 30 days" },
          { value: "34",     label: "Active Models",             sub: "items with conf ≥ 50%" },
          { value: "87%",    label: "Top Confidence",            sub: "Sunflower Oil — 14 orders" },
        ].map((s) => (
          <div key={s.label} className="card p-5 flex flex-col gap-2">
            <div className="stat-value text-accent">{s.value}</div>
            <div className="stat-label">{s.label}</div>
            <div className="font-data text-[11px] text-muted">{s.sub}</div>
          </div>
        ))}
      </div>

      {/* ── Item List ───────────────────────────────────────── */}
      <div className="flex flex-col gap-4">
        {ITEMS.map((item) => {
          const u = urgencyStyle(item.days);
          const fill = Math.max(4, Math.round((item.days / 30) * 100));
          return (
            <div key={item.id} className="card overflow-hidden">

              {/* Item header row */}
              <div className="px-6 py-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-4 min-w-0">
                  <span className={`pill ${u.pill}`}>{u.label}</span>
                  <div className="flex flex-col min-w-0">
                    <span className="font-bold tracking-wide truncate">{item.name}</span>
                    <span className="font-data text-xs text-muted">{item.category} · Last bought {item.lastBuy} ({item.qty})</span>
                  </div>
                </div>
                <div className="flex items-center gap-6 shrink-0">
                  <div className="flex flex-col items-end gap-1">
                    <span className="font-data text-xs text-muted">DEPLETES</span>
                    <span className="font-data text-sm font-bold">{item.depletes}</span>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className="font-data text-xs text-muted">CONF</span>
                    <span className="font-data text-sm font-bold text-accent">{item.conf}%</span>
                  </div>
                </div>
              </div>

              {/* Full-width depletion bar */}
              <div className="depletion-bar">
                <div className="depletion-bar-fill" style={{ width: `${fill}%`, background: u.bar }} />
              </div>

              {/* Detail panel */}
              <div className="px-6 py-4 bg-surface border-t border-border grid grid-cols-2 sm:grid-cols-4 gap-6">
                <div className="flex flex-col gap-1">
                  <span className="font-data text-[10px] text-muted uppercase tracking-widest">Daily Use</span>
                  <span className="font-data text-sm">{item.avg}</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="font-data text-[10px] text-muted uppercase tracking-widest">Avg Cycle</span>
                  <span className="font-data text-sm">{item.cycle}</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="font-data text-[10px] text-muted uppercase tracking-widest">Days Left</span>
                  <span className="font-data text-sm">{item.days} days</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="font-data text-[10px] text-muted uppercase tracking-widest">Data Points</span>
                  <span className="font-data text-sm">{item.history.length} orders</span>
                </div>
              </div>

              {/* Prediction accuracy table */}
              <div className="border-t border-border">
                <div className="px-6 py-3 font-data text-[10px] text-muted uppercase tracking-widest">
                  Prediction Accuracy — Last 5 Cycles
                </div>
                <div className="px-6 pb-4 overflow-x-auto">
                  <table className="w-full font-data text-xs">
                    <thead>
                      <tr className="text-muted">
                        <th className="text-left pb-2 pr-6 font-medium">Predicted</th>
                        <th className="text-left pb-2 pr-6 font-medium">Actual</th>
                        <th className="text-left pb-2 font-medium">Error</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {item.history.map((h, i) => (
                        <tr key={i} className="hover:bg-grid transition-colors">
                          <td className="py-2 pr-6">{h.predicted}</td>
                          <td className="py-2 pr-6">{h.actual}</td>
                          <td className={`py-2 font-bold ${
                            h.actual === "—" ? "text-muted" :
                            Math.abs(h.error) <= 1 ? "text-ok" : "text-warning"
                          }`}>
                            {h.actual === "—" ? "pending" : h.error === 0 ? "exact" : `${h.error > 0 ? "+" : ""}${h.error}d`}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
}
