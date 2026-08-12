import { NavLink, Outlet, Link } from "react-router-dom";
import { Bot, LayoutDashboard, Table2, ShieldCheck, Home } from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Home", icon: Home, end: true },
  { to: "/assistant", label: "AI Assistant", icon: Bot },
  { to: "/dashboards", label: "Power BI", icon: LayoutDashboard },
  { to: "/data-viewer", label: "Data Viewer", icon: Table2 },
];

export default function PublicLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-ink-50">
      <header className="border-b border-ink-100 bg-white sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-bold text-ink-900 tracking-tight">
            <div className="w-8 h-8 bg-ink-900 flex items-center justify-center text-white">
              <Bot size={18} />
            </div>
            <span className="text-lg">AI Workforce Assistant</span>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 px-4 py-2 text-sm font-medium transition-colors ${
                    isActive ? "text-accent-700 bg-accent-100" : "text-ink-700 hover:bg-ink-100"
                  }`
                }
              >
                <Icon size={16} />
                {label}
              </NavLink>
            ))}
          </nav>

          <Link to="/login" className="flex items-center gap-1.5 text-sm font-semibold text-ink-700 hover:text-ink-900 border border-ink-300 px-4 py-2 hover:border-ink-900 transition-colors">
            <ShieldCheck size={16} />
            Admin Login
          </Link>
        </div>

        {/* mobile nav */}
        <nav className="md:hidden flex border-t border-ink-100 overflow-x-auto">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-1.5 px-4 py-3 text-xs font-medium whitespace-nowrap ${
                  isActive ? "text-accent-700 border-b-2 border-accent-700" : "text-ink-500"
                }`
              }
            >
              <Icon size={14} />
              {label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <footer className="border-t border-ink-100 bg-white">
        <div className="max-w-7xl mx-auto px-6 py-8 flex flex-col md:flex-row justify-between gap-4 text-sm text-ink-500">
          <div>AI Workforce Assistant Platform — Workforce Analytics &amp; Talent Intelligence</div>
          <div>Contact: <a href="mailto:info@gu-saurabh.site" className="text-accent-700 hover:underline">info@gu-saurabh.site</a></div>
        </div>
      </footer>
    </div>
  );
}
