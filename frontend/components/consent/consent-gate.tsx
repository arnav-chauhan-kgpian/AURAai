"use client";

/**
 * Biometric-consent gate.
 *
 * Face imagery is biometric data, so before AuraAI processes a selfie the
 * signed-in user must grant explicit, revocable consent (GDPR Art. 9). This
 * component checks the backend once per signed-in session and, if consent is
 * missing, presents a one-time modal that records it. In demo/anonymous mode
 * (no Clerk) the backend skips the consent gate, so this renders nothing.
 */
import { ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Dialog } from "@/components/ui/dialog";
import { getConsent, setConsent } from "@/lib/api";
import { getAuthToken } from "@/lib/auth-token";
import { clerkEnabled } from "@/lib/clerk";

const LOCAL_FLAG = "aura:consent-granted";

export function ConsentGate() {
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!clerkEnabled) return;
    if (typeof window !== "undefined" && window.localStorage.getItem(LOCAL_FLAG) === "1") {
      return;
    }
    let cancelled = false;
    (async () => {
      // Only relevant once the user is authenticated (has a Clerk token).
      const token = await getAuthToken();
      if (cancelled || !token) return;
      const granted = await getConsent();
      if (cancelled) return;
      if (granted) {
        window.localStorage.setItem(LOCAL_FLAG, "1");
      } else {
        setOpen(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const accept = async () => {
    setSaving(true);
    const ok = await setConsent(true);
    setSaving(false);
    if (ok && typeof window !== "undefined") {
      window.localStorage.setItem(LOCAL_FLAG, "1");
    }
    setOpen(false);
  };

  return (
    <Dialog open={open} onClose={() => setOpen(false)} label="Consent to face-image processing">
      <div className="p-6 sm:p-8">
        <div className="mb-4 inline-flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
          <ShieldCheck className="size-6" />
        </div>
        <h2 className="text-xl font-semibold">Before we analyze your selfie</h2>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
          Skin analysis and virtual try-on process your facial image, which is biometric data. We
          send it to the analysis provider only to generate your results, never sell or share it,
          and you can delete it any time from <b className="text-foreground">Settings → Privacy</b>.
          We need your consent to continue.
        </p>
        <div className="mt-6 flex flex-col gap-2 sm:flex-row-reverse">
          <Button onClick={accept} disabled={saving} className="sm:min-w-40">
            {saving ? "Saving…" : "I consent"}
          </Button>
          <Button variant="ghost" onClick={() => setOpen(false)} disabled={saving}>
            Not now
          </Button>
        </div>
        <p className="mt-4 text-2xs text-muted-foreground">
          You can still chat for styling advice without a selfie.
        </p>
      </div>
    </Dialog>
  );
}
