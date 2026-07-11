"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Menu, Sparkles, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { AuthControls } from "@/components/auth/auth-controls";
import { DemoBadge } from "@/components/layout/demo-badge";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { buttonVariants } from "@/components/ui/button-variants";
import { NAV_LINKS } from "@/lib/constants";
import { cn } from "@/lib/utils";

export function SiteHeader() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 h-16 w-full">
      <div className="glass absolute inset-0 border-x-0 border-t-0" aria-hidden />
      <div className="container relative flex h-16 items-center justify-between gap-4">
        <Link href="/" className="flex items-center gap-2.5 focus-visible:ring-focus rounded-full">
          <span className="grid size-9 place-items-center rounded-xl bg-brand shadow-glow">
            <Sparkles className="size-5 text-white" />
          </span>
          <span className="text-lg font-semibold tracking-tight">Aura<span className="text-gradient">AI</span></span>
        </Link>
        <DemoBadge />

        <nav className="hidden items-center gap-1 md:flex" aria-label="Primary">
          {NAV_LINKS.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "relative rounded-full px-4 py-2 text-sm font-medium transition-colors focus-visible:ring-focus",
                  active ? "text-foreground" : "text-muted-foreground hover:text-foreground",
                )}
              >
                {active && (
                  <motion.span
                    layoutId="nav-pill"
                    className="absolute inset-0 rounded-full bg-secondary"
                    transition={{ type: "spring", stiffness: 400, damping: 32 }}
                  />
                )}
                <span className="relative">{link.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Link
            href="/chat"
            className={cn(buttonVariants({ size: "sm" }), "hidden sm:inline-flex")}
          >
            Start Analysis
          </Link>
          <AuthControls />
          <button
            type="button"
            className="grid size-10 place-items-center rounded-full border border-border md:hidden focus-visible:ring-focus"
            aria-label="Toggle menu"
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
          >
            {open ? <X className="size-5" /> : <Menu className="size-5" />}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {open && (
          <motion.nav
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="glass-strong absolute inset-x-0 top-16 border-x-0 p-4 md:hidden"
            aria-label="Mobile"
          >
            <ul className="flex flex-col gap-1">
              {NAV_LINKS.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    onClick={() => setOpen(false)}
                    className={cn(
                      "block rounded-xl px-4 py-3 text-sm font-medium transition-colors",
                      pathname === link.href
                        ? "bg-secondary text-foreground"
                        : "text-muted-foreground hover:bg-secondary/60",
                    )}
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  );
}
