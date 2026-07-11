"use client";

import { SignUp } from "@clerk/nextjs";
import Link from "next/link";

import { buttonVariants } from "@/components/ui/button-variants";
import { clerkEnabled } from "@/lib/clerk";
import { cn } from "@/lib/utils";

export default function SignUpPage() {
  return (
    <div className="grid min-h-[calc(100vh-4rem)] place-items-center p-6">
      {clerkEnabled ? (
        <SignUp />
      ) : (
        <div className="max-w-sm text-center">
          <h1 className="text-xl font-semibold tracking-tight">Sign-up is not configured</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Set your Clerk keys to enable accounts. You can explore AuraAI in Demo Mode meanwhile.
          </p>
          <Link href="/dashboard" className={cn(buttonVariants(), "mt-6")}>
            Continue in Demo Mode
          </Link>
        </div>
      )}
    </div>
  );
}
