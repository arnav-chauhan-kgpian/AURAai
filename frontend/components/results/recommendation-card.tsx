"use client";

import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { humanize } from "@/lib/utils";
import type { ProductRecommendation } from "@/types/api";

export function RecommendationCard({
  item,
  index,
}: {
  item: ProductRecommendation;
  index: number;
}) {
  const content = (
    <>
      <div className="flex items-start justify-between gap-3">
        <h4 className="font-medium leading-snug">{item.title}</h4>
        {item.url && (
          <ArrowUpRight className="size-4 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
        )}
      </div>
      <Badge variant="outline" className="mt-2 w-fit">
        {humanize(item.category)}
      </Badge>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{item.rationale}</p>
    </>
  );

  const className =
    "group flex flex-col rounded-2xl border border-border bg-card/60 p-4 transition-all hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-soft";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, ease: [0.16, 1, 0.3, 1] }}
    >
      {item.url ? (
        <a href={item.url} target="_blank" rel="noopener noreferrer" className={className}>
          {content}
        </a>
      ) : (
        <div className={className}>{content}</div>
      )}
    </motion.div>
  );
}
