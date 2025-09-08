import torch
import torch.optim as optim
import matplotlib.pyplot as plt
import pandas as pd
import random
from tqdm import tqdm

from config import config
from dataset import CandleDataset
from dataloader import CandleDataLoader
from model import CandlePredictionModel

# Variable setting(Dataset, ...)
filename = f"{config['dataset_type']}_normalization.csv"
df = pd.read_csv(filename)
start_timestamp = df['timestamp'][0]
if config['dataset_type'] == 'hourly':
    timestamp_interval = config['HOURLY_INTERVAL'] * 60
elif config['dataset_type'] == 'daily':
    timestamp_interval = config['DAILY_INTERVAL'] * 60 * 60
elif config['dataset_type'] == 'weekly':
    timestamp_interval = config['WEEKLY_INTERVAL'] * 60 * 60 * 24
    
cols = ['close', 'high', 'low','volume', 'volume_top_tier', 'volume_direct']
dataset_length = int((max(df['timestamp']) - df['timestamp'][0]) / timestamp_interval + 1 - (config['HOURLY_SAMPLE_INPUT_LENGTH'] + config['HOURLY_SAMPLE_OUTPUT_LENGTH']) + 1)
dataset = df[cols].to_numpy()

dataset_list = list(range(dataset_length))
random.shuffle(dataset_list)

train_list_length = int(dataset_length * config['TRAIN_RATE'])
valid_list_length = int(dataset_length * config['VALID_RATE'])

train_dataset_list = dataset_list[:train_list_length]
valid_dataset_list = dataset_list[train_list_length:train_list_length + valid_list_length]
test_dataset_list = dataset_list[train_list_length + valid_list_length:]
print(type(train_dataset_list), type(train_dataset_list[0]))
print(dataset.shape, type(config['HOURLY_SAMPLE_INPUT_LENGTH']))

# functions for model training and testing

def custom_loss(outputs, targets):
    return torch.mean((outputs - targets) ** 2)

# def lr_for_epoch(epoch):
#     if epoch < 20:
#         return 1e-3
#     elif epoch < 50:
#         return 1e-4
#     elif epoch < 70:
#         return 5e-5
#     else:
#         return 1e-5
    
def train_model(model, optimizer, device, num_epochs=50):
    train_losses = []
    valid_losses = []
    candle_train_dataset = CandleDataset(train_dataset_list, dataset, dataset_type=config['dataset_type'])
    prev_valid_loss = float('inf')
    for epoch in range(num_epochs):
        # lr = lr_for_epoch(epoch)
        # for param_group in optimizer.param_groups:
        #     param_group['lr'] = lr
        print(f"Epoch {epoch+1}, Learning Rate: {optimizer.param_groups[0]['lr']}")
        model.train()
        running_train_loss = 0.0
        candle_train_loader = CandleDataLoader(candle_train_dataset, batch_size=config['BATCH_SIZE'], shuffle=True)
        pbar = tqdm(candle_train_loader)
        candle_train_loader.prefetch()
        for batch_x, batch_y in pbar:
            candle_train_loader.prefetch()
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = custom_loss(outputs, batch_y)
            loss.backward()
            optimizer.step()
            running_train_loss += loss.item()

        avg_train_loss = running_train_loss / len(candle_train_loader)
        train_losses.append(avg_train_loss)

        model.eval()
        running_valid_loss = 0.0
        candle_valid_dataset = CandleDataset(valid_dataset_list, dataset, dataset_type=config['dataset_type'])
        candle_valid_loader = CandleDataLoader(candle_valid_dataset, batch_size=config['BATCH_SIZE'], shuffle=False)
        pbar = tqdm(candle_valid_loader)
        candle_valid_loader.prefetch()
        with torch.no_grad():
            for batch_x, batch_y in pbar:
                candle_valid_loader.prefetch()
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                outputs = model(batch_x)
                loss = custom_loss(outputs, batch_y)
                running_valid_loss += loss.item()
        avg_valid_loss = running_valid_loss / len(candle_valid_loader)
        valid_losses.append(avg_valid_loss)
        
        if epoch > 0 and avg_valid_loss > prev_valid_loss:
            for pg in optimizer.param_groups:
                old_lr = pg['lr']
                new_lr = max(old_lr * 0.5, 1e-6)  # avoid going to zero
                pg['lr'] = new_lr
            print(f"Epoch {epoch+1}: validation loss increased. Halving LR to {new_lr:.6f}")
        
        prev_valid_loss = avg_valid_loss
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': avg_train_loss,
        }, f'model/{config['dataset_type']}/model_checkpoint_{epoch:02d}.pth')

        print(f"Epoch [{epoch + 1}/{num_epochs}], Train Loss: {avg_train_loss:.4f}, Valid Loss: {avg_valid_loss:.4f}")

    # Plot loss curves
    plt.figure(figsize=(8, 5))
    plt.plot(range(1, num_epochs + 1), train_losses, label='Train Loss')
    plt.plot(range(1, num_epochs + 1), valid_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training & Validation Loss')
    plt.legend()
    plt.savefig(f'model/loss_plot_{config['dataset_type']}.png')
    plt.show()

    return train_losses, valid_losses

def test_model(model, device):
    model.eval()
    running_test_loss = 0.0
    candle_test_dataset = CandleDataset(test_dataset_list, dataset, dataset_type=config['dataset_type'])
    candle_test_loader = CandleDataLoader(candle_test_dataset, batch_size=config['BATCH_SIZE'], shuffle=False)
    pbar = tqdm(candle_test_loader)
    candle_test_loader.prefetch()
    with torch.no_grad():
        for batch_x, batch_y in pbar:
            candle_test_loader.prefetch()
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            outputs = model(batch_x)
            loss = custom_loss(outputs, batch_y)
            running_test_loss += loss.item()
    avg_test_loss = running_test_loss / len(candle_test_loader)
    print(f"Test Loss: {avg_test_loss:.4f}")
    return avg_test_loss

model = CandlePredictionModel()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
optimizer = optim.Adam(model.parameters(), lr=1e-3)
num_epochs = 150

train_losses, valid_losses = train_model(model, optimizer, device, num_epochs)
print(train_losses, valid_losses)
# checkpoint = torch.load('model/model_checkpoint_49.pth')
# model.load_state_dict(checkpoint['model_state_dict'])
# model.to(device)
# print(dataset[182300:182588, :].shape)
# y = model(torch.tensor(dataset[182300:182588, :].reshape(1, 288, 6), dtype=torch.float32))
# import json
# with open('means.json', 'r') as file:
#     means = json.load(file)
# with open('stds.json', 'r') as file:
#     stds = json.load(file)

# y = y * stds['close'] + means['close']
# print(y)