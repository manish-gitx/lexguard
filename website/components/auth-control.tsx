"use client";

import { useState } from "react";
import { useAuth } from "@/components/auth-provider";

export function AuthControl() {
  const { user, loading, configured, signIn, signOut } = useAuth();
  const [busy, setBusy] = useState(false);

  async function run(action: () => Promise<void>) {
    setBusy(true);
    try {
      await action();
    } finally {
      setBusy(false);
    }
  }

  if (!configured) {
    return (
      <span className="label text-accent">
        auth env missing
      </span>
    );
  }

  if (loading) {
    return <span className="label">checking login</span>;
  }

  if (!user) {
    return (
      <button
        type="button"
        onClick={() => run(signIn)}
        disabled={busy}
        className="label border border-rule px-3 py-1.5 hover:border-accent hover:text-ink transition-colors disabled:text-ink-faint"
      >
        {busy ? "opening google" : "sign in"}
      </button>
    );
  }

  return (
    <span className="inline-flex items-center gap-3">
      {user.photoURL && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={user.photoURL}
          alt=""
          className="h-6 w-6 rounded-full border border-rule"
          referrerPolicy="no-referrer"
        />
      )}
      <span className="label max-w-[12rem] truncate text-ink-mid">
        {user.displayName || user.email || "signed in"}
      </span>
      <button
        type="button"
        onClick={() => run(signOut)}
        disabled={busy}
        className="label text-ink-low hover:text-accent transition-colors disabled:text-ink-faint"
      >
        sign out
      </button>
    </span>
  );
}
