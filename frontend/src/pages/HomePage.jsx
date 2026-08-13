import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Bot, LayoutDashboard, Table2, Database, ShieldCheck,
  ArrowRight, FileText, Users, Mail,
} from "lucide-react";
import api from "../api/client";

const TECH_STACK = [
  { name: "React + Vite", category: "Frontend" },
  { name: "Tailwind CSS", category: "Frontend" },
  { name: "FastAPI", category: "Backend" },
  { name: "ChromaDB", category: "Vector Store" },
  { name: "Sentence Transformers", category: "Embeddings" },
  { name: "Groq API", category: "LLM Inference" },
  { name: "SQLAlchemy / SQLite", category: "Database" },
  { name: "Power BI Embed", category: "Analytics" },
];

const ARCHITECTURE_STEPS = [
  "User Question",
  "React Frontend",
  "FastAPI Backend",
  "Generate Embedding",
  "Search ChromaDB",
  "Top-5 Relevant Chunks",
  "Prompt Construction",
  "Groq API (LLM)",
  "Grounded Answer",
  "React Frontend",
];

const SITE_PAGES = [
  { to: "/", label: "Home", desc: "Project overview, architecture, and team.", icon: Bot },
  { to: "/assistant", label: "AI Assistant", desc: "RAG-based chatbot grounded in uploaded documents.", icon: Bot },
  { to: "/dashboards", label: "Power BI Dashboards", desc: "Embedded workforce analytics dashboards.", icon: LayoutDashboard },
  { to: "/data-viewer", label: "Data Viewer", desc: "Browse uploaded datasets in table format.", icon: Table2 },
];

export default function HomePage() {
  const [team, setTeam] = useState([]);
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    api.get("/api/team").then((res) => setTeam(res.data)).catch(() => setTeam([]));
    // Public, metadata-only document listing (no uploader email / content) —
    // shows every uploaded document type, not just CSV datasets.
    api.get("/api/documents/public").then((res) => setDocuments(res.data)).catch(() => setDocuments([]));
  }, []);

  return (
    <div>
      {/* Hero */}
      <section className="border-b border-ink-100 bg-white">
        <div className="max-w-7xl mx-auto px-6 py-20 grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <div className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-accent-700 bg-accent-100 px-3 py-1.5 mb-6">
              Workforce Analytics &amp; Talent Intelligence
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-ink-900 leading-tight mb-6">
              AI Workforce Assistant Platform
            </h1>
            <p className="text-lg text-ink-500 leading-relaxed mb-8">
              A retrieval-augmented AI assistant that answers workforce and policy questions
              grounded in your organization's own documents — backed by embedded Power BI
              dashboards and a live data viewer for full transparency.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link to="/assistant" className="btn-primary flex items-center gap-2">
                Ask the AI Assistant <ArrowRight size={16} />
              </Link>
              <Link to="/dashboards" className="btn-secondary flex items-center gap-2">
                View Dashboards
              </Link>
            </div>
          </div>
          <div className="card p-8">
            <div className="text-xs font-semibold uppercase tracking-wider text-ink-500 mb-4">RAG Architecture</div>
            <div className="space-y-0">
              {ARCHITECTURE_STEPS.map((step, i) => (
                <div key={i} className="flex items-center gap-3 text-sm">
                  <div className="flex flex-col items-center">
                    <div className="w-6 h-6 bg-ink-900 text-white text-[11px] font-bold flex items-center justify-center shrink-0">
                      {i + 1}
                    </div>
                    {i < ARCHITECTURE_STEPS.length - 1 && <div className="w-px h-4 bg-ink-300" />}
                  </div>
                  <div className="text-ink-700 py-1">{step}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Site pages */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-ink-900 mb-2">Explore the Platform</h2>
        <p className="text-ink-500 mb-8">Every page on this site, one click away.</p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {SITE_PAGES.map(({ to, label, desc, icon: Icon }) => (
            <Link key={to} to={to} className="card p-5 hover:border-ink-900 transition-colors group">
              <Icon className="text-accent-700 mb-3" size={22} />
              <div className="font-semibold text-ink-900 mb-1 flex items-center gap-1">
                {label}
                <ArrowRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <div className="text-sm text-ink-500">{desc}</div>
            </Link>
          ))}
        </div>
      </section>

      {/* Technology */}
      <section className="border-y border-ink-100 bg-white">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <h2 className="text-2xl font-bold text-ink-900 mb-2">Technology</h2>
          <p className="text-ink-500 mb-8">The stack powering this platform.</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {TECH_STACK.map((t) => (
              <div key={t.name} className="border border-ink-100 px-4 py-3">
                <div className="text-[11px] font-semibold uppercase tracking-wider text-accent-700 mb-1">{t.category}</div>
                <div className="text-sm font-medium text-ink-900">{t.name}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-ink-900 mb-2 flex items-center gap-2">
          <Users size={22} /> Team Contributions
        </h2>
        <p className="text-ink-500 mb-8">The people behind this platform.</p>

        {team.length === 0 ? (
          <div className="card p-8 text-center text-ink-500 text-sm">
            Team member details will appear here once added by an admin.
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {team.map((m) => (
              <div key={m.id} className="card p-5">
                <div className="flex items-center gap-3 mb-3">
                  {m.photo_url ? (
                    <img src={m.photo_url} alt={m.name} className="w-11 h-11 object-cover allow-round" />
                  ) : (
                    <div className="w-11 h-11 bg-ink-900 text-white flex items-center justify-center font-bold allow-round">
                      {m.name.charAt(0)}
                    </div>
                  )}
                  <div>
                    <div className="font-semibold text-ink-900 text-sm">{m.name}</div>
                    <div className="text-xs text-accent-700 font-medium">{m.role}</div>
                  </div>
                </div>
                <p className="text-sm text-ink-500 leading-relaxed">{m.contribution}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Supporting documents / datasets */}
      <section className="border-t border-ink-100 bg-white">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <h2 className="text-2xl font-bold text-ink-900 mb-2 flex items-center gap-2">
            <FileText size={22} /> Supporting Documents
          </h2>
          <p className="text-ink-500 mb-8">
            Datasets currently available in the <Link to="/data-viewer" className="text-accent-700 hover:underline">Data Viewer</Link>.
          </p>
          {documents.length === 0 ? (
            <div className="card p-8 text-center text-ink-500 text-sm">No datasets uploaded yet.</div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {documents.map((d) => (
                <div key={d.id} className="card px-4 py-3 flex items-center gap-3">
                  <Database size={16} className="text-accent-700 shrink-0" />
                  <div className="min-w-0">
                    <div className="text-sm font-medium text-ink-900 truncate">{d.filename}</div>
                    <div className="text-xs text-ink-500">{d.category}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Contact */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <div className="card p-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Mail className="text-accent-700" size={22} />
            <div>
              <div className="font-semibold text-ink-900">Have questions about this project?</div>
              <div className="text-sm text-ink-500">Reach out any time.</div>
            </div>
          </div>
          <a href="mailto:info@gu-saurabh.site" className="btn-primary flex items-center gap-2">
            info@gu-saurabh.site <ArrowRight size={15} />
          </a>
        </div>
      </section>
    </div>
  );
}
