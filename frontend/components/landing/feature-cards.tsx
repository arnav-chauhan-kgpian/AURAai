"use client";

import { motion } from "framer-motion";
import { Palette, ScanFace, Shield, Shirt, type LucideIcon } from "lucide-react";

const FEATURES: { icon: LucideIcon; title: string; body: string; accent: string }[] = [
  {
    icon: ScanFace,
    title: "Skin AI",
    body: "Dermatologist-grade analysis scores concerns like acne, pores and redness from a single selfie.",
    accent: "from-violet-500/20 to-transparent",
  },
  {
    icon: Shirt,
    title: "Virtual Try-On",
    body: "See any garment rendered on you with realistic fit, fabric and drape before you buy.",
    accent: "from-fuchsia-500/20 to-transparent",
  },
  {
    icon: Palette,
    title: "AI Stylist",
    body: "An agent plans skincare routines and complete outfits tuned to your palette and goals.",
    accent: "from-indigo-500/20 to-transparent",
  },
  {
    icon: Shield,
    title: "Privacy First",
    body: "Photos are processed for analysis only — never sold, never used to train models.",
    accent: "from-emerald-500/20 to-transparent",
  },
];

export function FeatureCards() {
  return (
    <section className="container py-24">
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          One agent, your whole routine
        </h2>
        <p className="mt-4 text-muted-foreground">
          AuraAI decides which tools to run for every request — you never pick an API.
        </p>
      </div>

      <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {FEATURES.map((feature, index) => (
          <motion.article
            key={feature.title}
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ duration: 0.55, delay: index * 0.08, ease: [0.16, 1, 0.3, 1] }}
            className="group card-hover relative overflow-hidden rounded-lg border border-border bg-card p-6"
          >
            <div
              className={`absolute -right-8 -top-8 size-32 rounded-full bg-gradient-to-br ${feature.accent} blur-2xl transition-opacity group-hover:opacity-100`}
            />
            <div className="relative">
              <span className="grid size-11 place-items-center rounded-2xl border border-border bg-secondary/60">
                <feature.icon className="size-5 text-primary" />
              </span>
              <h3 className="mt-5 text-lg font-semibold">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{feature.body}</p>
            </div>
          </motion.article>
        ))}
      </div>
    </section>
  );
}
