from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.reports import (
    IncomeVsExpenseResponse,
    NetWorthResponse,
    SpendingReportResponse,
    TrendsReportResponse,
)
from app.services.reports import ReportsService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/spending", response_model=SpendingReportResponse)
async def spending_report(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    from_date: date = Query(...),
    to_date: date = Query(...),
    currency: str | None = Query(default=None),
) -> SpendingReportResponse:
    service = ReportsService(session)
    return await service.spending_report(
        current_user.id,
        from_date,
        to_date,
        currency or current_user.base_currency,
    )


@router.get("/income-vs-expenses", response_model=IncomeVsExpenseResponse)
async def income_vs_expenses(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    from_date: date = Query(...),
    to_date: date = Query(...),
    currency: str | None = Query(default=None),
) -> IncomeVsExpenseResponse:
    service = ReportsService(session)
    return await service.income_vs_expenses(
        current_user.id,
        from_date,
        to_date,
        currency or current_user.base_currency,
    )


@router.get("/trends", response_model=TrendsReportResponse)
async def trends_report(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    months: int = Query(default=12, ge=1, le=24),
    currency: str | None = Query(default=None),
) -> TrendsReportResponse:
    service = ReportsService(session)
    return await service.trends_report(
        current_user.id,
        months,
        currency or current_user.base_currency,
    )


@router.get("/net-worth", response_model=NetWorthResponse)
async def net_worth(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    currency: str | None = Query(default=None),
) -> NetWorthResponse:
    service = ReportsService(session)
    return await service.net_worth(
        current_user.id,
        currency or current_user.base_currency,
    )
