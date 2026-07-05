"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { AuthControl } from "@/components/auth-control";
import { useAuth } from "@/components/auth-provider";
import { ChatPanel } from "@/components/chat-panel";
import { Checklist } from "@/components/checklist";
import { ClauseCard } from "@/components/clause-card";
import { ScorecardHero } from "@/components/scorecard-hero";
import { ScrollReveal } from "@/components/scroll-reveal";
import { StatusPulse } from "@/components/status-pulse";
import { StatuteDrawer } from "@/components/statute-drawer";
import { LexGuardApiError, getUserHistory } from "@/lib/api";
import type { ChatTurn, DocumentScorecard, UserHistoryItem } from "@/lib/types";

export default function HistoryPage() {
  const { user, loading, getIdToken, signIn } = useAuth();
  const [items, setItems] = useState<UserHistoryItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openStatute, setOpenStatute] = useState<string | null>(null);

  useEffect(() => {
    if (loading || !user) return;
    let cancelled = false;
    async function load() {
      setFetching(true);
      setError(null);
      try {
        const token = await getIdToken();
        if (!token) throw new Error("Sign in again to load your history.");
        const nextItems = await getUserHistory(token);
        if (cancelled) return;
        setItems(nextItems);
        setSelectedId((current) => current ?? nextItems[0]?.document_id ?? null);
      } catch (e) {
        if (cancelled) return;
        setError(e instanceof LexGuardApiError ? e.message : (e as Error).message);
      } finally {
        if (!cancelled) setFetching(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [getIdToken, loading, user]);

  const selected = useMemo(
    () => items.find((item) => item.document_id === selectedId) ?? null,
    [items, selectedId],
  );

  return (
    <>
      <Header />

      <main className="px-6 md:px-12 lg:px-16 max-w-6xl mx-auto pb-32">
        <section className="pt-16 md:pt-20">
          <p className="label mb-6">your history</p>
          <h1 className="display max-w-4xl text-[clamp(2rem,5vw,3.6rem)] text-ink leading-[1.05]">
            Every signed-in scan,
            <br />
            with its <span className="display-italic">follow-up chat</span>.
          </h1>
        </section>

        {!loading && !user && (
          <section className="mt-14 border-l-2 border-accent pl-6 py-8">
            <p className="label text-accent mb-4">sign in required</p>
            <p className="text-ink-mid max-w-2xl leading-relaxed">
              History is tied to your Google account. Sign in to see saved scans,
              uploaded PDFs, URL checks, and the chat turns attached to them.
            </p>
            <button
              type="button"
              onClick={signIn}
              className="mt-6 px-5 py-3 bg-accent text-bg"
            >
              <span className="label text-bg">sign in with google</span>
            </button>
          </section>
        )}

        {user && (
          <div className="mt-14 grid gap-10 lg:grid-cols-[19rem_1fr] items-start">
            <aside className="border-t border-rule">
              <div className="py-4 flex items-baseline gap-3">
                <span className="label">saved scans</span>
                <span className="h-px flex-1 bg-rule" />
                <span className="label">{items.length}</span>
              </div>

              {fetching && <p className="text-sm text-ink-low py-8">Loading history...</p>}
              {error && <p className="text-sm text-accent py-8">{error}</p>}
              {!fetching && !error && items.length === 0 && (
                <div className="py-8">
                  <p className="text-sm text-ink-mid leading-relaxed">
                    No saved scans yet. Run a scan while signed in and it will
                    appear here.
                  </p>
                  <Link
                    href="/scan"
                    className="inline-block mt-5 label text-accent hover:text-ink transition-colors"
                  >
                    start a scan
                  </Link>
                </div>
              )}

              <div className="grid gap-px bg-rule">
                {items.map((item) => (
                  <HistoryButton
                    key={item.document_id}
                    item={item}
                    active={item.document_id === selectedId}
                    onClick={() => setSelectedId(item.document_id)}
                  />
                ))}
              </div>
            </aside>

            {selected && (
              <HistoryDetail
                item={selected}
                onStatuteClick={setOpenStatute}
              />
            )}
          </div>
        )}
      </main>

      <Footer />
      <StatuteDrawer
        statuteId={openStatute}
        onClose={() => setOpenStatute(null)}
      />
    </>
  );
}

function HistoryButton({
  item,
  active,
  onClick,
}: {
  item: UserHistoryItem;
  active: boolean;
  onClick: () => void;
}) {
  const title = item.issuer_name || item.filename || item.source_url || item.document_id;
  return (
    <button
      type="button"
      onClick={onClick}
      className={`bg-bg text-left px-4 py-4 border-l-2 transition-colors ${
        active ? "border-accent" : "border-transparent hover:border-rule-strong"
      }`}
    >
      <span className="label">{formatDate(item.created_at)}</span>
      <p className="mt-2 text-sm text-ink leading-snug line-clamp-2">{title}</p>
      <p className="mt-3 text-xs text-ink-low">
        {item.source_kind} · {item.domain} · risk {item.risk_score}
      </p>
    </button>
  );
}

function HistoryDetail({
  item,
  onStatuteClick,
}: {
  item: UserHistoryItem;
  onStatuteClick: (id: string) => void;
}) {
  const scorecard: DocumentScorecard = item.scorecard;
  const initialMessages: ChatTurn[] = item.chat_history.map((turn) => ({
    role: turn.role,
    content: turn.content,
  }));

  return (
    <section className="min-w-0">
      <ScrollReveal>
        <ScorecardHero scorecard={scorecard} />
      </ScrollReveal>

      <ScrollReveal className="mt-10">
        <ChatPanel
          key={`${scorecard.document_id}-${initialMessages.length}`}
          documentId={scorecard.document_id}
          suggestedQuestions={scorecard.suggested_questions}
          initialMessages={initialMessages}
          language="en"
        />
      </ScrollReveal>

      <ScrollReveal className="mt-10">
        <Checklist items={scorecard.pre_sign_checklist} />
      </ScrollReveal>

      <ScrollReveal className="mt-12">
        <div className="flex items-baseline gap-3 mb-2">
          <span className="label">clause-by-clause</span>
          <span className="h-px flex-1 bg-rule" />
          <span className="label">{scorecard.clauses.length} findings</span>
        </div>
        <div>
          {scorecard.clauses.map((c, i) => (
            <ClauseCard
              key={c.clause_id}
              clause={c}
              index={i}
              onStatuteClick={onStatuteClick}
            />
          ))}
        </div>
      </ScrollReveal>
    </section>
  );
}

function Header() {
  return (
    <header className="relative z-10 px-6 md:px-12 lg:px-16 max-w-6xl mx-auto pt-8 flex items-center justify-between flex-wrap gap-y-3">
      <Link href="/" className="flex items-baseline gap-3">
        <span className="display-italic text-2xl">Lex</span>
        <span className="display text-2xl">Guard</span>
      </Link>
      <nav className="flex items-center gap-1 border border-rule rounded-full p-1">
        <NavPill href="/" label="Home" active={false} />
        <NavPill href="/scan" label="Scan" active={false} />
        <NavPill href="/compare" label="Compare" active={false} />
        <NavPill href="/history" label="History" active />
      </nav>
      <div className="flex items-center gap-4">
        <StatusPulse label="Cloud Run / asia-south1" />
        <AuthControl />
      </div>
    </header>
  );
}

function NavPill({
  href,
  label,
  active,
}: {
  href: string;
  label: string;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      className={`relative px-4 py-1.5 rounded-full transition-colors ${
        active ? "bg-surface" : ""
      }`}
    >
      <span
        className={`label ${
          active ? "text-ink" : "text-ink-low hover:text-ink-mid transition-colors"
        }`}
      >
        {label}
      </span>
      {active && (
        <span className="absolute inset-x-3 -bottom-px h-px bg-accent" aria-hidden />
      )}
    </Link>
  );
}

function Footer() {
  return (
    <footer className="px-6 md:px-12 lg:px-16 max-w-6xl mx-auto pb-12">
      <div className="border-t border-rule pt-8 flex flex-wrap gap-y-3 gap-x-8 items-baseline">
        <span className="label">privacy</span>
        <p className="text-ink-mid text-sm max-w-2xl leading-relaxed">
          History is scoped to the signed-in Firebase user. Uploaded PDFs are
          stored in your project bucket; scorecards and chat turns are stored in
          Firestore.
        </p>
      </div>
    </footer>
  );
}

function formatDate(value: string | null) {
  if (!value) return "saved scan";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "saved scan";
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}
