"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { cn } from "@/lib/utils";

/** Markdown renderer for assistant replies: styled prose, code blocks, images, links. */
export function Markdown({ children, className }: { children: string; className?: string }) {
  return (
    <div
      className={cn(
        "space-y-3 text-sm leading-relaxed [&_p]:leading-relaxed",
        "[&_strong]:font-semibold [&_strong]:text-foreground",
        "[&_ul]:ml-1 [&_ul]:space-y-1.5 [&_ol]:ml-1 [&_ol]:space-y-1.5",
        "[&_li]:relative [&_li]:pl-5 [&_li]:before:absolute [&_li]:before:left-0 [&_li]:before:text-primary [&_ul>li]:before:content-['•']",
        "[&_h1]:text-lg [&_h1]:font-semibold [&_h2]:text-base [&_h2]:font-semibold [&_h3]:font-semibold",
        className,
      )}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ node, ...props }) => (
            <a
              {...props}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-primary underline underline-offset-2 hover:opacity-80"
            />
          ),
          img: ({ node, ...props }) => (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              {...props}
              alt={props.alt ?? ""}
              className="my-2 max-h-80 w-full rounded-xl border border-border object-cover"
            />
          ),
          code: ({ node, className: cls, children, ...props }) => {
            const isBlock = /language-/.test(cls ?? "");
            if (!isBlock) {
              return (
                <code
                  className="rounded-md bg-muted px-1.5 py-0.5 font-mono text-[0.8em] text-foreground"
                  {...props}
                >
                  {children}
                </code>
              );
            }
            return (
              <code className={cn("font-mono text-[0.8em]", cls)} {...props}>
                {children}
              </code>
            );
          },
          pre: ({ node, children, ...props }) => (
            <pre
              className="overflow-x-auto rounded-xl border border-border bg-[hsl(240_10%_6%)] p-4 text-slate-100"
              {...props}
            >
              {children}
            </pre>
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
