import aiohttp
import asyncio
from datetime import datetime, timedelta
import json

class CurrencyRate:
    def __init__(self, days):
        self.days = min(max(1, days), 10)
        self.api_url = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

    async def fetch(self, session, url):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Error: status code {response.status}")
                    return None

        except Exception as e:
            print(f"An error with making a request: {e}")
            return None

    async def get_currency_rate(self):
        currency_data = []
        async with aiohttp.ClientSession() as session:
            for day in range(self.days):
                date = datetime.now() - timedelta(days=day)
                formatted_date = date.strftime("%d.%m.%Y")
                url = self.api_url + date.strftime("%d.%m.%Y")
                response = await self.fetch(session, url)
                if response is None:
                    print(f"Could not fetch data for {formatted_date}")
                    continue
                try:
                    data = json.loads(response)
                except json.JSONDecodeError as e:
                    print(f"An error occurred while parsing the response: {e}")
                    continue
                eur_data = next((item for item in data['exchangeRate'] if item["currency"] == "EUR"), None)
                usd_data = next((item for item in data['exchangeRate'] if item["currency"] == "USD"), None)
                currency_data.append({
                    formatted_date: {
                        'EUR': {
                            'sale': eur_data['saleRate'],
                            'purchase': eur_data['purchaseRate']
                        },
                        'USD': {
                            'sale': usd_data['saleRate'],
                            'purchase': usd_data['purchaseRate']
                        }
                    }
                })
        return currency_data

    async def main(self):
        currency_data = await self.get_currency_rate()
        print(json.dumps(currency_data, indent=2))

if __name__ == "__main__":
    import sys
    days = int(sys.argv[1])
    rate = CurrencyRate(days)
    asyncio.run(rate.main())
