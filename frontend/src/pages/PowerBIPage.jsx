import { useEffect, useState } from "react";
import { LayoutDashboard, AlertCircle } from "lucide-react";
import api from "../api/client";

export default function PowerBIPage() {
  const [links, setLinks] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/api/powerbi")
      .then((res) => {
        setLinks(res.data);
        if (res.data.length > 0) setActiveId(res.data[0].id);
      })
      .finally(() => setLoading(false));
  }, []);

  const active = links.find((l) => l.id === activeId);

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-ink-900 flex items-center gap-2">
          <LayoutDashboard size={20} /> Power BI Dashboards
        </h1>
        <p className="text-sm text-ink-500">Live embedded workforce analytics dashboards.</p>
      </div>

      {loading ? (
        <div className="text-ink-500 text-sm">Loading dashboards…</div>
      ) : links.length === 0 ? (
        <div className="card p-10 text-center">
          <AlertCircle className="mx-auto text-ink-300 mb-3" size={28} />
          <p className="text-ink-500 text-sm">No dashboards have been published yet. Check back soon.</p>
        </div>
      ) : (
        <div className="grid lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1 space-y-2">
            {links.map((l) => (
              <button
                key={l.id}
                onClick={() => setActiveId(l.id)}
                className={`w-full text-left px-4 py-3 border text-sm transition-colors ${
                  l.id === activeId ? "border-ink-900 bg-white font-semibold" : "border-ink-100 bg-white text-ink-500 hover:border-ink-300"
                }`}
              >
                {l.title}
                {l.description && <div className="text-xs font-normal text-ink-500 mt-1">{l.description}</div>}
              </button>
            ))}
          </div>

          <div className="lg:col-span-3 card p-2">
            {active && (
              <iframe
                title={active.title}
                src={active.embed_url}
                className="w-full aspect-video"
                allowFullScreen
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
