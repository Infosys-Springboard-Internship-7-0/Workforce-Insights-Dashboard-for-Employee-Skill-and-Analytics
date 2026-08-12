import ChatWindow from "../components/ChatWindow";

export default function ChatbotPage() {
  return (
    <div className="max-w-5xl mx-auto h-[calc(100vh-64px)] flex flex-col">
      <div className="px-6 pt-6 pb-2">
        <h1 className="text-xl font-bold text-ink-900">AI Workforce Assistant</h1>
        <p className="text-sm text-ink-500">
          Ask questions about policies and workforce documents. Answers are grounded in
          admin-uploaded documents via retrieval-augmented generation.
        </p>
      </div>
      <div className="flex-1 min-h-0">
        <ChatWindow
          queryEndpoint="/api/chat/query"
          suggestedQuestionsUrl="/api/chat/suggested-questions?audience=assistant"
          emptyStateText="Ask me anything about company policy, benefits, or workforce documents."
        />
      </div>
    </div>
  );
}
