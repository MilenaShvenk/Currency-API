import httpx
from config import CURRENCY_CODES

async def fetch_cbr_rates():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()

        return {
            code: data["Valute"][code]["Value"]
            for code in CURRENCY_CODES
        }
