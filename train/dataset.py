import sys
from pathlib import Path

import torch
from torch.utils.data import Dataset
from config import config

class CandleDataset(Dataset):
    def __init__(self, data_list, dataset, dataset_type):
        self.data_list = data_list
        self.dataset = torch.tensor(dataset, dtype=torch.float32)
        self.dataset_type = dataset_type
        self.sample_length_input = None
        self.sample_length_output = None
        print(type(self.dataset))
        
    def __len__(self):
        return len(self.data_list)

    def __getitem__(self, idx):
        # print(f"Prefetching...{idx}")
        return self.get_sample_data(self.data_list[idx])
        
    def get_sample_data(self, idx):
        if self.dataset_type == 'hourly':
            self.sample_length_input = config['HOURLY_SAMPLE_INPUT_LENGTH']
            self.sample_length_output = config['HOURLY_SAMPLE_OUTPUT_LENGTH']
        elif self.dataset_type == 'daily':
            self.sample_length_input = config['DAILY_SAMPLE_INPUT_LENGTH']
            self.sample_length_output = config['DAILY_SAMPLE_OUTPUT_LENGTH']
        elif self.dataset_type == 'weekly':
            self.sample_length_input = config['WEEKLY_SAMPLE_INPUT_LENGTH']
            self.sample_length_output = config['WEEKLY_SAMPLE_OUTPUT_LENGTH']
        else: print(f"Dataset Type Invaild: {self.dataset_type}")
        
        if self.sample_length_input is None or self.sample_length_output is None:
            return None, None
        
        return self.dataset[idx:idx + self.sample_length_input, :], self.dataset[idx + self.sample_length_input:idx + self.sample_length_input + self.sample_length_output, 0:1].reshape(-1)
