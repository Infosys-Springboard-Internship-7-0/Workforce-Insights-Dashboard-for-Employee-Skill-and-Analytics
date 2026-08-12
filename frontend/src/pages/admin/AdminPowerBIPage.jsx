import { useEffect, useState } from "react";
import { LayoutDashboard, Plus, Trash2, Pencil, X, Eye, EyeOff } from "lucide-react";
import api from "../../api/client";

const EMPTY_FORM = { title: "", description: "", embed_url: "", is_active: true, display_order: 0 };

export default function AdminPowerBIPage() {
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);

  function loadLinks() {
    setLoading(true);
    api.get("/api/powerbi?active_only=false").then((res) => setLinks(res.data)).finally(() => setLoading(false));
  }

  useEffect(loadLinks, []);

  function openCreate() {
    setForm(EMPTY_FORM);
    setEditingId(null);
    setShowForm(true);
  }

  function openEdit(link) {
    setForm({ ...link });
    setEditingId(link.id);
    setShowForm(true);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (editingId) {
      await api.put(`/api/powerbi/${editingId}`, form);
    } else {
      await api.post("/api/powerbi", form);
    }
    setShowForm(false);
    loadLinks();
  }

  async function toggleActive(link) {
    await api.put(`/api/powerbi/${link.id}`, { is_active: !link.is_active });
    loadLinks();
  }

  async function handleDelete(id) {
    if (!confirm("Delete this Power BI link?")) return;
    await api.delete(`/api/powerbi/${id}`);
    loadLinks();
  }

  return (
    <div className="max-w-4xl mx-auto px-8 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-ink-900 flex items-center gap-2">
            <LayoutDashboard size={20} /> Power BI Links
          </h1>
          <p className="text-sm text-ink-500">
            Use a Power BI "Publish to web" or secure embed URL. Only active links show on the public Dashboards page.
          </p>
        </div>
        <button onClick={openCreate} className="btn-primary flex items-center gap-2">
          <Plus size={15} /> Add Dashboard
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="card p-5 mb-6 space-y-3">
          <div className="flex items-center justify-between mb-1">
            <h2 className="font-semibold text-ink-900 text-sm">{editingId ? "Edit Dashboard" : "New Dashboard"}</h2>
            <button type="button" onClick={() => setShowForm(false)} className="text-ink-400 hover:text-ink-900">
              <X size={16} />
            </button>
          </div>
          <div>
            <label className="label">Title</label>
            <input required className="input-field" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </div>
          <div>
            <label className="label">Description (optional)</label>
            <input className="input-field" value={form.description || ""} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>
          <div>
            <label className="label">Embed URL</label>
            <input required className="input-field" placeholder="https://app.powerbi.com/view?r=..." value={form.embed_url} onChange={(e) => setForm({ ...form, embed_url: e.target.value })} />
          </div>
          <div className="flex items-center gap-4">
            <div className="w-32">
              <label className="label">Display Order</label>
              <input type="number" className="input-field" value={form.display_order} onChange={(e) => setForm({ ...form, display_order: Number(e.target.value) })} />
            </div>
            <label className="flex items-center gap-2 text-sm text-ink-700 mt-5">
              <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
              Active (visible publicly)
            </label>
          </div>
          <button type="submit" className="btn-primary">{editingId ? "Save Changes" : "Add Dashboard"}</button>
        </form>
      )}

      {loading ? (
        <div className="text-ink-500 text-sm">Loading dashboards…</div>
      ) : links.length === 0 ? (
        <div className="card p-10 text-center text-ink-500 text-sm">No dashboards added yet.</div>
      ) : (
        <div className="space-y-3">
          {links.map((l) => (
            <div key={l.id} className="card p-4 flex items-center justify-between gap-4">
              <div>
                <div className="font-semibold text-ink-900 text-sm flex items-center gap-2">
                  {l.title}
                  {!l.is_active && <span className="text-[10px] uppercase tracking-wider bg-ink-100 text-ink-500 px-2 py-0.5">Hidden</span>}
                </div>
                {l.description && <div className="text-sm text-ink-500 mt-0.5">{l.description}</div>}
                <div className="text-xs text-ink-300 mt-1 truncate max-w-md">{l.embed_url}</div>
              </div>
              <div className="flex gap-3 shrink-0">
                <button onClick={() => toggleActive(l)} className="text-ink-400 hover:text-ink-900" title={l.is_active ? "Hide" : "Show"}>
                  {l.is_active ? <Eye size={15} /> : <EyeOff size={15} />}
                </button>
                <button onClick={() => openEdit(l)} className="text-ink-400 hover:text-ink-900"><Pencil size={15} /></button>
                <button onClick={() => handleDelete(l.id)} className="text-ink-400 hover:text-red-600"><Trash2 size={15} /></button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
