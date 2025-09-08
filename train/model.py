import torch.nn as nn

from config import config


class CandlePredictionModel(nn.Module):
    def __init__(self, dataset_type = 'hourly', input_size=6, lstm_hidden_size=128, lstm_layers=3, dense_hidden_size=32, output_size=12, dropout_p=0.3):
        super(CandlePredictionModel, self).__init__()
        if dataset_type == 'hourly':
            self.output_size = config['HOURLY_SAMPLE_OUTPUT_LENGTH']
        elif dataset_type == 'daily':
            self.output_size = config['DAILY_SAMPLE_OUTPUT_LENGTH']
        elif dataset_type == 'weekly':
            self.output_size = config['WEEKLY_SAMPLE_OUTPUT_LENGTH']
        else:
            self.output_size = output_size
        self.lstm = nn.LSTM(input_size, lstm_hidden_size, lstm_layers, batch_first=True, dropout=dropout_p)
        self.dropout = nn.Dropout(dropout_p)
        self.fc1 = nn.Linear(lstm_hidden_size, dense_hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(dense_hidden_size, self.output_size)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]
        x = self.dropout(last_hidden)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        output = self.fc2(x)
        return output