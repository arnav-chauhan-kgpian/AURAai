"use client";

import { Sparkles } from "lucide-react";

import { RecommendationCard } from "@/components/results/recommendation-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { colorToCss, humanize } from "@/lib/utils";
import type { RecommendationSet } from "@/types/api";

export function Recommendations({ data }: { data: RecommendationSet }) {
  const tabs = [
    { value: "skincare", label: "Skincare", items: data.skincare },
    { value: "outfit", label: "Fashion", items: data.outfit },
    { value: "shopping", label: "Shopping", items: data.shopping },
  ].filter((t) => t.items.length > 0);

  const defaultTab = tabs[0]?.value ?? "colors";

  return (
    <Card>
      <CardHeader className="flex-row items-center gap-2 space-y-0">
        <span className="grid size-8 place-items-center rounded-lg bg-primary/15 text-primary">
          <Sparkles className="size-4" />
        </span>
        <div>
          <CardTitle>Recommendations</CardTitle>
          {data.summary && (
            <p className="mt-0.5 text-xs text-muted-foreground">{data.summary}</p>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue={defaultTab}>
          <TabsList className="mb-4 flex-wrap">
            {tabs.map((tab) => (
              <TabsTrigger key={tab.value} value={tab.value}>
                {tab.label}
              </TabsTrigger>
            ))}
            {data.colors.length > 0 && <TabsTrigger value="colors">Colors</TabsTrigger>}
          </TabsList>

          {tabs.map((tab) => (
            <TabsContent key={tab.value} value={tab.value} className="grid gap-3 sm:grid-cols-2">
              {tab.items.map((item, i) => (
                <RecommendationCard key={`${item.title}-${i}`} item={item} index={i} />
              ))}
            </TabsContent>
          ))}

          {data.colors.length > 0 && (
            <TabsContent value="colors" className="flex flex-wrap gap-2">
              {data.colors.map((color) => (
                <span
                  key={color}
                  className="inline-flex items-center gap-2 rounded-full border border-border bg-card/60 py-1.5 pl-2 pr-3.5 text-sm"
                >
                  <span
                    className="size-5 rounded-full ring-1 ring-inset ring-black/10"
                    style={{ background: colorToCss(color) }}
                  />
                  {humanize(color)}
                </span>
              ))}
            </TabsContent>
          )}
        </Tabs>
      </CardContent>
    </Card>
  );
}
