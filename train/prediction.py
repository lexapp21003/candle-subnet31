from datetime import datetime, timezone, timedelta
import aiohttp
import asyncio
import csv
import time
import numpy as np
import random
from decimal import Decimal
import pandas as pd
import json
import torch


from config import config
from model import CandlePredictionModel

async def fetch_tao_history(interval, current_ts, sample_count):
    PRICE_INFO_URL = f"https://data-api.coindesk.com/index/cc/v1/historical/minutes"
    if interval == config['HOURLY_INTERVAL']:
        PRICE_INFO_URL = f"https://data-api.coindesk.com/index/cc/v1/historical/minutes"
        means_filename = 'means_hourly.json'
        stds_filename = 'stds_hourly.json'
    elif interval == config['DAILY_INTERVAL']:
        PRICE_INFO_URL = f"https://data-api.coindesk.com/index/cc/v1/historical/hours"
        means_filename = 'means_daily.json'
        stds_filename = 'stds_daily.json'
    elif interval == config['WEEKLY_INTERVAL']:
        PRICE_INFO_URL = f"https://data-api.coindesk.com/index/cc/v1/historical/days"
        means_filename = 'means_weekly.json'
        stds_filename = 'stds_weekly.json'
    api_key= "f8152ac7443b093e3ee1e3f67293e5e7144fa4e6945138af1e108a107ed5a1fe"
    
    async with aiohttp.ClientSession() as session:

        params={
            "market": "cadli",
            "instrument": "TAO-USD",
            "limit": sample_count,
            "aggregate": interval,
            "fill": "true",
            "apply_mapping": "true",
            "response_format": "JSON",
            "to_ts": current_ts,
            "groups": ["OHLC", "VOLUME"],
            "api_key": api_key
        }
        async with session.get(PRICE_INFO_URL, params = params) as resp:
            # resp.raise_for_status()
            result = await resp.json()
            data_points = result.get("Data", [])
            
            min_timestamp = min(dp['TIMESTAMP'] for dp in data_points)
            max_timestamp = max(dp['TIMESTAMP'] for dp in data_points)
            
            if not data_points:
                print("No data points retrieved.")
            if len(data_points) != sample_count:
                print(f"Count Error: {sample_count} | {len(data_points)}")
            input_data = []
            with open(means_filename, 'r') as file:
                means = json.load(file)
            with open(stds_filename, 'r') as file:
                stds = json.load(file)
            cols = ['close','high','low','volume','volume_top_tier','volume_direct']
            means = np.asarray([float(means[col]) for col in cols], dtype=np.float32)
            stds = np.asarray([float(stds[col]) for col in cols], dtype=np.float32)
            for dp in data_points:
                input_data.append([dp.get("CLOSE"), dp.get("HIGH"), dp.get("LOW"), dp.get('VOLUME'), dp.get("VOLUME_TOP_TIER"), dp.get("VOLUME_DIRECT")])
            input_data = np.asarray(input_data, dtype=np.float32)
            input_data = (input_data - means) / stds
            print(input_data)
            return input_data, min_timestamp, max_timestamp

def save(interval, after_timestamp, color, after_price):
    if interval == config['HOURLY_INTERVAL']:
        filename = "/root/.candles/data/hourly_prediction.csv"
        next_timestamp = after_timestamp + 60 * 60
        means_filename = "means_hourly.json"
        stds_filename = "stds_hourly.json"
        prediction_type = 'hourly'
    elif interval == config['DAILY_INTERVAL']:
        filename = "/root/.candles/data/daily_prediction.csv"
        next_timestamp = after_timestamp + 60 * 60 * 24
        means_filename = "means_daily.json"
        stds_filename = "stds_daily.json"
        prediction_type = 'daily'
    elif interval == config['WEEKLY_INTERVAL']:
        filename = "/root/.candles/data/weekly_prediction.csv"
        next_timestamp = after_timestamp + 60 * 60 * 24 * 7
        means_filename = "means_weekly.json"
        stds_filename = "stds_weekly.json"
        prediction_type = 'weekly'
    
    confidence1 = Decimal(str(random.uniform(0.6, 0.8)))
    confidence2 = Decimal(str(random.uniform(0.6, 0.8)))
    
    with open(means_filename,'r') as file:
        means = json.load(file)
    with open(stds_filename, 'r') as file:
        stds = json.load(file)
    
    after_price = after_price * stds['close'] + means['close']
    
    df = pd.DataFrame([
        {'timestamp': int(after_timestamp), 'color': color, 'confidence': confidence1, 'price': float(after_price.item())},
        {'timestamp': int(next_timestamp), 'color': color, 'confidence': confidence2, 'price': float(after_price.item())}
    ])
    print(f"[green]Prediction Type: {prediction_type} | Price : {after_price}")
    df.to_csv(filename, index=False) 
    print(f"Successfully saved prediction to {filename} | Interval : {interval} | Time : {datetime.fromtimestamp(after_timestamp, timezone.utc)}")

async def prediction_updating(current_ts, interval):
    current_ts = int(current_ts)
    current_dt = datetime.fromtimestamp(current_ts, timezone.utc)
    if interval == config['HOURLY_INTERVAL']:
        prediction_timestamp = current_dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        input_data, min_timestamp, max_timestamp = await fetch_tao_history(config['HOURLY_INTERVAL'],current_ts, config['HOURLY_SAMPLE_INPUT_LENGTH'])
        print(f"MAX Timestamp:{max_timestamp} | MIN Timestamp:{min_timestamp}")
        
        model = CandlePredictionModel(dataset_type='hourly')
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load('model/hourly/model_checkpoint_98.pth')
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(device)
        output = model(torch.tensor(np.array(input_data).reshape(1, config['HOURLY_SAMPLE_INPUT_LENGTH'], 6), dtype=torch.float32))
        output = output.reshape(config['HOURLY_SAMPLE_OUTPUT_LENGTH'])
        
        index = int((prediction_timestamp.timestamp() - max_timestamp) / (interval * 60))
        length = config['HOURLY_SAMPLE_OUTPUT_LENGTH']
    elif interval == config['DAILY_INTERVAL']:
        prediction_timestamp = current_dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        input_data, min_timestamp, max_timestamp = await fetch_tao_history(config['DAILY_INTERVAL'],current_ts, config['DAILY_SAMPLE_INPUT_LENGTH'])
        print(f"MAX Timestamp:{max_timestamp} | MIN Timestamp:{min_timestamp}")
        
        model = CandlePredictionModel(dataset_type='daily')
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load('model/daily/model_checkpoint_99.pth')
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(device)
        output = model(torch.tensor(np.array(input_data).reshape(1, config['DAILY_SAMPLE_INPUT_LENGTH'], 6), dtype=torch.float32))
        output = output.reshape(config['DAILY_SAMPLE_OUTPUT_LENGTH'])
        
        index = int((prediction_timestamp.timestamp() - max_timestamp) / (interval * 60 * 60))
        length = config['DAILY_SAMPLE_OUTPUT_LENGTH']
    elif interval == config['WEEKLY_INTERVAL']:
        days_until_monday = (7 - current_dt.weekday()) % 7
        if days_until_monday == 0:  # If today is Monday, go to next Monday
            days_until_monday = 7
        prediction_timestamp = current_dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
        input_data, min_timestamp, max_timestamp = await fetch_tao_history(config['WEEKLY_INTERVAL'],current_ts, config['WEEKLY_SAMPLE_INPUT_LENGTH'])
        print(f"MAX Timestamp:{max_timestamp} | MIN Timestamp:{min_timestamp}")
        
        model = CandlePredictionModel(dataset_type='weekly')
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load('model/weekly/model_checkpoint_99.pth')
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(device)
        output = model(torch.tensor(np.array(input_data).reshape(1, config['WEEKLY_SAMPLE_INPUT_LENGTH'], 6), dtype=torch.float32))
        output = output.reshape(config['WEEKLY_SAMPLE_OUTPUT_LENGTH'])
        
        index = int((prediction_timestamp.timestamp() - max_timestamp) / (interval * 60 * 60 * 24))
        length = config['WEEKLY_SAMPLE_OUTPUT_LENGTH']
    
    before_index = int(index - length - 2)
    color = "Green" if output[index - 1] > input_data[before_index][0] else "Red"
    save(interval, prediction_timestamp.timestamp(), color, output[index - 1])
    dt = datetime.fromtimestamp(current_ts, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    print(dt)

async def main():
    current_ts = time.time()
    await prediction_updating(current_ts, config['HOURLY_INTERVAL'])
    await prediction_updating(current_ts, config['DAILY_INTERVAL'])
    await prediction_updating(current_ts, config['WEEKLY_INTERVAL'])
    
    while True:
        current_ts = time.time()
        if int(current_ts) % 1800 < 5: # every 30 minutes updated
            start_time = time.time()
            print("Hourly Prediction Updating ...")
            await prediction_updating(current_ts, config['HOURLY_INTERVAL'])
            time.sleep(2)
            print(f"Hourly Prediction Time Used: {time.time() - start_time} seconds")
        if 20 < int(current_ts) % (3600 * 12) < 25: # every 12 hours updated
            start_time = time.time()
            print("Daily Prediction Updating ...")
            await prediction_updating(current_ts, config['DAILY_INTERVAL'])
            time.sleep(2)
            print(f"Daily Prediction Time Used: {time.time() - start_time} seconds")
            
        if 50 < int(current_ts) % (3600 * 24 * 3) < 55:
            start_time = time.time()
            print("Weekly Prediction Updating ...")
            await prediction_updating(current_ts, config['WEEKLY_INTERVAL'])
            time.sleep(2)
            print(f"Weekly Prediction Time Used: {time.time() - start_time} seconds")
        print(f"Monitoring... [yellow]{datetime.fromtimestamp(current_ts, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}[/yellow]")
        time.sleep(3)

    
if __name__ == "__main__":
    asyncio.run(main())
# await prediction_updating(current_ts, config['DAILY_INTERVAL'])
# await prediction_updating(current_ts, config['WEEKLY_INTERVAL'])
# while True:
#     current_ts = time.time()
#     if int(current_ts) % 60 < 5: # every 30 minutes updated
#         start_time = time.time()
#         print("Hourly Prediction Updating ...")
#         prediction_updating(current_ts, config['HOURLY_INTERVAL'])
#         time.sleep(2)
#         print(f"Hourly Prediction Time Used: {time.time() - start_time} seconds")
#     if 20 < int(current_ts) % (3600 * 12) < 25: # every 12 hours updated
#         start_time = time.time()
#         print("Daily Prediction Updating ...")
#         prediction_updating(current_ts, config['DAILY_INTERVAL'])
#         time.sleep(2)
#         print(f"Daily Prediction Time Used: {time.time() - start_time} seconds")
        
#     if 50 < int(current_ts) % (3600 * 24 * 3) < 55:
#         start_time = time.time()
#         print("Weekly Prediction Updating ...")
#         prediction_updating(current_ts, config['WEEKLY_INTERVAL'])
#         time.sleep(2)
#         print(f"Weekly Prediction Time Used: {time.time() - start_time} seconds")
#     print(f"Monitoring... [yellow]{datetime.fromtimestamp(current_ts, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}[/yellow]")
#     time.sleep(3)