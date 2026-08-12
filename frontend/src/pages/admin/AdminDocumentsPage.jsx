import { useEffect, useState, useRef } from "react";
import { FileText, Upload, Trash2, Pencil, Check, X, AlertCircle } from "lucide-react";
import api from "../../api/client";

const CATEGORIES = ["Policy", "Privacy", "HR Policy", "Report", "Dataset", "General"];

export default function AdminDocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [category, setCategory] = useState("Policy");
  const [error, setError] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editCategory, setEditCategory] = useState("");
  const fileInputRef = useRef(null);

  function loadDocuments() {
    setLoading(true);
    api.get("/api/documents").then((res) => setDocuments(res.data)).finally(() => setLoading(false));
  }

  useEffect(loadDocuments, []);

  async function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    setError("");
    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.post(`/api/documents/upload?category=${encodeURIComponent(category)}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      loadDocuments();
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleDelete(id) {
    if (!confirm("Delete this document? This removes it from the knowledge base permanently.")) return;
    await api.delete(`/api/documents/${id}`);
    loadDocuments();
  }

  function startEdit(doc) {
    setEditingId(doc.id);
    setEditCategory(doc.category);
  }

  async function saveEdit(id) {
    await api.put(`/api/documents/${id}`, { category: editCategory });
    setEditingId(null);
    loadDocuments();
  }

  return (
    <div className="max-w-5xl mx-auto px-8 py-8">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-ink-900 flex items-center gap-2">
          <FileText size={20} /> Document Management
        </h1>
        <p className="text-sm text-ink-500">
          Upload PDF, DOCX, TXT, or CSV files — they're extracted, chunked, embedded, and stored
          in ChromaDB for the AI Assistant to search.
        </p>
      </div>

      <div className="card p-5 mb-6">
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <label className="label">Category</label>
            <select value={category} onChange={(e) => setCategory(e.target.value)} className="input-field w-48">
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <label className="btn-primary flex items-center gap-2 cursor-pointer">
            <Upload size={15} />
            {uploading ? "Uploading…" : "Upload Document"}
            <input ref={fileInputRef} type="file" accept=".pdf,.docx,.txt,.csv" onChange={handleFileSelect} disabled={uploading} className="hidden" />
          </label>
          <span className="text-xs text-ink-500">PDF, DOCX, TXT, or CSV</span>
        </div>

        {error && (
          <div className="flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2 mt-3">
            <AlertCircle size={16} className="shrink-0 mt-0.5" /> {error}
          </div>
        )}
      </div>

      {loading ? (
        <div className="text-ink-500 text-sm">Loading documents…</div>
      ) : documents.length === 0 ? (
        <div className="card p-10 text-center text-ink-500 text-sm">No documents uploaded yet.</div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-ink-900 text-white text-left">
                <th className="px-4 py-2.5 font-semibold">Filename</th>
                <th className="px-4 py-2.5 font-semibold">Type</th>
                <th className="px-4 py-2.5 font-semibold">Category</th>
                <th className="px-4 py-2.5 font-semibold">Chunks</th>
                <th className="px-4 py-2.5 font-semibold">Uploaded By</th>
                <th className="px-4 py-2.5 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((d, i) => (
                <tr key={d.id} className={i % 2 === 0 ? "bg-white" : "bg-ink-50"}>
                  <td className="px-4 py-2.5 border-t border-ink-100 font-medium text-ink-900">{d.filename}</td>
                  <td className="px-4 py-2.5 border-t border-ink-100 uppercase text-xs text-ink-500">{d.file_type}</td>
                  <td className="px-4 py-2.5 border-t border-ink-100">
                    {editingId === d.id ? (
                      <select value={editCategory} onChange={(e) => setEditCategory(e.target.value)} className="input-field text-xs py-1">
                        {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                      </select>
                    ) : (
                      <span className="text-ink-700">{d.category}</span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 border-t border-ink-100 text-ink-500">{d.chunk_count}</td>
                  <td className="px-4 py-2.5 border-t border-ink-100 text-ink-500 text-xs">{d.uploaded_by}</td>
                  <td className="px-4 py-2.5 border-t border-ink-100 text-right">
                    {editingId === d.id ? (
                      <div className="flex justify-end gap-2">
                        <button onClick={() => saveEdit(d.id)} className="text-green-700 hover:text-green-800"><Check size={16} /></button>
                        <button onClick={() => setEditingId(null)} className="text-ink-400 hover:text-ink-700"><X size={16} /></button>
                      </div>
                    ) : (
                      <div className="flex justify-end gap-3">
                        <button onClick={() => startEdit(d)} className="text-ink-400 hover:text-ink-900"><Pencil size={15} /></button>
                        <button onClick={() => handleDelete(d.id)} className="text-ink-400 hover:text-red-600"><Trash2 size={15} /></button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
