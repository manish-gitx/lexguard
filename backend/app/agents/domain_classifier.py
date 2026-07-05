from __future__ import annotations

from typing import ClassVar

from app.agents.base import BaseAgent
from app.schemas import Domain, DomainVerdict

_SYSTEM = """You are the Domain Classifier for LexGuard.

Your job is to read the whole document and decide which single LexGuard domain best fits it:
employment, privacy, ticketing, consumer, rental, generic.

Use these meanings:
- employment: offer letters, employment agreements, internships, contractor work terms, HR policies.
- privacy: privacy policies, data processing notices, consent/data-sharing terms.
- ticketing: event, movie, travel, booking, entry, cancellation, or rescheduling terms.
- consumer: product/service terms, ecommerce, subscriptions, refunds, warranty, app/platform terms.
- rental: residential/commercial lease, deposit, maintenance, lock-in, tenancy terms.
- generic: mixed or unclear legal text where no domain is clearly dominant.

Return strict JSON:
{
  "inferred_domain": "employment|privacy|ticketing|consumer|rental|generic",
  "confidence": 0.0-1.0,
  "reason": "one short sentence",
  "evidence": ["2-4 short phrases from the document that support the inference"]
}"""


class DomainClassifierAgent(BaseAgent):
    name: ClassVar[str] = "domain_classifier"
    system_prompt: ClassVar[str] = _SYSTEM

    async def run(self, *, text: str, selected_domain: Domain) -> DomainVerdict:
        excerpt = text[:12000]
        raw = await self._call(
            (
                f"User selected domain: {selected_domain.value}\n\n"
                "Document text:\n"
                "-----\n"
                f"{excerpt}\n"
                "-----\n\n"
                "Return the strict JSON object only."
            ),
            temperature=0.0,
            max_output_tokens=1024,
        )

        inferred_raw = raw.get("inferred_domain")
        try:
            inferred = Domain(inferred_raw)
        except Exception:
            inferred = Domain.GENERIC

        confidence = raw.get("confidence", 0.5)
        if not isinstance(confidence, int | float):
            confidence = 0.5

        reason = raw.get("reason")
        if not isinstance(reason, str):
            reason = ""

        evidence_raw = raw.get("evidence", [])
        evidence = [str(item).strip() for item in evidence_raw if str(item).strip()][:4]

        matches = selected_domain == Domain.GENERIC or inferred == selected_domain
        return DomainVerdict(
            selected_domain=selected_domain,
            inferred_domain=inferred,
            matches_selection=matches,
            confidence=float(max(0.0, min(1.0, confidence))),
            reason=reason.strip(),
            evidence=evidence,
        )
