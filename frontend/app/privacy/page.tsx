import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy & Data Use — AuraAI",
  description:
    "How AuraAI collects, processes, stores, and deletes your data — including biometric (facial) data used for skin analysis and virtual try-on.",
};

/** A plain-language privacy policy that reflects the app's actual data flows. */
export default function PrivacyPage() {
  return (
    <article className="mx-auto max-w-2xl px-4 py-12 sm:py-16">
      <h1 className="text-3xl font-semibold tracking-tight">Privacy & Data Use</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        This describes what AuraAI does with your data. It reflects how the product actually
        works, not a generic template.
      </p>

      <div className="prose-aura mt-8 space-y-8">
        <Section title="What we collect">
          <ul>
            <li>
              <b>Face images</b> you upload for skin analysis or virtual try-on. These are{" "}
              <b>biometric data</b> and are only processed with your explicit consent.
            </li>
            <li>
              <b>Garment images</b> you upload for virtual try-on.
            </li>
            <li>
              <b>Messages and results</b> from your conversations (skin scores, recommendations,
              try-on outputs) so we can show your history and progress.
            </li>
            <li>
              <b>Account identity</b> (from our authentication provider, Clerk) — a user id and
              email.
            </li>
          </ul>
        </Section>

        <Section title="How your face image is used">
          <p>
            When you run a skin analysis or try-on, your image is sent to our analysis provider
            (Perfect Corp / YouCam) solely to generate your results. We do not use your images to
            train models, and we never sell or share them for advertising. Skin masks (heatmaps)
            are generated from your image and shown back to you.
          </p>
        </Section>

        <Section title="Where it's stored & for how long">
          <p>
            Uploaded images are stored in access-controlled object storage and served only to you
            through short-lived signed links. Structured results are stored in our database, scoped
            to your account. Images are automatically purged after our retention window; you can
            delete everything sooner at any time.
          </p>
        </Section>

        <Section title="Your controls">
          <ul>
            <li>
              <b>Consent</b> is required before any face processing and can be withdrawn at any
              time.
            </li>
            <li>
              <b>Delete your images</b> or <b>erase your entire account</b> (GDPR right to erasure)
              from <Link href="/settings" className="text-primary underline">Settings</Link>.
            </li>
            <li>
              You can use AuraAI for text-only styling advice without ever uploading a photo.
            </li>
          </ul>
        </Section>

        <Section title="Legal basis">
          <p>
            We process biometric data under your explicit consent (GDPR Art. 9(2)(a)). All other
            processing is to provide the service you requested. You may lodge a complaint with your
            local data-protection authority.
          </p>
        </Section>

        <p className="text-sm text-muted-foreground">
          Questions? Contact the project maintainer. This is a personal/educational project and not
          a commercial service.
        </p>
      </div>
    </article>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-2">
      <h2 className="text-lg font-semibold">{title}</h2>
      <div className="space-y-2 text-sm leading-relaxed text-muted-foreground [&_b]:text-foreground [&_li]:ml-4 [&_li]:list-disc [&_ul]:space-y-1.5">
        {children}
      </div>
    </section>
  );
}
