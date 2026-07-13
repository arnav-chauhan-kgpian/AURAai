"use client";

import { Sparkles } from "lucide-react";
import { useEffect, useRef } from "react";

import { InlineTryOn } from "@/components/chat/inline-try-on";
import { MessageBubble } from "@/components/chat/message-bubble";
import { useSessionStore } from "@/lib/store";

const PROMPTS = [
  "I have acne. What should I wear?",
  "What colors suit me?",
  "My skin feels oily.",
  "Suggest a smart-casual outfit.",
];

export function MessageList() {
  const messages = useSessionStore((s) => s.messages);
  const bottomRef = useRef<HTMLDivElement>(null);
  const lastContent = messages[messages.length - 1]?.content;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, lastContent]);

  if (messages.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center px-6 text-center">
        <span className="grid size-14 place-items-center rounded-2xl bg-brand shadow-glow">
          <Sparkles className="size-7 text-white" />
        </span>
        <h2 className="mt-5 text-lg font-semibold">Ask AuraAI anything</h2>
        <p className="mt-1 max-w-xs text-sm text-muted-foreground">
          Describe a concern or a look. The agent decides what to analyse.
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-2">
          {PROMPTS.map((prompt) => (
            <Suggestion key={prompt} text={prompt} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-5 p-4 sm:p-6">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      <InlineTryOn />
      <div ref={bottomRef} />
    </div>
  );
}

function Suggestion({ text }: { text: string }) {
  return (
    <button
      type="button"
      onClick={() => window.dispatchEvent(new CustomEvent("aura:prompt", { detail: text }))}
      className="rounded-full border border-border bg-card/60 px-3.5 py-1.5 text-xs text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground focus-visible:ring-focus"
    >
      {text}
    </button>
  );
}
