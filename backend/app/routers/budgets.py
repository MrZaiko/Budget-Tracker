import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.budget import (
    BudgetCreate,
    BudgetResponse,
    BudgetSummaryResponse,
    BudgetUpdate,
    CollaboratorInvite,
    CollaboratorResponse,
    CollaboratorUpdate,
)
from app.services.budget import BudgetService

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetResponse])
async def list_budgets(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[BudgetResponse]:
    service = BudgetService(session)
    budgets = await service.list_budgets(current_user.id)
    return [BudgetResponse.model_validate(b) for b in budgets]


@router.post("", response_model=BudgetResponse, status_code=201)
async def create_budget(
    data: BudgetCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BudgetResponse:
    service = BudgetService(session)
    budget = await service.create_budget(current_user.id, data)
    return BudgetResponse.model_validate(budget)


@router.get("/{id}", response_model=BudgetResponse)
async def get_budget(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BudgetResponse:
    service = BudgetService(session)
    budget = await service.get_budget(id, current_user.id)
    return BudgetResponse.model_validate(budget)


@router.patch("/{id}", response_model=BudgetResponse)
async def update_budget(
    id: uuid.UUID,
    data: BudgetUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BudgetResponse:
    service = BudgetService(session)
    budget = await service.update_budget(id, current_user.id, data)
    return BudgetResponse.model_validate(budget)


@router.delete("/{id}", status_code=204)
async def delete_budget(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = BudgetService(session)
    await service.delete_budget(id, current_user.id)


@router.get("/{id}/summary", response_model=BudgetSummaryResponse)
async def get_budget_summary(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BudgetSummaryResponse:
    service = BudgetService(session)
    return await service.get_summary(id, current_user.id)


@router.get("/{id}/collaborators", response_model=list[CollaboratorResponse])
async def list_collaborators(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[CollaboratorResponse]:
    service = BudgetService(session)
    collabs = await service.list_collaborators(id, current_user.id)
    return [CollaboratorResponse.model_validate(c) for c in collabs]


@router.post("/{id}/collaborators", response_model=CollaboratorResponse, status_code=201)
async def invite_collaborator(
    id: uuid.UUID,
    data: CollaboratorInvite,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CollaboratorResponse:
    service = BudgetService(session)
    collab = await service.invite_collaborator(id, current_user.id, data)
    return CollaboratorResponse.model_validate(collab)


@router.patch("/{id}/collaborators/{user_id}", response_model=CollaboratorResponse)
async def update_collaborator(
    id: uuid.UUID,
    user_id: uuid.UUID,
    data: CollaboratorUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CollaboratorResponse:
    service = BudgetService(session)
    collab = await service.update_collaborator_role(id, user_id, current_user.id, data)
    return CollaboratorResponse.model_validate(collab)


@router.delete("/{id}/collaborators/{user_id}", status_code=204)
async def remove_collaborator(
    id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = BudgetService(session)
    await service.remove_collaborator(id, user_id, current_user.id)
