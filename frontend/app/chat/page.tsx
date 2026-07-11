import { ChatPanel } from "@/components/chat/chat-panel";
import { ChatResultsHint } from "@/components/chat/chat-results-hint";

export default function ChatPage() {
  return (
    <div className="mx-auto h-[calc(100vh-4rem)] max-w-3xl sm:p-4">
      <div className="h-full overflow-hidden border-x border-border sm:rounded-2xl sm:border">
        <ChatPanel className="h-full" />
      </div>
      <ChatResultsHint />
    </div>
  );
}
