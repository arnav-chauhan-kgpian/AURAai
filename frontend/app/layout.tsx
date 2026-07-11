import type { Metadata, Viewport } from "next";

import { Onboarding } from "@/components/onboarding/onboarding";
import { SiteHeader } from "@/components/layout/site-header";
import { Providers } from "@/app/providers";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "AuraAI — Your Personal AI Skin & Style Agent",
  description:
    "An autonomous AI stylist that analyses your skin, renders virtual try-ons, and plans personalised skincare and outfit recommendations.",
  applicationName: "AuraAI",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: dark)", color: "#0a0a0f" },
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="min-h-screen">
        <Providers>
          <div className="relative flex min-h-screen flex-col">
            <SiteHeader />
            <div className="flex-1">{children}</div>
          </div>
          <Onboarding />
        </Providers>
      </body>
    </html>
  );
}
