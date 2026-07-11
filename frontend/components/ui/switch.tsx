"use client";

import { cn } from "@/lib/utils";

interface SwitchProps {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  id?: string;
  "aria-label"?: string;
  disabled?: boolean;
  className?: string;
}

/** Accessible toggle switch (role=switch, keyboard-operable). */
export function Switch({
  checked,
  onCheckedChange,
  id,
  disabled,
  className,
  ...aria
}: SwitchProps) {
  return (
    <button
      id={id}
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={aria["aria-label"]}
      disabled={disabled}
      onClick={() => onCheckedChange(!checked)}
      className={cn(
        "relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors focus-visible:ring-focus disabled:opacity-50",
        checked ? "bg-brand" : "bg-muted",
        className,
      )}
    >
      <span
        className={cn(
          "inline-block size-5 translate-x-0.5 rounded-full bg-white shadow-sm transition-transform duration-200",
          checked && "translate-x-[22px]",
        )}
      />
    </button>
  );
}
