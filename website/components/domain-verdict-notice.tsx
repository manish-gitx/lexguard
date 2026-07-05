import type { DocumentScorecard } from "@/lib/types";

const LABELS: Record<string, string> = {
  employment: "Employment",
  privacy: "Privacy",
  ticketing: "Ticketing",
  consumer: "Consumer",
  rental: "Rental",
  generic: "Generic",
};

export function DomainVerdictNotice({
  scorecard,
  compact = false,
}: {
  scorecard: DocumentScorecard;
  compact?: boolean;
}) {
  const verdict = scorecard.domain_verdict;
  if (!verdict) return null;

  const selected = LABELS[verdict.selected_domain] ?? verdict.selected_domain;
  const inferred = LABELS[verdict.inferred_domain] ?? verdict.inferred_domain;
  const isGuidance =
    verdict.selected_domain === "generic" && verdict.inferred_domain !== "generic";
  const shouldShow = isGuidance || !verdict.matches_selection;
  if (!shouldShow) return null;

  return (
    <div className={`border border-accent/40 bg-accent-soft px-5 py-4 ${compact ? "mb-5" : "mb-10"}`}>
      <p className="label text-accent mb-2">
        {isGuidance ? "domain detected" : "domain mismatch"}
      </p>
      <p className="text-ink-mid text-sm leading-relaxed">
        You selected <span className="text-ink">{selected}</span>, but LexGuard
        thinks this reads more like{" "}
        <span className="text-ink">{inferred}</span>
        {verdict.confidence ? ` (${Math.round(verdict.confidence * 100)}% confidence)` : ""}.
        {verdict.reason ? ` ${verdict.reason}` : ""}
      </p>
      {verdict.evidence.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {verdict.evidence.map((item) => (
            <span
              key={item}
              className="label-wide border border-rule bg-bg/50 px-2 py-1 text-ink-low"
            >
              {item}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
