"use client";

import { motion } from "framer-motion";
import { ImageIcon, Sparkles } from "lucide-react";

import { Markdown } from "@/components/chat/markdown";
import { TypingIndicator } from "@/components/chat/typing-indicator";
import { cn } from "@/lib/utils";
import type { UiMessage } from "@/lib/store";

export function MessageBubble({ message }: { message: UiMessage }) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className={cn("flex gap-3", isUser ? "flex-row-reverse" : "flex-row")}
    >
      {!isUser && (
        <span className="mt-0.5 grid size-8 shrink-0 place-items-center rounded-xl bg-brand shadow-glow">
          <Sparkles className="size-4 text-white" />
        </span>
      )}
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-4 py-3",
          isUser
            ? "rounded-tr-sm bg-brand text-white"
            : "rounded-tl-sm border border-border bg-card",
        )}
      >
        {message.hasImage && isUser && (
          <span className="mb-2 inline-flex items-center gap-1.5 rounded-full bg-white/20 px-2 py-0.5 text-2xs font-medium">
            <ImageIcon className="size-3" /> Photo attached
          </span>
        )}
        {message.streaming && message.content.length === 0 ? (
          <TypingIndicator />
        ) : isUser ? (
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
        ) : (
          <Markdown>{message.content}</Markdown>
        )}
      </div>
    </motion.div>
  );
}
