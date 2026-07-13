import type { NextConfig } from "next";

// Conservative security headers for the HTML app. No CSP here — a strict CSP
// with Next's inline runtime + Clerk is fragile; these headers give clickjacking,
// MIME-sniffing, and referrer protection without that risk.
const securityHeaders = [
  { key: "X-Frame-Options", value: "SAMEORIGIN" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  {
    key: "Strict-Transport-Security",
    value: "max-age=63072000; includeSubDomains; preload",
  },
];

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Don't advertise the framework/version in responses.
  poweredByHeader: false,
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.perfectcorp.com" },
      { protocol: "https", hostname: "**.supabase.co" },
    ],
  },
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
};

export default nextConfig;
