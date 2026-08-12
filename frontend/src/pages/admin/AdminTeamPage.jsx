import { useEffect, useState } from "react";
import { Users, Plus, Trash2, Pencil, X } from "lucide-react";
import api from "../../api/client";

const EMPTY_FORM = { name: "", role: "", contribution: "", photo_url: "", linkedin_url: "", display_order: 0 };

export default function AdminTeamPage() {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);

  function loadMembers() {
    setLoading(true);
    api.get("/api/team").then((res) => setMembers(res.data)).finally(() => setLoading(false));
  }

  useEffect(loadMembers, []);

  function openCreate() {
    setForm(EMPTY_FORM);
    setEditingId(null);
    setShowForm(true);
  }

  function openEdit(member) {
    setForm({ ...member });
    setEditingId(member.id);
    setShowForm(true);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (editingId) {
      await api.put(`/api/team/${editingId}`, form);
    } else {
      await api.post("/api/team", form);
    }
    setShowForm(false);
    loadMembers();
  }

  async function handleDelete(id) {
    if (!confirm("Remove this team member from the landing page?")) return;
    await api.delete(`/api/team/${id}`);
    loadMembers();
  }

  return (
    <div className="max-w-4xl mx-auto px-8 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-ink-900 flex items-center gap-2">
            <Users size={20} /> Team Members
          </h1>
          <p className="text-sm text-ink-500">Shown on the public landing page's Team Contributions section.</p>
        </div>
        <button onClick={openCreate} className="btn-primary flex items-center gap-2">
          <Plus size={15} /> Add Member
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="card p-5 mb-6 space-y-3">
          <div className="flex items-center justify-between mb-1">
            <h2 className="font-semibold text-ink-900 text-sm">{editingId ? "Edit Member" : "New Member"}</h2>
            <button type="button" onClick={() => setShowForm(false)} className="text-ink-400 hover:text-ink-900">
              <X size={16} />
            </button>
          </div>
          <div className="grid sm:grid-cols-2 gap-3">
            <div>
              <label className="label">Name</label>
              <input required className="input-field" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </div>
            <div>
              <label className="label">Role</label>
              <input required className="input-field" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="label">Contribution</label>
            <textarea required rows={2} className="input-field" value={form.contribution} onChange={(e) => setForm({ ...form, contribution: e.target.value })} />
          </div>
          <div className="grid sm:grid-cols-2 gap-3">
            <div>
              <label className="label">Photo URL (optional)</label>
              <input className="input-field" value={form.photo_url || ""} onChange={(e) => setForm({ ...form, photo_url: e.target.value })} />
            </div>
            <div>
              <label className="label">LinkedIn URL (optional)</label>
              <input className="input-field" value={form.linkedin_url || ""} onChange={(e) => setForm({ ...form, linkedin_url: e.target.value })} />
            </div>
          </div>
          <div className="w-32">
            <label className="label">Display Order</label>
            <input type="number" className="input-field" value={form.display_order} onChange={(e) => setForm({ ...form, display_order: Number(e.target.value) })} />
          </div>
          <button type="submit" className="btn-primary">{editingId ? "Save Changes" : "Add Member"}</button>
        </form>
      )}

      {loading ? (
        <div className="text-ink-500 text-sm">Loading team members…</div>
      ) : members.length === 0 ? (
        <div className="card p-10 text-center text-ink-500 text-sm">No team members added yet.</div>
      ) : (
        <div className="space-y-3">
          {members.map((m) => (
            <div key={m.id} className="card p-4 flex items-center justify-between gap-4">
              <div>
                <div className="font-semibold text-ink-900 text-sm">{m.name} <span className="font-normal text-ink-500">— {m.role}</span></div>
                <div className="text-sm text-ink-500 mt-0.5">{m.contribution}</div>
              </div>
              <div className="flex gap-3 shrink-0">
                <button onClick={() => openEdit(m)} className="text-ink-400 hover:text-ink-900"><Pencil size={15} /></button>
                <button onClick={() => handleDelete(m.id)} className="text-ink-400 hover:text-red-600"><Trash2 size={15} /></button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
