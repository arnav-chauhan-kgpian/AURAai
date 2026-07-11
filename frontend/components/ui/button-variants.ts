import { cva, type VariantProps } from "class-variance-authority";

/**
 * Button class variants, kept in a non-client module so server components
 * (e.g. styled `Link`s) can import them without crossing the client boundary.
 */
export const buttonVariants = cva(
  "relative inline-flex items-center justify-center gap-2 overflow-hidden whitespace-nowrap rounded-full text-sm font-medium transition-all focus-visible:ring-focus disabled:pointer-events-none disabled:opacity-50 [&_svg]:size-4 [&_svg]:shrink-0 active:scale-[0.98]",
  {
    variants: {
      variant: {
        primary:
          "bg-brand text-white shadow-glow hover:brightness-110 hover:shadow-[0_10px_50px_-8px_hsl(var(--primary)/0.6)]",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/70 border border-border",
        outline: "border border-border bg-transparent hover:bg-secondary/60",
        ghost: "hover:bg-secondary/60",
        glass: "glass text-foreground hover:bg-card/80",
        destructive: "bg-destructive text-destructive-foreground hover:brightness-110",
      },
      size: {
        sm: "h-9 px-4",
        md: "h-11 px-6",
        lg: "h-12 px-8 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  },
);

export type ButtonVariantProps = VariantProps<typeof buttonVariants>;
