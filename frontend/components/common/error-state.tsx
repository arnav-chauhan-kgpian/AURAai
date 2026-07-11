"use client";

import { motion } from "framer-motion";
import {
  RefreshCw,
  ScanFace,
  ServerCrash,
  Timer,
  UploadCloud,
  Users,
  type LucideIcon,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type ErrorKind =
  | "no_face_detected"
  | "multiple_faces_detected"
  | "upload_error"
  | "rate_limited"
  | "provider_server_error"
  | "unknown";

interface ErrorMeta {
  icon: LucideIcon;
  title: string;
  description: string;
  action: string;
}

const ERROR_META: Record<ErrorKind, ErrorMeta> = {
  no_face_detected: {
    icon: ScanFace,
    title: "We couldn't find a face",
    description: "Use a clear, front-facing photo in good lighting with your whole face visible.",
    action: "Try another photo",
  },
  multiple_faces_detected: {
    icon: Users,
    title: "More than one face detected",
    description: "Skin analysis works best with a single person. Crop to just you and retry.",
    action: "Upload a solo photo",
  },
  upload_error: {
    icon: UploadCloud,
    title: "That image didn't upload",
    description: "It may be too large or an unsupported format. Try a JPG or PNG under 10 MB.",
    action: "Choose another file",
  },
  rate_limited: {
    icon: Timer,
    title: "Just a moment",
    description: "We're handling a lot of requests. Give it a few seconds and try again.",
    action: "Retry",
  },
  provider_server_error: {
    icon: ServerCrash,
    title: "The analysis service hiccuped",
    description: "This is on our side. You can retry, or continue in Demo Mode.",
    action: "Retry",
  },
  unknown: {
    icon: ServerCrash,
    title: "Something went wrong",
    description: "An unexpected error occurred. Your session is safe — please try again.",
    action: "Try again",
  },
};

/** Maps a backend error code to a friendly error kind. */
export function toErrorKind(code?: string): ErrorKind {
  if (code && code in ERROR_META) return code as ErrorKind;
  return "unknown";
}

export function ErrorState({
  kind,
  onRetry,
  className,
}: {
  kind: ErrorKind;
  onRetry?: () => void;
  className?: string;
}) {
  const meta = ERROR_META[kind];
  const Icon = meta.icon;

  return (
    <motion.div
      role="alert"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className={cn(
        "flex flex-col items-center justify-center rounded-lg border border-border bg-card px-6 py-10 text-center",
        className,
      )}
    >
      <span className="grid size-14 place-items-center rounded-2xl bg-destructive/10 text-destructive">
        <Icon className="size-6" />
      </span>
      <p className="mt-5 text-base font-semibold">{meta.title}</p>
      <p className="mt-1.5 max-w-sm text-sm leading-relaxed text-muted-foreground">
        {meta.description}
      </p>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry} className="mt-6">
          <RefreshCw className="size-4" />
          {meta.action}
        </Button>
      )}
    </motion.div>
  );
}
