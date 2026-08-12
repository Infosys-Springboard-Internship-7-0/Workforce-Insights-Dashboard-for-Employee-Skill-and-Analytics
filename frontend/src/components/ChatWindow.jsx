import { useState, useRef, useEffect } from "react";
import { Send, FileText, Sparkles, Loader2 } from "lucide-react";
import api from "../api/client";

/**
 * Reusable RAG chat UI. Used by both the public AI Workforce Assistant page
 * (queryEndpoint="/api/chat/query") and the admin decision-support chatbot
 * (queryEndpoint="/api/chat/admin-query"), so both stay visually consistent
 * and share the same request/response handling and suggested-questions UX.
 */
export default function ChatWindow({ queryEndpoint, suggestedQuestionsUrl, emptyStateText }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const bottomRef = useRef(null);

  useEffect(() => {
    api
      .get(suggestedQuestionsUrl)
      .then((res) => setSuggestions(res.data.questions || []))
      .catch(() => setSuggestions([]));
  }, [suggestedQuestionsUrl]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(overrideText) {
    const question = (overrideText ?? input).trim();
    if (!question || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.post(queryEndpoint, { question });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: res.data.answer, sources: res.data.sources || [], grounded: res.data.grounded },
      ]);
    } catch (err) {
      const detail = err.response?.data?.detail || "Something went wrong. Please try again.";
      setMessages((prev) => [...prev, { role: "assistant", text: detail, error: true }]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="max-w-2xl mx-auto text-center pt-10">
            <div className="w-14 h-14 bg-ink-900 mx-auto flex items-center justify-center mb-4">
              <Sparkles className="text-white" size={24} />
            </div>
            <p className="text-ink-500 text-sm mb-6">{emptyStateText}</p>

            {suggestions.length > 0 && (
              <div className="grid sm:grid-cols-2 gap-2 text-left">
                {suggestions.map((q) => (
                  <button
                    key={q}
                    onClick={() => sendMessage(q)}
                    className="card px-4 py-3 text-sm text-ink-700 hover:border-ink-900 transition-colors text-left"
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                m.role === "user"
                  ? "bg-ink-900 text-white"
                  : m.error
                  ? "bg-red-50 border border-red-200 text-red-700"
                  : "card text-ink-900"
              }`}
            >
              {m.text}

              {m.sources && m.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-ink-100 space-y-1.5">
                  <div className="text-xs font-semibold text-ink-500 flex items-center gap-1">
                    <FileText size={12} /> Sources
                  </div>
                  {m.sources.map((s, si) => (
                    <div key={si} className="text-xs text-ink-500">
                      <span className="font-medium text-ink-700">{s.document}</span>
                      {s.category ? ` — ${s.category}` : ""}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="card px-4 py-3 text-sm text-ink-500 flex items-center gap-2">
              <Loader2 size={14} className="animate-spin" /> Thinking…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-ink-100 bg-white px-6 py-4">
        <div className="max-w-3xl mx-auto flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question…"
            rows={1}
            className="input-field resize-none"
          />
          <button onClick={() => sendMessage()} disabled={loading || !input.trim()} className="btn-primary flex items-center gap-1.5 shrink-0">
            <Send size={15} /> Send
          </button>
        </div>
      </div>
    </div>
  );
}
