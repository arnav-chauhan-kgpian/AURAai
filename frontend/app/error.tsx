"use client";

import { useEffect } from "react";

import { ErrorState } from "@/components/common/error-state";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-[70vh] items-center justify-center px-6">
      <ErrorState kind="unknown" onRetry={reset} className="max-w-md" />
    </div>
  );
}
