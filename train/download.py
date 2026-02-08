from datetime import datetime, timezone, timedelta
import aiohttp
import asyncio
import csv
import time
import dotenv
from config import config
import os

dotenv.load_dotenv()
# interval = config['HOURLY_INTERVAL'] # hourly prediction
# interval = config['DAILY_INTERVAL'] # daily prediction
# interval = config['WEEKLY_INTERVAL'] # weekly prediction
if config['dataset_type'] == 'hourly':
    interval = config['HOURLY_INTERVAL']
    PRICE_INFO_URL = f"https://data-api.coindesk.com/index/cc/v1/historical/minutes"
elif config['dataset_type'] == 'daily':
    interval = config['DAILY_INTERVAL']
    PRICE_INFO_URL = f"https://data-api.coindesk.com/index/cc/v1/historical/hours"
elif config['dataset_type'] == 'weekly':
    interval = config['WEEKLY_INTERVAL']
    PRICE_INFO_URL = f"https://data-api.coindesk.com/index/cc/v1/historical/days"

async def fetch_tao_history():
    api_key= os.getenv("COINDESK_API_KEY")  # Replace with your actual API key
    launch_date = datetime(2023, 12, 1, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    
    async with aiohttp.ClientSession() as session:
        current_ts = int(now.timestamp())
        start_ts = int(launch_date.timestamp())
        filename = f"{config['dataset_type']}_dataset.csv"
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'close', 'high', 'low', 'volume', 'volume_top_tier', 'volume_direct'])
        while current_ts > start_ts:
            params={
                "market": "cadli",
                "instrument": "TAO-USD",
                "limit": 200,
                "aggregate": interval,  # interval
                "fill": "true",
                "apply_mapping": "true",
                "response_format": "JSON",
                "to_ts": current_ts,
                "groups": ["OHLC", "VOLUME"],
                "api_key": api_key
            }
            async with session.get(PRICE_INFO_URL, params = params) as resp:
                print(interval, PRICE_INFO_URL)
                # resp.raise_for_status()
                result = await resp.json()
                # print(result)
                data_points = result.get("Data", [])
                
                if not data_points:
                    break
                data_points.reverse()
                earliest = min(dp['TIMESTAMP'] for dp in data_points)
                if len(data_points) != 200:
                    print(f"Count Error:{earliest} | {len(data_points)}")
                print(datetime.fromtimestamp(earliest, timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
                with open(filename, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for dp in data_points:
                        dt = datetime.fromtimestamp(dp['TIMESTAMP'], timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                        # writer.writerow([dp['TIMESTAMP'], dt, dp.get("CLOSE"), dp.get("HIGH"), dp.get("LOW"), dp.get('VOLUME'), buy_sell_vol_df['buy_volume'], buy_sell_vol_df['sell_volume']])
                        writer.writerow([dp['TIMESTAMP'], dp.get("CLOSE"), dp.get("HIGH"), dp.get("LOW"), dp.get('VOLUME'), dp.get("VOLUME_TOP_TIER"), dp.get("VOLUME_DIRECT")])

                if earliest < start_ts:
                    break
                current_ts = earliest - 1
    print(f"TAO {config['dataset_type']} interval price history successfully downloaded")

asyncio.run(fetch_tao_history())

# import aiohttp
# import asyncio
# from datetime import datetime, timezone, timedelta
# import pandas as pd

# API_KEY = "your_api_key_here"
# TRADES_API_URL = "https://data-api.coindesk.com/spot/v1/historical_trades"  # Example endpoint for trades

# async def fetch_trades(instrument="TAO-USD", start_ts=None, end_ts=None, limit=1000):
#     headers = {"Authorization": f"Bearer {API_KEY}"}
#     params = {
#         "instrument": instrument,
#         "limit": limit,
#         "start_ts": start_ts,
#         "end_ts": end_ts
#     }
#     async with aiohttp.ClientSession() as session:
#         async with session.get(TRADES_API_URL, headers=headers, params=params) as resp:
#             resp.raise_for_status()
#             return await resp.json()

# def aggregate_buy_sell_volumes(trades, interval_minutes=5):
#     # Convert timestamps and create DataFrame
#     df = pd.DataFrame(trades)
#     df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
#     df.set_index('timestamp', inplace=True)
    
#     # Resample to interval and sum volumes separated by side
#     buy_vol = df[df['side'] == 'buy'].resample(f'{interval_minutes}T')['volume'].sum()
#     sell_vol = df[df['side'] == 'sell'].resample(f'{interval_minutes}T')['volume'].sum()
    
#     # Combine into one DataFrame
#     result = pd.DataFrame({
#         'buy_volume': buy_vol,
#         'sell_volume': sell_vol
#     }).fillna(0)
    
#     return result

# async def main():
#     now_ts = int(datetime.now(timezone.utc).timestamp())
#     one_hour_ago_ts = now_ts - 3600  # e.g., fetch trades from last 1 hour for demo
    
#     data = await fetch_trades(start_ts=one_hour_ago_ts, end_ts=now_ts)
#     trades = data.get('trades', [])
    
#     buy_sell_vol_df = aggregate_buy_sell_volumes(trades, interval_minutes=5)
#     print(buy_sell_vol_df)

# asyncio.run(main())
