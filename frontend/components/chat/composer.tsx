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
  const [category, setCategory] = useState("upper_body");
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
    void send({
      message: text.trim(),
      faceImage: face,
      garmentImage: garment,
      garmentCategory: category,
    });
    setText("");
    setFace(null);
    setGarment(null);
  };

  return (
    <div className="border-t border-border bg-card/40 p-3 sm:p-4">
      {/* Labeled attach controls — make skin analysis + try-on discoverable. */}
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <FilePill
          label="Selfie"
          icon={<ImagePlus className="size-4" />}
          file={face}
          onFile={setFace}
          onClear={() => setFace(null)}
        />
        <FilePill
          label="Garment"
          icon={<Shirt className="size-4" />}
          file={garment}
          onFile={setGarment}
          onClear={() => setGarment(null)}
        />
        {garment && (
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            aria-label="Garment type"
            className="rounded-full border border-border bg-background px-3 py-1.5 text-xs font-medium focus-visible:ring-focus"
          >
            <option value="upper_body">Top / Jacket</option>
            <option value="lower_body">Bottoms</option>
            <option value="dress">Dress</option>
            <option value="full_body">Full outfit</option>
          </select>
        )}
        <span className="text-2xs text-muted-foreground">
          Add a <b className="font-medium text-foreground">Selfie</b> for skin analysis · add a{" "}
          <b className="font-medium text-foreground">Garment</b> too to try it on
        </span>
      </div>

      <div className="flex items-end gap-2 rounded-3xl border border-border bg-background p-2 pl-4">
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

function FilePill({
  label,
  icon,
  file,
  onFile,
  onClear,
}: {
  label: string;
  icon: React.ReactNode;
  file: File | null;
  onFile: (file: File) => void;
  onClear: () => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const active = file !== null;
  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors",
        active
          ? "border-primary/50 bg-primary/10 text-primary"
          : "border-border text-muted-foreground hover:bg-secondary hover:text-foreground",
      )}
    >
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        aria-label={active ? `Change ${label}` : `Add a ${label}`}
        className="inline-flex items-center gap-1.5 rounded-full focus-visible:ring-focus"
      >
        {icon}
        {active ? <span className="max-w-[7rem] truncate">{file!.name}</span> : label}
      </button>
      {active && (
        <button
          type="button"
          onClick={onClear}
          aria-label={`Remove ${label}`}
          className="grid size-4 place-items-center rounded-full hover:bg-background/60"
        >
          <X className="size-3" />
        </button>
      )}
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) onFile(f);
          e.target.value = "";
        }}
      />
    </div>
  );
}
