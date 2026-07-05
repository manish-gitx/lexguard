from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.auth import AuthUser, get_current_user
from app.persistence.user_documents import get_user_document_store
from app.schemas import UserHistoryResponse

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get(
    "/me/history",
    response_model=UserHistoryResponse,
    summary="List the signed-in user's saved scan and chat history",
)
async def get_my_history(
    user: Annotated[AuthUser, Depends(get_current_user)],
    limit: Annotated[int, Query(ge=1, le=50)] = 25,
) -> UserHistoryResponse:
    items = await get_user_document_store().list_history(user=user, limit=limit)
    return UserHistoryResponse(items=items)
