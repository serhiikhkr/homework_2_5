import aiohttp
import asyncio
import json
import sys
from datetime import datetime, timedelta


class ApiClient:
    @staticmethod
    async def fetch_exchange_rate(session, date):
        url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}'
        async with session.get(url) as response:
            data = await response.json()
            return data


class DataSaver:
    @staticmethod
    def save_to_file(filename, data):
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
            print(json.dumps(data, indent=2))  # Выводим в консоль


def get_dates(num_days):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=num_days)
    date_list = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
    return [date.strftime('%d.%m.%Y') for date in date_list]


async def main():
    num_days = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    if num_days > 10:
        print("Ошибка: количество дней не может превышать 10.")
        return

    dates = get_dates(num_days)
    exchange_rates = []

    api_client = ApiClient()

    async with aiohttp.ClientSession() as session:
        for date in dates:
            data = await api_client.fetch_exchange_rate(session, date)
            currencies = data.get('exchangeRate', [])
            rates = {}

            if not currencies:
                rates = 'Data not available'
            else:
                for currency in currencies:
                    if currency['currency'] in ['EUR', 'USD']:
                        rates[currency['currency']] = {
                            'sale': currency['saleRateNB'],
                            'purchase': currency['purchaseRateNB']
                        }

            exchange_rates.append({date: rates})

    data_saver = DataSaver()
    data_saver.save_to_file('exchange_rates.json', exchange_rates)


if __name__ == '__main__':
    asyncio.run(main())
