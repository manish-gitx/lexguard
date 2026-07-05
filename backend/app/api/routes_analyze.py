from __future__ import annotations

import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.deps import SettingsDep
from app.auth import AuthUser, get_optional_user
from app.core.errors import AnalysisError, IngestionError, PayloadTooLargeError
from app.ingestion.html import fetch_and_clean
from app.ingestion.pdf import extract_text_from_pdf
from app.orchestrator import analyze_document
from app.persistence.user_documents import get_user_document_store
from app.schemas import (
    AnalyzeTextRequest,
    AnalyzeUrlRequest,
    DocumentScorecard,
    Domain,
    Language,
)

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analyze", tags=["analysis"])

_ANALYSIS_TIMEOUT_SECONDS = 240.0
_ACCEPTED_PDF_MIME = {"application/pdf", "application/x-pdf"}


async def _run(text: str, domain: Domain, language: Language, source_url: str | None) -> DocumentScorecard:
    try:
        return await asyncio.wait_for(
            analyze_document(
                text=text, domain=domain, language=language, source_url=source_url
            ),
            timeout=_ANALYSIS_TIMEOUT_SECONDS,
        )
    except TimeoutError as exc:
        raise AnalysisError(
            f"Analysis exceeded the {int(_ANALYSIS_TIMEOUT_SECONDS)}-second timeout."
        ) from exc


@router.post("/text", response_model=DocumentScorecard, summary="Analyze raw text")
async def analyze_text(
    req: AnalyzeTextRequest,
    user: Annotated[AuthUser | None, Depends(get_optional_user)],
) -> DocumentScorecard:
    scorecard = await _run(
        text=req.text,
        domain=req.domain_hint,
        language=req.language,
        source_url=str(req.source_url) if req.source_url else None,
    )
    if user:
        await get_user_document_store().save_scan_metadata(
            user=user,
            scorecard=scorecard,
            source_kind="text",
            selected_domain=req.domain_hint.value,
        )
    return scorecard


@router.post("/pdf", response_model=DocumentScorecard, summary="Analyze a PDF upload")
async def analyze_pdf(
    settings: SettingsDep,
    user: Annotated[AuthUser | None, Depends(get_optional_user)],
    file: Annotated[UploadFile, File(description="Digital PDF (scanned not supported in v1).")],
    domain_hint: Annotated[Domain, Form()] = Domain.GENERIC,
    language: Annotated[Language, Form()] = "en",
) -> DocumentScorecard:
    if file.content_type not in _ACCEPTED_PDF_MIME:
        raise IngestionError(
            f"Expected application/pdf, got {file.content_type!r}.",
            details={"received_content_type": file.content_type},
        )

    data = await file.read()
    if len(data) > settings.MAX_DOC_BYTES:
        raise PayloadTooLargeError(
            f"PDF exceeds the {settings.MAX_DOC_BYTES}-byte limit.",
            details={"size": len(data), "limit": settings.MAX_DOC_BYTES},
        )

    text = extract_text_from_pdf(data)
    log.info("pdf_ingested", extra={"chars": len(text), "pdf_filename": file.filename})

    scorecard = await _run(text=text, domain=domain_hint, language=language, source_url=None)
    if user:
        await get_user_document_store().save_pdf(
            user=user,
            scorecard=scorecard,
            filename=file.filename or "document.pdf",
            content_type=file.content_type or "application/pdf",
            data=data,
            selected_domain=domain_hint.value,
        )
    return scorecard


@router.post("/url", response_model=DocumentScorecard, summary="Analyze a public URL")
async def analyze_url(
    req: AnalyzeUrlRequest,
    user: Annotated[AuthUser | None, Depends(get_optional_user)],
) -> DocumentScorecard:
    url = str(req.url)
    text = await fetch_and_clean(url)
    log.info("url_ingested", extra={"chars": len(text), "url": url})
    scorecard = await _run(text=text, domain=req.domain_hint, language=req.language, source_url=url)
    if user:
        await get_user_document_store().save_scan_metadata(
            user=user,
            scorecard=scorecard,
            source_kind="url",
            selected_domain=req.domain_hint.value,
        )
    return scorecard
