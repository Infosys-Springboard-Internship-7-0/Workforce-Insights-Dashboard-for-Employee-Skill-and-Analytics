import { useState } from "react";
import { Lightbulb, RefreshCw, FileText, AlertCircle } from "lucide-react";
import api from "../../api/client";

export default function AdminRecommendationsPage() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function generate() {
    setLoading(true);
    setError("");
    try {
      const res = await api.get("/api/chat/recommendations");
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not generate recommendations.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-8 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-ink-900 flex items-center gap-2">
            <Lightbulb size={20} /> Recommendations
          </h1>
          <p className="text-sm text-ink-500">
            AI-generated, data-grounded recommendations based on all uploaded documents.
          </p>
        </div>
        <button onClick={generate} disabled={loading} className="btn-primary flex items-center gap-2">
          <RefreshCw size={15} className={loading ? "animate-spin" : ""} />
          {loading ? "Analyzing…" : result ? "Regenerate" : "Generate"}
        </button>
      </div>

      {error && (
        <div className="flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 mb-6">
          <AlertCircle size={16} className="shrink-0 mt-0.5" /> {error}
        </div>
      )}

      {!result && !loading && !error && (
        <div className="card p-10 text-center text-ink-500 text-sm">
          Click "Generate" to analyze uploaded documents and data for leadership recommendations.
          <div className="text-xs mt-2 text-ink-300">
            Recommendations require human review before being acted on.
          </div>
        </div>
      )}

      {result && (
        <div className="card p-6">
          <div className="whitespace-pre-wrap text-sm text-ink-900 leading-relaxed">{result.answer}</div>

          {result.sources?.length > 0 && (
            <div className="mt-6 pt-4 border-t border-ink-100">
              <div className="text-xs font-semibold text-ink-500 flex items-center gap-1 mb-2">
                <FileText size={12} /> Based on
              </div>
              <div className="flex flex-wrap gap-2">
                {result.sources.map((s, i) => (
                  <span key={i} className="text-xs bg-ink-100 text-ink-700 px-2.5 py-1">
                    {s.document}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
