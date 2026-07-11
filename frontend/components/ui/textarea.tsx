import { forwardRef } from "react";

import { cn } from "@/lib/utils";

export const Textarea = forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={cn(
      "flex min-h-[52px] w-full resize-none rounded-2xl border border-border bg-transparent px-4 py-3 text-sm outline-none transition-colors placeholder:text-muted-foreground focus-visible:border-primary/50 focus-visible:ring-focus disabled:opacity-50",
      className,
    )}
    {...props}
  />
));
Textarea.displayName = "Textarea";
