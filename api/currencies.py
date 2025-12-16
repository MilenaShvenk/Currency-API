from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from db.database import get_db
from models.currency import (Currency, CurrencyCreate, CurrencyUpdate, CurrencyRead, to_read_model)
from ws.ws_manager import ws_manager

router = APIRouter()


@router.get("/currencies", response_model=List[CurrencyRead])
async def get_currencies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Currency))
    items = result.scalars().all()
    return [to_read_model(i) for i in items]


@router.get("/currencies/{currency_id}", response_model=CurrencyRead)
async def get_currency(currency_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(Currency, currency_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Currency not found")
    return to_read_model(obj)


@router.post("/currencies", response_model=CurrencyRead, status_code=201)
async def create_currency(data: CurrencyCreate, db: AsyncSession = Depends(get_db)):
    obj = Currency(currency=data.currency, rate=data.rate)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    await ws_manager.broadcast({
        "event": "currency_created",
        "currency": to_read_model(obj).dict()
    })

    return to_read_model(obj)


@router.patch("/currencies/{currency_id}", response_model=CurrencyRead)
async def update_currency(currency_id: int, patch: CurrencyUpdate, db: AsyncSession = Depends(get_db)):
    obj = await db.get(Currency, currency_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Currency not found")

    if patch.currency is not None:
        obj.currency = patch.currency
    if patch.rate is not None:
        obj.rate = patch.rate

    await db.commit()
    await db.refresh(obj)

    await ws_manager.broadcast({
        "event": "currency_updated",
        "currency": to_read_model(obj).dict()
    })

    return to_read_model(obj)


@router.delete("/currencies/{currency_id}", status_code=204)
async def delete_currency(currency_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(Currency, currency_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Currency not found")

    await db.delete(obj)
    await db.commit()

    await ws_manager.broadcast({
        "event": "currency_deleted",
        "id": currency_id
    })
