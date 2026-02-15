from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.currency import CurrencyResponse, HistoricalRatesResponse, LatestRatesResponse
from app.services.currency import CurrencyService

router = APIRouter(prefix="/currencies", tags=["currencies"])


@router.get("", response_model=list[CurrencyResponse])
async def list_currencies(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[CurrencyResponse]:
    service = CurrencyService(session)
    currencies = await service.list_currencies()
    return [CurrencyResponse.model_validate(c) for c in currencies]


@router.get("/rates", response_model=LatestRatesResponse)
async def get_latest_rates(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    base: str | None = Query(default=None),
) -> LatestRatesResponse:
    service = CurrencyService(session)
    base_currency = base or current_user.base_currency
    return await service.get_latest_rates(base_currency)


@router.get("/rates/history", response_model=HistoricalRatesResponse)
async def get_historical_rates(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    from_date: date = Query(...),
    to_date: date = Query(...),
    base: str | None = Query(default=None),
) -> HistoricalRatesResponse:
    service = CurrencyService(session)
    base_currency = base or current_user.base_currency
    return await service.get_historical_rates(base_currency, from_date, to_date)
