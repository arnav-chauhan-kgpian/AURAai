"use client";

import { forwardRef, useCallback, useState } from "react";

import { buttonVariants, type ButtonVariantProps } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    ButtonVariantProps {}

interface Ripple {
  id: number;
  x: number;
  y: number;
  size: number;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, onPointerDown, children, ...props }, ref) => {
    const [ripples, setRipples] = useState<Ripple[]>([]);

    const handlePointerDown = useCallback(
      (event: React.PointerEvent<HTMLButtonElement>) => {
        const rect = event.currentTarget.getBoundingClientRect();
        const rippleSize = Math.max(rect.width, rect.height);
        const id = Date.now() + Math.random();
        setRipples((prev) => [
          ...prev,
          {
            id,
            size: rippleSize,
            x: event.clientX - rect.left - rippleSize / 2,
            y: event.clientY - rect.top - rippleSize / 2,
          },
        ]);
        window.setTimeout(() => setRipples((prev) => prev.filter((r) => r.id !== id)), 600);
        onPointerDown?.(event);
      },
      [onPointerDown],
    );

    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size }), className)}
        onPointerDown={handlePointerDown}
        {...props}
      >
        {ripples.map((ripple) => (
          <span
            key={ripple.id}
            className="aura-ripple"
            style={{ left: ripple.x, top: ripple.y, width: ripple.size, height: ripple.size }}
          />
        ))}
        {children}
      </button>
    );
  },
);
Button.displayName = "Button";
