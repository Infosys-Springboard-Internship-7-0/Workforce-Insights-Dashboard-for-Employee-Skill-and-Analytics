import ChatWindow from "../../components/ChatWindow";
import { MessageSquareText } from "lucide-react";

export default function AdminAssistantPage() {
  return (
    <div className="h-full flex flex-col">
      <div className="px-8 pt-8 pb-2 shrink-0">
        <h1 className="text-xl font-bold text-ink-900 flex items-center gap-2">
          <MessageSquareText size={20} /> Admin Decision Assistant
        </h1>
        <p className="text-sm text-ink-500">
          Recommendation-focused analysis grounded in uploaded documents and data. For leadership
          decision support — recommendations always require human review.
        </p>
      </div>
      <div className="flex-1 min-h-0">
        <ChatWindow
          queryEndpoint="/api/chat/admin-query"
          suggestedQuestionsUrl="/api/chat/suggested-questions?audience=admin"
          emptyStateText="Ask an analytics or decision-support question grounded in your uploaded data."
        />
      </div>
    </div>
  );
}
