"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import Link from "next/link";

import { buttonVariants } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

export function CtaSection() {
  return (
    <section className="container pb-28">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="relative overflow-hidden rounded-xl border border-border p-10 text-center sm:p-16"
      >
        <div className="absolute inset-0 -z-10 bg-brand opacity-[0.12]" />
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(60%_120%_at_50%_0%,hsl(var(--primary)/0.25),transparent)]" />
        <h2 className="mx-auto max-w-xl text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
          Meet the stylist that actually understands your skin
        </h2>
        <p className="mx-auto mt-4 max-w-md text-muted-foreground">
          Start a conversation and watch the agent plan, analyse and recommend in real time.
        </p>
        <Link
          href="/chat"
          className={cn(buttonVariants({ size: "lg" }), "group mt-8")}
        >
          Start Analysis
          <ArrowRight className="transition-transform group-hover:translate-x-1" />
        </Link>
      </motion.div>
    </section>
  );
}
