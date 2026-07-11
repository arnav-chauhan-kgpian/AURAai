"use client";

import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";

import { buttonVariants } from "@/components/ui/button-variants";
import { clerkEnabled } from "@/lib/clerk";
import { cn } from "@/lib/utils";

/** Header auth controls. Renders nothing unless Clerk is configured. */
export function AuthControls() {
  if (!clerkEnabled) return null;
  return (
    <>
      <SignedOut>
        <SignInButton mode="modal">
          <button type="button" className={cn(buttonVariants({ variant: "outline", size: "sm" }))}>
            Sign in
          </button>
        </SignInButton>
      </SignedOut>
      <SignedIn>
        <UserButton
          appearance={{ elements: { avatarBox: "h-9 w-9" } }}
          afterSignOutUrl="/"
        />
      </SignedIn>
    </>
  );
}
