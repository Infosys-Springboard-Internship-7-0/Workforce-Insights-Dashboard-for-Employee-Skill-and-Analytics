import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  Users, UserCog, FileText, LayoutDashboard, MessageSquareText,
  Lightbulb, LogOut, Bot, ExternalLink,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";

const NAV_SECTIONS = [
  {
    title: "Overview",
    items: [{ to: "/admin", label: "Recommendations", icon: Lightbulb, end: true }],
  },
  {
    title: "Content Management",
    items: [
      { to: "/admin/documents", label: "Documents", icon: FileText },
      { to: "/admin/team", label: "Team Members", icon: Users },
      { to: "/admin/powerbi", label: "Power BI Links", icon: LayoutDashboard },
    ],
  },
  {
    title: "Assistant",
    items: [{ to: "/admin/assistant", label: "Decision Assistant", icon: MessageSquareText }],
  },
  {
    title: "Account",
    items: [
      { to: "/admin/admins", label: "Manage Admins", icon: UserCog },
      { to: "/admin/profile", label: "My Profile", icon: Users },
    ],
  },
];

export default function AdminLayout() {
  const { admin, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="min-h-screen flex bg-ink-50">
      <aside className="w-64 bg-ink-900 text-white flex flex-col shrink-0">
        <div className="h-16 flex items-center gap-2 px-5 border-b border-white/10">
          <div className="w-8 h-8 bg-white flex items-center justify-center">
            <Bot size={18} className="text-ink-900" />
          </div>
          <span className="font-bold text-sm">Admin Console</span>
        </div>

        <nav className="flex-1 overflow-y-auto py-4">
          {NAV_SECTIONS.map((section) => (
            <div key={section.title} className="mb-5">
              <div className="px-5 text-[11px] font-semibold uppercase tracking-wider text-white/40 mb-1.5">
                {section.title}
              </div>
              {section.items.map(({ to, label, icon: Icon, end }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={end}
                  className={({ isActive }) =>
                    `flex items-center gap-2.5 px-5 py-2.5 text-sm font-medium transition-colors ${
                      isActive ? "bg-accent-600 text-white" : "text-white/70 hover:bg-white/10 hover:text-white"
                    }`
                  }
                >
                  <Icon size={16} />
                  {label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <div className="border-t border-white/10 p-4">
          <NavLink to="/" className="flex items-center gap-2 text-xs text-white/60 hover:text-white mb-3">
            <ExternalLink size={13} /> View public site
          </NavLink>
          <div className="text-xs text-white/50 mb-2 truncate">{admin?.email}</div>
          <button onClick={handleLogout} className="flex items-center gap-2 text-sm font-semibold text-white/80 hover:text-white">
            <LogOut size={15} /> Sign out
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
