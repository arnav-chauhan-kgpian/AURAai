"use client";

import { useQuery } from "@tanstack/react-query";
import { Check, Monitor, Moon, PlayCircle, Plug, RefreshCw, Sparkles, Sun, Trash2 } from "lucide-react";
import { useEffect } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { useMounted } from "@/hooks/use-mounted";
import { checkHealth } from "@/lib/api";
import { DEMO_USERS } from "@/lib/demo-users";
import { useDemoStore } from "@/lib/demo-store";
import { env } from "@/lib/env";
import { useOnboardingStore } from "@/lib/onboarding-store";
import { useSessionStore } from "@/lib/store";
import { useThemeStore, type Theme } from "@/lib/theme-store";
import { cn } from "@/lib/utils";

export function SettingsView() {
  const mounted = useMounted();
  const theme = useThemeStore((s) => s.theme);
  const setTheme = useThemeStore((s) => s.setTheme);
  const sessionId = useSessionStore((s) => s.sessionId);
  const newSession = useSessionStore((s) => s.newSession);
  const clearConversation = useSessionStore((s) => s.clearConversation);

  const demo = useDemoStore();
  const reopenOnboarding = useOnboardingStore((s) => s.reopen);
  useEffect(() => demo.hydrate(), []); // eslint-disable-line react-hooks/exhaustive-deps

  const health = useQuery({
    queryKey: ["health"],
    queryFn: checkHealth,
    refetchInterval: 30_000,
  });

  const connected = env.useMock || health.data === true;
  const statusLabel = env.useMock ? "Demo mode" : connected ? "Connected" : "Offline";

  return (
    <div className="container max-w-2xl py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Personalise appearance and manage your session.
        </p>
      </div>

      <div className="space-y-5">
        <Card>
          <CardHeader className="flex-row items-center gap-2 space-y-0">
            <Monitor className="size-4 text-primary" />
            <CardTitle>Appearance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Theme</p>
                <p className="text-xs text-muted-foreground">Dark is the default.</p>
              </div>
              <div className="inline-flex rounded-full bg-muted/70 p-1">
                {(["light", "dark"] as Theme[]).map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setTheme(option)}
                    aria-pressed={mounted && theme === option}
                    className={cn(
                      "inline-flex items-center gap-1.5 rounded-full px-4 py-1.5 text-sm font-medium capitalize transition-all focus-visible:ring-focus",
                      mounted && theme === option
                        ? "bg-card text-foreground shadow-sm"
                        : "text-muted-foreground",
                    )}
                  >
                    {option === "light" ? <Sun className="size-3.5" /> : <Moon className="size-3.5" />}
                    {option}
                  </button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-center gap-2 space-y-0">
            <Sparkles className="size-4 text-primary" />
            <CardTitle>Demo Mode</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-medium">Use curated demo data</p>
                <p className="text-xs text-muted-foreground">
                  Runs the full experience offline — no backend or API keys needed.
                </p>
              </div>
              <Switch
                checked={mounted ? demo.enabled : false}
                onCheckedChange={demo.setEnabled}
                aria-label="Toggle demo mode"
              />
            </div>
            {mounted && demo.enabled && (
              <>
                <Separator />
                <p className="text-xs font-medium text-muted-foreground">Demo persona</p>
                <div className="grid gap-2 sm:grid-cols-3">
                  {DEMO_USERS.map((user) => (
                    <button
                      key={user.id}
                      type="button"
                      onClick={() => demo.setUser(user.id)}
                      aria-pressed={demo.userId === user.id}
                      className={cn(
                        "rounded-xl border p-3 text-left transition-all focus-visible:ring-focus",
                        demo.userId === user.id
                          ? "border-primary/50 bg-primary/5"
                          : "border-border hover:border-primary/30",
                      )}
                    >
                      <span className="text-sm font-medium">{user.name}</span>
                      <span className="mt-0.5 block text-2xs leading-tight text-muted-foreground">
                        {user.tagline}
                      </span>
                    </button>
                  ))}
                </div>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-center gap-2 space-y-0">
            <Plug className="size-4 text-primary" />
            <CardTitle>Connection</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Row label="Status">
              <span className="inline-flex items-center gap-2 text-sm">
                <span
                  className={cn(
                    "size-2 rounded-full",
                    connected ? "bg-success" : "bg-destructive",
                    !env.useMock && health.isFetching && "animate-pulse",
                  )}
                />
                {statusLabel}
              </span>
            </Row>
            <Separator />
            <Row label="Backend">
              <code className="max-w-[16rem] truncate rounded-md bg-muted px-2 py-1 text-xs">
                {env.apiBaseUrl}
              </code>
            </Row>
            <Button
              variant="outline"
              size="sm"
              onClick={() => health.refetch()}
              disabled={env.useMock}
              className="w-fit"
            >
              <RefreshCw className={cn("size-4", health.isFetching && "animate-spin")} />
              Test connection
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-center gap-2 space-y-0">
            <Check className="size-4 text-primary" />
            <CardTitle>Session</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Row label="Session ID">
              <code className="rounded-md bg-muted px-2 py-1 text-xs">{sessionId}</code>
            </Row>
            <Separator />
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" size="sm" onClick={newSession}>
                <RefreshCw className="size-4" /> New session
              </Button>
              <Button variant="outline" size="sm" onClick={clearConversation}>
                <Trash2 className="size-4" /> Clear conversation
              </Button>
              <Button variant="outline" size="sm" onClick={reopenOnboarding}>
                <PlayCircle className="size-4" /> Replay walkthrough
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-sm text-muted-foreground">{label}</span>
      {children}
    </div>
  );
}
