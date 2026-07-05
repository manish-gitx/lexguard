from __future__ import annotations

import logging
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any

from app.auth import AuthUser
from app.config import Settings, get_settings
from app.schemas import DocumentScorecard, DomainVerdict, UserHistoryChatMessage, UserHistoryItem

log = logging.getLogger(__name__)


class UserDocumentStore:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._firestore_client: Any = None
        self._storage_client: Any = None
        self._enabled: bool | None = None

    @property
    def enabled(self) -> bool:
        if self._enabled is not None:
            return self._enabled
        if not self._settings.GCP_PROJECT_ID:
            self._enabled = False
            return False
        try:
            from google.cloud import firestore, storage

            self._firestore_client = firestore.AsyncClient(project=self._settings.GCP_PROJECT_ID)
            self._storage_client = storage.Client(project=self._settings.GCP_PROJECT_ID)
            self._enabled = True
        except Exception as exc:
            log.warning("user_document_store_unavailable", extra={"error": str(exc)})
            self._enabled = False
        return self._enabled

    async def upsert_user(self, user: AuthUser) -> None:
        if not self.enabled:
            return
        from google.cloud import firestore

        now = datetime.now(UTC)
        payload = {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.name,
            "photo_url": user.picture,
            "provider": "google.com",
            "last_seen": now,
            "updated_at": now,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        try:
            await self._firestore_client.collection("users").document(user.uid).set(
                payload,
                merge=True,
            )
        except Exception as exc:
            log.warning("user_upsert_failed", extra={"uid": user.uid, "error": str(exc)})

    async def save_scan_metadata(
        self,
        *,
        user: AuthUser,
        scorecard: DocumentScorecard,
        source_kind: str,
        selected_domain: str,
        filename: str | None = None,
        content_type: str | None = None,
        size_bytes: int | None = None,
        gcs_path: str | None = None,
    ) -> None:
        if not self.enabled:
            return
        await self.upsert_user(user)
        now = datetime.now(UTC)
        verdict: DomainVerdict | None = scorecard.domain_verdict
        payload: dict[str, Any] = {
            "document_id": scorecard.document_id,
            "source_kind": source_kind,
            "selected_domain": selected_domain,
            "domain": scorecard.domain.value,
            "domain_verdict": verdict.model_dump(mode="json") if verdict else None,
            "scorecard": scorecard.model_dump(mode="json"),
            "issuer_name": scorecard.issuer_name,
            "risk_score": scorecard.risk_score,
            "overall_severity": scorecard.overall_severity.value,
            "source_url": str(scorecard.source_url) if scorecard.source_url else None,
            "filename": filename,
            "content_type": content_type,
            "size_bytes": size_bytes,
            "gcs_path": gcs_path,
            "created_at": now,
            "updated_at": now,
        }
        try:
            await (
                self._firestore_client.collection("users")
                .document(user.uid)
                .collection("documents")
                .document(scorecard.document_id)
                .set(payload, merge=True)
            )
        except Exception as exc:
            log.warning(
                "user_document_metadata_save_failed",
                extra={"uid": user.uid, "document_id": scorecard.document_id, "error": str(exc)},
            )

    async def save_pdf(
        self,
        *,
        user: AuthUser,
        scorecard: DocumentScorecard,
        filename: str,
        content_type: str,
        data: bytes,
        selected_domain: str,
    ) -> None:
        if not self.enabled:
            return
        bucket_name = self._settings.user_docs_bucket
        if not bucket_name:
            log.warning("user_document_pdf_skipped_no_bucket")
            return

        object_name = f"users/{user.uid}/documents/{scorecard.document_id}/original.pdf"
        gcs_path = f"gs://{bucket_name}/{object_name}"
        try:
            bucket = self._storage_client.bucket(bucket_name)
            blob = bucket.blob(object_name)
            blob.upload_from_string(data, content_type=content_type or "application/pdf")
        except Exception as exc:
            log.warning(
                "user_document_pdf_save_failed",
                extra={"uid": user.uid, "document_id": scorecard.document_id, "error": str(exc)},
            )
            gcs_path = None

        await self.save_scan_metadata(
            user=user,
            scorecard=scorecard,
            source_kind="pdf",
            selected_domain=selected_domain,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            gcs_path=gcs_path,
        )

    async def save_chat_turns(
        self,
        *,
        user: AuthUser,
        document_id: str,
        question: str,
        answer: str,
    ) -> None:
        if not self.enabled:
            return
        await self.upsert_user(user)
        now = datetime.now(UTC)
        doc_ref = (
            self._firestore_client.collection("users")
            .document(user.uid)
            .collection("documents")
            .document(document_id)
        )
        try:
            batch = self._firestore_client.batch()
            chat_ref = doc_ref.collection("chat_messages")
            batch.set(
                chat_ref.document(),
                {"role": "user", "content": question, "created_at": now},
            )
            batch.set(
                chat_ref.document(),
                {"role": "assistant", "content": answer, "created_at": now},
            )
            batch.set(doc_ref, {"updated_at": now}, merge=True)
            await batch.commit()
        except Exception as exc:
            log.warning(
                "user_document_chat_save_failed",
                extra={"uid": user.uid, "document_id": document_id, "error": str(exc)},
            )

    async def list_history(self, *, user: AuthUser, limit: int = 25) -> list[UserHistoryItem]:
        if not self.enabled:
            return []
        await self.upsert_user(user)
        from google.cloud import firestore

        docs_ref = (
            self._firestore_client.collection("users")
            .document(user.uid)
            .collection("documents")
        )
        query = docs_ref.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
        items: list[UserHistoryItem] = []
        try:
            async for snap in query.stream():
                data = snap.to_dict() or {}
                scorecard_data = data.get("scorecard")
                if not isinstance(scorecard_data, dict):
                    continue
                chat_history = await self._list_chat_history(
                    user=user,
                    document_id=str(data.get("document_id") or snap.id),
                )
                items.append(
                    UserHistoryItem(
                        document_id=str(data.get("document_id") or snap.id),
                        source_kind=str(data.get("source_kind") or "text"),
                        selected_domain=data.get("selected_domain") or scorecard_data.get("domain") or "generic",
                        domain=data.get("domain") or scorecard_data.get("domain") or "generic",
                        issuer_name=data.get("issuer_name"),
                        risk_score=int(data.get("risk_score") or scorecard_data.get("risk_score") or 0),
                        overall_severity=data.get("overall_severity")
                        or scorecard_data.get("overall_severity")
                        or "low",
                        source_url=data.get("source_url"),
                        filename=data.get("filename"),
                        created_at=data.get("created_at"),
                        updated_at=data.get("updated_at"),
                        scorecard=DocumentScorecard(**scorecard_data),
                        chat_history=chat_history,
                    )
                )
        except Exception as exc:
            log.warning("user_history_list_failed", extra={"uid": user.uid, "error": str(exc)})
        return items

    async def _list_chat_history(
        self,
        *,
        user: AuthUser,
        document_id: str,
        limit: int = 50,
    ) -> list[UserHistoryChatMessage]:
        from google.cloud import firestore

        chat_ref = (
            self._firestore_client.collection("users")
            .document(user.uid)
            .collection("documents")
            .document(document_id)
            .collection("chat_messages")
        )
        query = chat_ref.order_by("created_at", direction=firestore.Query.ASCENDING).limit(limit)
        messages: list[UserHistoryChatMessage] = []
        async for snap in query.stream():
            data = snap.to_dict() or {}
            role = data.get("role")
            content = data.get("content")
            if role not in {"user", "assistant"} or not isinstance(content, str):
                continue
            messages.append(
                UserHistoryChatMessage(
                    role=role,
                    content=content,
                    created_at=data.get("created_at"),
                )
            )
        return messages


@lru_cache(maxsize=1)
def get_user_document_store() -> UserDocumentStore:
    return UserDocumentStore(get_settings())
