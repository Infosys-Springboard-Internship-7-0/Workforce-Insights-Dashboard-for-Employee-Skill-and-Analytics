import { useEffect, useState } from "react";
import { Table2, ChevronLeft, ChevronRight, AlertCircle } from "lucide-react";
import api from "../api/client";

export default function DataViewerPage() {
  const [datasets, setDatasets] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [table, setTable] = useState(null);
  const [page, setPage] = useState(1);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingTable, setLoadingTable] = useState(false);

  useEffect(() => {
    api
      .get("/api/data-viewer/datasets")
      .then((res) => {
        setDatasets(res.data);
        if (res.data.length > 0) setActiveId(res.data[0].id);
      })
      .finally(() => setLoadingList(false));
  }, []);

  useEffect(() => {
    if (!activeId) return;
    setLoadingTable(true);
    api
      .get(`/api/data-viewer/datasets/${activeId}`, { params: { page, page_size: 25 } })
      .then((res) => setTable(res.data))
      .finally(() => setLoadingTable(false));
  }, [activeId, page]);

  function selectDataset(id) {
    setActiveId(id);
    setPage(1);
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-ink-900 flex items-center gap-2">
          <Table2 size={20} /> Data Viewer
        </h1>
        <p className="text-sm text-ink-500">Browse uploaded datasets in table format.</p>
      </div>

      {loadingList ? (
        <div className="text-ink-500 text-sm">Loading datasets…</div>
      ) : datasets.length === 0 ? (
        <div className="card p-10 text-center">
          <AlertCircle className="mx-auto text-ink-300 mb-3" size={28} />
          <p className="text-ink-500 text-sm">No datasets have been uploaded yet.</p>
        </div>
      ) : (
        <div className="grid lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1 space-y-2">
            {datasets.map((d) => (
              <button
                key={d.id}
                onClick={() => selectDataset(d.id)}
                className={`w-full text-left px-4 py-3 border text-sm transition-colors ${
                  d.id === activeId ? "border-ink-900 bg-white font-semibold" : "border-ink-100 bg-white text-ink-500 hover:border-ink-300"
                }`}
              >
                <div className="truncate">{d.filename}</div>
                <div className="text-xs font-normal text-ink-500">{d.category}</div>
              </button>
            ))}
          </div>

          <div className="lg:col-span-3">
            {loadingTable || !table ? (
              <div className="card p-10 text-center text-ink-500 text-sm">Loading table…</div>
            ) : (
              <div className="card overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-ink-900 text-white">
                        {table.columns.map((c) => (
                          <th key={c} className="text-left px-4 py-2.5 font-semibold whitespace-nowrap">
                            {c}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {table.rows.map((row, i) => (
                        <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-ink-50"}>
                          {table.columns.map((c) => (
                            <td key={c} className="px-4 py-2 text-ink-700 whitespace-nowrap border-t border-ink-100">
                              {String(row[c])}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="flex items-center justify-between px-4 py-3 border-t border-ink-100 text-sm">
                  <span className="text-ink-500">
                    Page {table.page} of {table.total_pages} — {table.total_rows} rows
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page <= 1}
                      className="btn-secondary flex items-center gap-1 px-3 py-1.5 text-xs disabled:opacity-40"
                    >
                      <ChevronLeft size={14} /> Prev
                    </button>
                    <button
                      onClick={() => setPage((p) => Math.min(table.total_pages, p + 1))}
                      disabled={page >= table.total_pages}
                      className="btn-secondary flex items-center gap-1 px-3 py-1.5 text-xs disabled:opacity-40"
                    >
                      Next <ChevronRight size={14} />
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
