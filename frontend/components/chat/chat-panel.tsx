"use client";

import { MessageSquare, RotateCcw } from "lucide-react";

import { Composer } from "@/components/chat/composer";
import { MessageList } from "@/components/chat/message-list";
import { useSessionStore } from "@/lib/store";
import { cn } from "@/lib/utils";

export function ChatPanel({ className }: { className?: string }) {
  const clear = useSessionStore((s) => s.clearConversation);
  const hasMessages = useSessionStore((s) => s.messages.length > 0);

  return (
    <section
      className={cn("flex h-full min-h-0 flex-col overflow-hidden bg-card/30", className)}
      aria-label="Conversation"
    >
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-border px-4">
        <div className="flex items-center gap-2 text-sm font-medium">
          <MessageSquare className="size-4 text-primary" />
          Conversation
        </div>
        {hasMessages && (
          <button
            type="button"
            onClick={clear}
            className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground focus-visible:ring-focus"
          >
            <RotateCcw className="size-3.5" /> New chat
          </button>
        )}
      </header>
      <div className="min-h-0 flex-1 overflow-y-auto">
        <MessageList />
      </div>
      <Composer />
    </section>
  );
}
