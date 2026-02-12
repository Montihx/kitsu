"use client";

import Link from "next/link";
import { useEffect } from "react";

import { ROUTES } from "@/constants/routes";
import { Button } from "@/components/ui/button";

export default function ProfileError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3 px-4 text-center">
      <h2 className="text-2xl font-semibold">Profile is unavailable</h2>
      <p className="text-sm text-slate-300">
        We could not load this profile right now. Please try again or return to
        the homepage.
      </p>
      <div className="flex gap-3">
        <Button onClick={reset}>Try again</Button>
        <Button variant="secondary" asChild>
          <Link href={ROUTES.HOME}>Go home</Link>
        </Button>
      </div>
    </div>
  );
}
