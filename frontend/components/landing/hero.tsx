"use client";

import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import Link from "next/link";

import { MeshGradient } from "@/components/landing/mesh-gradient";
import { buttonVariants } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12, delayChildren: 0.05 } },
};
const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] } },
};

export function Hero() {
  return (
    <section className="relative flex min-h-[calc(100vh-4rem)] items-center overflow-hidden">
      <MeshGradient />
      <div className="container">
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="mx-auto flex max-w-3xl flex-col items-center text-center"
        >
          <motion.div variants={item}>
            <span className="inline-flex items-center gap-2 rounded-full border border-border bg-card/50 px-4 py-1.5 text-sm text-muted-foreground backdrop-blur">
              <Sparkles className="size-3.5 text-primary" />
              Powered by an autonomous AI agent
            </span>
          </motion.div>

          <motion.h1
            variants={item}
            className="mt-6 text-balance text-5xl font-semibold leading-[1.05] tracking-tight sm:text-6xl md:text-7xl"
          >
            Your Personal{" "}
            <span className="text-gradient">AI Skin &amp; Style</span> Agent
          </motion.h1>

          <motion.p
            variants={item}
            className="mt-6 max-w-xl text-balance text-lg text-muted-foreground"
          >
            Snap a selfie and AuraAI analyses your skin, finds the colors that suit
            you, and styles complete looks — planned and reasoned by an agent, not a
            form.
          </motion.p>

          <motion.div variants={item} className="mt-9 flex flex-col items-center gap-3 sm:flex-row">
            <Link href="/chat" className={cn(buttonVariants({ size: "lg" }), "group")}>
              Start Analysis
              <ArrowRight className="transition-transform group-hover:translate-x-1" />
            </Link>
            <Link href="/dashboard" className={buttonVariants({ variant: "glass", size: "lg" })}>
              Open Dashboard
            </Link>
          </motion.div>

          <motion.p variants={item} className="mt-6 text-xs text-muted-foreground">
            No sign-up needed · Your photos never leave the analysis pipeline
          </motion.p>
        </motion.div>
      </div>
    </section>
  );
}
