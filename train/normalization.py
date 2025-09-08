import pandas as pd
import json
import os

from config import config

filename = f"{config['dataset_type']}_dataset.csv"
normalization_filename = f"{config['dataset_type']}_normalization.csv"
df = pd.read_csv(filename)

cols = ['close', 'high', 'low', 'volume', 'volume_top_tier', 'volume_direct']
means = df[cols].mean()
stds = df[cols].std()

means.to_json(f'means_{config['dataset_type']}.json')
stds.to_json(f'stds_{config['dataset_type']}.json')

# Apply normalization
df_norm = df.copy()
df_norm[cols] = (df[cols] - means) / stds
df_norm[cols] = df_norm[cols].astype('float32')
df_norm = df_norm.sort_values(by='timestamp', ascending=True)
df_norm.to_csv(normalization_filename, index=False)
print(df_norm.head())
print(means,stds)
    