config = {
    'HOURLY_INTERVAL' : 10,  # 10 minutes
    'DAILY_INTERVAL' : 4, # 4 hour
    'WEEKLY_INTERVAL' : 1, # 1 day
    'HOURLY_SAMPLE_INPUT_LENGTH': int(60 / 10 * 24), # Use data every 5 mintues
    'HOURLY_SAMPLE_OUTPUT_LENGTH' : int(60 / 10 * 1), # Use data every 5 mintues
    'DAILY_SAMPLE_INPUT_LENGTH' : int(24 / 4 * 20), # Use data per hour
    'DAILY_SAMPLE_OUTPUT_LENGTH' : int(24 / 4 * 1), # Use data per hour
    'WEEKLY_SAMPLE_INPUT_LENGTH' : int(24 / 24 * 7 * 10), # Use data every 6 hours
    'WEEKLY_SAMPLE_OUTPUT_LENGTH' : int(24 / 24 * 7 * 1), # Use data every 6 hours
    'TRAIN_RATE' : 0.5,
    'VALID_RATE' : 0.3,
    'BATCH_SIZE' : 128,
    'dataset_type': 'hourly' # 'hourly', 'daily', 'weekly'
}