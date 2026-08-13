import { useEffect, useState } from "react";
import { UserCog, Plus, Trash2, X, AlertCircle, ShieldCheck } from "lucide-react";
import api from "../../api/client";
import { useAuth } from "../../context/AuthContext";

const EMPTY_FORM = { name: "", email: "", password: "", is_super_admin: false };

export default function AdminAdminsPage() {
  const { admin: currentAdmin } = useAuth();
  const [admins, setAdmins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");

  function loadAdmins() {
    setLoading(true);
    api.get("/api/admins").then((res) => setAdmins(res.data)).finally(() => setLoading(false));
  }

  useEffect(loadAdmins, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post("/api/admins", form);
      setForm(EMPTY_FORM);
      setShowForm(false);
      loadAdmins();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not create admin.");
    }
  }

  async function toggleActive(a) {
    await api.put(`/api/admins/${a.id}`, { is_active: !a.is_active });
    loadAdmins();
  }

  async function toggleSuperAdmin(a) {
    await api.put(`/api/admins/${a.id}`, { is_super_admin: !a.is_super_admin });
    loadAdmins();
  }

  async function handleDelete(id) {
    if (!confirm("Remove this admin account? This cannot be undone.")) return;
    try {
      await api.delete(`/api/admins/${id}`);
      loadAdmins();
    } catch (err) {
      alert(err.response?.data?.detail || "Could not delete admin.");
    }
  }

  const isSuperAdmin = currentAdmin?.is_super_admin;

  return (
    <div className="max-w-4xl mx-auto px-8 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-ink-900 flex items-center gap-2">
            <UserCog size={20} /> Manage Admins
          </h1>
          <p className="text-sm text-ink-500">
            {isSuperAdmin ? "Add, update, or remove admin accounts." : "Only super admins can add or remove admins."}
          </p>
        </div>
        {isSuperAdmin && (
          <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
            <Plus size={15} /> Add Admin
          </button>
        )}
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="card p-5 mb-6 space-y-3">
          <div className="flex items-center justify-between mb-1">
            <h2 className="font-semibold text-ink-900 text-sm">New Admin</h2>
            <button type="button" onClick={() => setShowForm(false)} className="text-ink-400 hover:text-ink-900">
              <X size={16} />
            </button>
          </div>
          {error && (
            <div className="flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2">
              <AlertCircle size={16} className="shrink-0 mt-0.5" /> {error}
            </div>
          )}
          <div className="grid sm:grid-cols-2 gap-3">
            <div>
              <label className="label">Name</label>
              <input required className="input-field" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </div>
            <div>
              <label className="label">Email</label>
              <input type="email" required className="input-field" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="label">Temporary Password (min 8 characters)</label>
            <input type="password" required minLength={8} className="input-field" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </div>
          <label className="flex items-center gap-2 text-sm text-ink-700">
            <input type="checkbox" checked={form.is_super_admin} onChange={(e) => setForm({ ...form, is_super_admin: e.target.checked })} />
            Grant super admin (can manage other admins)
          </label>
          <button type="submit" className="btn-primary">Create Admin</button>
        </form>
      )}

      {loading ? (
        <div className="text-ink-500 text-sm">Loading admins…</div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-ink-900 text-white text-left">
                <th className="px-4 py-2.5 font-semibold">Name</th>
                <th className="px-4 py-2.5 font-semibold">Email</th>
                <th className="px-4 py-2.5 font-semibold">Role</th>
                <th className="px-4 py-2.5 font-semibold">Status</th>
                {isSuperAdmin && <th className="px-4 py-2.5 font-semibold text-right">Actions</th>}
              </tr>
            </thead>
            <tbody>
              {admins.map((a, i) => (
                <tr key={a.id} className={i % 2 === 0 ? "bg-white" : "bg-ink-50"}>
                  <td className="px-4 py-2.5 border-t border-ink-100 font-medium text-ink-900">
                    {a.name} {a.id === currentAdmin?.id && <span className="text-xs text-accent-700">(you)</span>}
                  </td>
                  <td className="px-4 py-2.5 border-t border-ink-100 text-ink-500">{a.email}</td>
                  <td className="px-4 py-2.5 border-t border-ink-100">
                    {a.is_super_admin ? (
                      <span className="inline-flex items-center gap-1 text-xs font-semibold text-accent-700"><ShieldCheck size={12} /> Super Admin</span>
                    ) : (
                      <span className="text-xs text-ink-500">Admin</span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 border-t border-ink-100">
                    <span className={`text-xs font-semibold ${a.is_active ? "text-green-700" : "text-ink-400"}`}>
                      {a.is_active ? "Active" : "Disabled"}
                    </span>
                  </td>
                  {isSuperAdmin && (
                    <td className="px-4 py-2.5 border-t border-ink-100 text-right space-x-3">
                      {a.id !== currentAdmin?.id && (
                        <>
                          <button onClick={() => toggleSuperAdmin(a)} className="text-xs text-ink-500 hover:text-ink-900">
                            {a.is_super_admin ? "Revoke super" : "Make super"}
                          </button>
                          <button onClick={() => toggleActive(a)} className="text-xs text-ink-500 hover:text-ink-900">
                            {a.is_active ? "Disable" : "Enable"}
                          </button>
                          <button onClick={() => handleDelete(a.id)} className="text-ink-400 hover:text-red-600 inline-block align-middle">
                            <Trash2 size={14} />
                          </button>
                        </>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
