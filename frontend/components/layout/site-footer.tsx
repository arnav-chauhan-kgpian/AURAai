import { Sparkles } from "lucide-react";
import Link from "next/link";

import { NAV_LINKS } from "@/lib/constants";

export function SiteFooter() {
  return (
    <footer className="border-t border-border">
      <div className="container flex flex-col items-center justify-between gap-4 py-8 sm:flex-row">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span className="grid size-6 place-items-center rounded-md bg-brand">
            <Sparkles className="size-3.5 text-white" />
          </span>
          AuraAI — Personal Skin &amp; Style Agent
        </div>
        <nav className="flex items-center gap-5 text-sm text-muted-foreground" aria-label="Footer">
          {NAV_LINKS.map((link) => (
            <Link key={link.href} href={link.href} className="hover:text-foreground">
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </footer>
  );
}
