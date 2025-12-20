import asyncio
import json
from datetime import datetime
from sqlmodel import select

from db.database import DBSession
from models.currency import Currency
from services.cbr_service import fetch_cbr_rates
from config import NATS_SUBJECT

async def update_currencies_periodically(app):
    print("[TASK] Фоновая задача обновления валют запущена")

    while True:
        try:
            rates = await fetch_cbr_rates()

            async with DBSession() as db:
                for currency_name, rate in rates.items():
                    result = await db.execute(
                        select(Currency).where(Currency.currency == currency_name)
                    )
                    existing = result.scalars().first()

                    if existing:
                        if existing.rate != rate:
                            print(
                                f"[DB] Обновление {currency_name}: "
                                f"{existing.rate} → {rate}"
                            )
                            existing.rate = rate
                            existing.updated_at = datetime.utcnow()
                    else:
                        print(f"[DB] Добавление новой валюты {currency_name} = {rate}")
                        db.add(Currency(currency=currency_name, rate=rate))

                await db.commit()

            if hasattr(app.state, "nc"):
                print("[NATS] Отправка события rates_update")
                await app.state.nc.publish(
                    NATS_SUBJECT,
                    json.dumps({
                        "event": "rates_update",
                        "rates": rates
                    }).encode()
                )

        except Exception as e:
            print("[TASK] Ошибка в фоновой задаче:", e)

        print("[TASK] Ожидание 120 секунд до следующего обновления\n")
        await asyncio.sleep(120)
