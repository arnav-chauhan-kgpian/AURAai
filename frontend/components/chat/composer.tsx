"use client";

import { ArrowUp, ImagePlus, Loader2, Shirt, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useChatStream } from "@/hooks/use-chat-stream";
import { useSessionStore } from "@/lib/store";
import { cn } from "@/lib/utils";

export function Composer() {
  const [text, setText] = useState("");
  const [face, setFace] = useState<File | null>(null);
  const [garment, setGarment] = useState<File | null>(null);
  const status = useSessionStore((s) => s.status);
  const { send } = useChatStream();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const streaming = status === "streaming";
  const canSend = text.trim().length > 0 && !streaming;

  useEffect(() => {
    const onPrompt = (event: Event) => {
      const detail = (event as CustomEvent<string>).detail;
      setText(detail);
      textareaRef.current?.focus();
    };
    window.addEventListener("aura:prompt", onPrompt);
    return () => window.removeEventListener("aura:prompt", onPrompt);
  }, []);

  const submit = () => {
    if (!canSend) return;
    void send({ message: text.trim(), faceImage: face, garmentImage: garment });
    setText("");
    setFace(null);
    setGarment(null);
  };

  return (
    <div className="border-t border-border bg-card/40 p-3 sm:p-4">
      {(face || garment) && (
        <div className="mb-2 flex flex-wrap gap-2">
          {face && <Attachment label={face.name} onRemove={() => setFace(null)} />}
          {garment && <Attachment label={garment.name} onRemove={() => setGarment(null)} />}
        </div>
      )}
      <div className="flex items-end gap-2 rounded-3xl border border-border bg-background p-2">
        <FileButton
          icon={<ImagePlus className="size-[18px]" />}
          label="Attach a selfie"
          onFile={setFace}
        />
        <FileButton
          icon={<Shirt className="size-[18px]" />}
          label="Attach a garment"
          onFile={setGarment}
        />
        <Textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Describe a concern or a look…"
          rows={1}
          className="border-0 bg-transparent focus-visible:ring-0"
          aria-label="Message"
        />
        <Button
          size="icon"
          onClick={submit}
          disabled={!canSend}
          aria-label="Send message"
          className={cn("shrink-0", !canSend && "opacity-60")}
        >
          {streaming ? <Loader2 className="size-4 animate-spin" /> : <ArrowUp className="size-4" />}
        </Button>
      </div>
      <p className="mt-2 px-2 text-center text-2xs text-muted-foreground">
        AuraAI can make mistakes. For persistent skin concerns, see a dermatologist.
      </p>
    </div>
  );
}

function FileButton({
  icon,
  label,
  onFile,
}: {
  icon: React.ReactNode;
  label: string;
  onFile: (file: File) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  return (
    <>
      <button
        type="button"
        aria-label={label}
        title={label}
        onClick={() => inputRef.current?.click()}
        className="grid size-9 shrink-0 place-items-center rounded-full text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground focus-visible:ring-focus"
      >
        {icon}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onFile(file);
          e.target.value = "";
        }}
      />
    </>
  );
}

function Attachment({ label, onRemove }: { label: string; onRemove: () => void }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-secondary/60 py-1 pl-3 pr-1.5 text-xs">
      <span className="max-w-[10rem] truncate">{label}</span>
      <button
        type="button"
        onClick={onRemove}
        aria-label={`Remove ${label}`}
        className="grid size-4 place-items-center rounded-full hover:bg-background"
      >
        <X className="size-3" />
      </button>
    </span>
  );
}
