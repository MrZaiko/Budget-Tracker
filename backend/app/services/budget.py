import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget, BudgetCategory, BudgetCollaborator
from app.repositories.budget import BudgetRepository
from app.repositories.user import UserRepository
from app.schemas.budget import (
    BudgetCreate,
    BudgetSummaryCategory,
    BudgetSummaryResponse,
    BudgetUpdate,
    CollaboratorInvite,
    CollaboratorUpdate,
)


class BudgetService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = BudgetRepository(session)
        self.user_repo = UserRepository(session)

    async def list_budgets(self, user_id: uuid.UUID) -> list[Budget]:
        return await self.repo.get_accessible(user_id)

    async def _require_access(self, budget_id: uuid.UUID, user_id: uuid.UUID) -> Budget:
        budget = await self.repo.get_by_id_with_categories(budget_id)
        if not budget:
            raise HTTPException(
                status_code=404, detail={"detail": "Budget not found", "code": "not_found"}
            )
        if budget.owner_id == user_id:
            return budget
        collab = await self.repo.get_collaborator(budget_id, user_id)
        if not collab or collab.accepted_at is None:
            raise HTTPException(
                status_code=403, detail={"detail": "Access denied", "code": "budget_access_denied"}
            )
        return budget

    async def _require_owner(self, budget_id: uuid.UUID, user_id: uuid.UUID) -> Budget:
        budget = await self._require_access(budget_id, user_id)
        if budget.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail={
                    "detail": "Only the budget owner can perform this action",
                    "code": "budget_role_insufficient",
                },
            )
        return budget

    async def get_budget(self, budget_id: uuid.UUID, user_id: uuid.UUID) -> Budget:
        return await self._require_access(budget_id, user_id)

    async def create_budget(self, user_id: uuid.UUID, data: BudgetCreate) -> Budget:
        budget = await self.repo.create(
            owner_id=user_id,
            name=data.name,
            period_type=data.period_type,
            start_date=data.start_date,
            end_date=data.end_date,
            currency=data.currency,
        )
        for bc in data.budget_categories:
            cat = BudgetCategory(
                budget_id=budget.id,
                category_id=bc.category_id,
                limit_amount=bc.limit_amount,
            )
            self.repo.session.add(cat)
        await self.repo.session.flush()
        # Reload with eager-loaded relationships to avoid lazy-load errors
        loaded = await self.repo.get_by_id_with_categories(budget.id)
        return loaded or budget

    async def update_budget(
        self, budget_id: uuid.UUID, user_id: uuid.UUID, data: BudgetUpdate
    ) -> Budget:
        budget = await self._require_owner(budget_id, user_id)
        kwargs = data.model_dump(exclude_none=True)
        if not kwargs:
            return budget
        updated = await self.repo.update(budget, **kwargs)
        loaded = await self.repo.get_by_id_with_categories(updated.id)
        return loaded or updated

    async def delete_budget(self, budget_id: uuid.UUID, user_id: uuid.UUID) -> None:
        budget = await self._require_owner(budget_id, user_id)
        await self.repo.delete(budget)

    async def get_summary(
        self, budget_id: uuid.UUID, user_id: uuid.UUID
    ) -> BudgetSummaryResponse:
        budget = await self._require_access(budget_id, user_id)
        spending = await self.repo.get_spending_by_category(budget_id, budget_currency=budget.currency)

        categories = []
        total_limit = Decimal("0")
        total_spent = Decimal("0")

        for bc in budget.budget_categories:
            spent = spending.get(bc.category_id, Decimal("0"))
            limit = Decimal(str(bc.limit_amount))
            remaining = limit - spent
            categories.append(
                BudgetSummaryCategory(
                    category_id=bc.category_id,
                    category_name=bc.category.name if bc.category else "Unknown",
                    limit_amount=limit,
                    spent_amount=spent,
                    remaining=remaining,
                )
            )
            total_limit += limit
            total_spent += spent

        return BudgetSummaryResponse(
            budget_id=budget.id,
            budget_name=budget.name,
            period_type=budget.period_type,
            start_date=budget.start_date,
            end_date=budget.end_date,
            currency=budget.currency,
            categories=categories,
            total_limit=total_limit,
            total_spent=total_spent,
            total_remaining=total_limit - total_spent,
        )

    async def invite_collaborator(
        self, budget_id: uuid.UUID, user_id: uuid.UUID, data: CollaboratorInvite
    ) -> BudgetCollaborator:
        await self._require_owner(budget_id, user_id)
        invitee = await self.user_repo.get_by_email(data.email)
        if not invitee:
            raise HTTPException(
                status_code=404,
                detail={"detail": "User with that email not found", "code": "user_not_found"},
            )
        existing = await self.repo.get_collaborator(budget_id, invitee.id)
        if existing:
            raise HTTPException(
                status_code=409,
                detail={"detail": "User is already a collaborator", "code": "already_collaborator"},
            )
        collab = BudgetCollaborator(
            budget_id=budget_id,
            user_id=invitee.id,
            role=data.role,
            accepted_at=datetime.now(timezone.utc),  # Auto-accept for simplicity
        )
        self.repo.session.add(collab)
        await self.repo.session.flush()
        await self.repo.session.refresh(collab)
        return collab

    async def update_collaborator_role(
        self,
        budget_id: uuid.UUID,
        collab_user_id: uuid.UUID,
        user_id: uuid.UUID,
        data: CollaboratorUpdate,
    ) -> BudgetCollaborator:
        await self._require_owner(budget_id, user_id)
        collab = await self.repo.get_collaborator(budget_id, collab_user_id)
        if not collab:
            raise HTTPException(
                status_code=404,
                detail={"detail": "Collaborator not found", "code": "not_found"},
            )
        collab.role = data.role
        self.repo.session.add(collab)
        await self.repo.session.flush()
        await self.repo.session.refresh(collab)
        return collab

    async def remove_collaborator(
        self,
        budget_id: uuid.UUID,
        collab_user_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        await self._require_owner(budget_id, user_id)
        collab = await self.repo.get_collaborator(budget_id, collab_user_id)
        if not collab:
            raise HTTPException(
                status_code=404,
                detail={"detail": "Collaborator not found", "code": "not_found"},
            )
        await self.repo.session.delete(collab)
        await self.repo.session.flush()

    async def list_collaborators(
        self, budget_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[BudgetCollaborator]:
        await self._require_access(budget_id, user_id)
        return await self.repo.list_collaborators(budget_id)
