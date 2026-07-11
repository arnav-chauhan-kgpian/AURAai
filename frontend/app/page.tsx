import { CtaSection } from "@/components/landing/cta-section";
import { FeatureCards } from "@/components/landing/feature-cards";
import { Hero } from "@/components/landing/hero";
import { SiteFooter } from "@/components/layout/site-footer";

export default function LandingPage() {
  return (
    <>
      <Hero />
      <FeatureCards />
      <CtaSection />
      <SiteFooter />
    </>
  );
}
