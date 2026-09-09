import os
import io
import sys
import json
import shutil
import pickle
import zipfile
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms


class Network(nn.Module):
    def __init__(self, num_classes=19):
        super(Network, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=6, kernel_size=5)
        self.conv2 = nn.Conv2d(in_channels=6, out_channels=12, kernel_size=5)
        self.conv3 = nn.Conv2d(in_channels=12, out_channels=24, kernel_size=5)
        self.conv4 = nn.Conv2d(in_channels=24, out_channels=48, kernel_size=5)

        self.fc1 = nn.Linear(in_features=48 * 12 * 12, out_features=240)
        self.fc2 = nn.Linear(in_features=240, out_features=120)
        self.out = nn.Linear(in_features=120, out_features=num_classes)

    def forward(self, t):
        t = F.max_pool2d(F.relu(self.conv1(t)), kernel_size=2, stride=2)
        t = F.max_pool2d(F.relu(self.conv2(t)), kernel_size=2, stride=2)
        t = F.max_pool2d(F.relu(self.conv3(t)), kernel_size=2, stride=2)
        t = F.max_pool2d(F.relu(self.conv4(t)), kernel_size=2, stride=2)

        t = t.reshape(-1, 48 * 12 * 12)
        t = F.relu(self.fc1(t))
        t = F.relu(self.fc2(t))
        t = self.out(t)
        return t


class PlantDataset(Dataset):
    def __init__(self, file_label_pairs, transform=None):
        self.samples = file_label_pairs
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        try:
            with Image.open(path) as img:
                img = img.convert('RGB')
                if self.transform:
                    img = self.transform(img)
                return img, label
        except Exception as e:
            # Fallback for corrupted images
            blank = Image.new('RGB', (256, 256))
            if self.transform:
                blank = self.transform(blank)
            return blank, label


def prepare_datasets(base_dir):
    model_dir = os.path.join(base_dir, 'model')
    dataset_zip = os.path.join(model_dir, 'dataset.zip')
    extracted_dir = os.path.join(model_dir, 'dataset_extracted')
    papaya_dir = os.path.join(model_dir, 'papaya_dataset')

    # Extract dataset.zip if needed
    if not os.path.exists(extracted_dir):
        print(f"Extracting {dataset_zip} to {extracted_dir}...")
        with zipfile.ZipFile(dataset_zip, 'r') as z:
            z.extractall(extracted_dir)
        print("Extraction complete.")

    train_base = os.path.join(extracted_dir, 'dataset', 'train')
    valid_base = os.path.join(extracted_dir, 'dataset', 'valid')

    # Load existing labels mapping
    existing_labels_path = os.path.join(base_dir, 'api', 'src', 'model_files', 'labels.json')
    with open(existing_labels_path, 'rb') as f:
        labels_map = pickle.load(f)

    # Add Papaya classes
    if 'Papaya___disease' not in labels_map:
        labels_map['Papaya___disease'] = 17
    if 'Papaya___healthy' not in labels_map:
        labels_map['Papaya___healthy'] = 18

    print("Target classes (19 total):")
    for k, v in sorted(labels_map.items(), key=lambda x: x[1]):
        print(f"  [{v:02d}] {k}")

    train_samples = []
    valid_samples = []

    # 1. Collect standard dataset classes (0..16)
    for class_name, class_idx in labels_map.items():
        if class_idx >= 17:
            continue
        c_train_dir = os.path.join(train_base, class_name)
        if os.path.exists(c_train_dir):
            for f in os.listdir(c_train_dir):
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    train_samples.append((os.path.join(c_train_dir, f), class_idx))

        c_valid_dir = os.path.join(valid_base, class_name)
        if os.path.exists(c_valid_dir):
            for f in os.listdir(c_valid_dir):
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    valid_samples.append((os.path.join(c_valid_dir, f), class_idx))

    # 2. Collect Papaya dataset
    # Training
    p_train_disease = os.path.join(papaya_dir, 'training', 'disease')
    if os.path.exists(p_train_disease):
        for f in os.listdir(p_train_disease):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                train_samples.append((os.path.join(p_train_disease, f), labels_map['Papaya___disease']))

    p_train_fresh = os.path.join(papaya_dir, 'training', 'fresh')
    if os.path.exists(p_train_fresh):
        for f in os.listdir(p_train_fresh):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                train_samples.append((os.path.join(p_train_fresh, f), labels_map['Papaya___healthy']))

    # Validation
    p_valid_disease = os.path.join(papaya_dir, 'validation', 'disease')
    if os.path.exists(p_valid_disease):
        for f in os.listdir(p_valid_disease):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                valid_samples.append((os.path.join(p_valid_disease, f), labels_map['Papaya___disease']))

    p_valid_fresh = os.path.join(papaya_dir, 'validation', 'fresh')
    if os.path.exists(p_valid_fresh):
        for f in os.listdir(p_valid_fresh):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                valid_samples.append((os.path.join(p_valid_fresh, f), labels_map['Papaya___healthy']))

    print(f"Total training samples: {len(train_samples)}")
    print(f"Total validation samples: {len(valid_samples)}")

    return train_samples, valid_samples, labels_map


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    train_samples, valid_samples, labels_map = prepare_datasets(base_dir)

    # Transforms
    train_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
        transforms.ToTensor(),
    ])

    valid_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
    ])

    train_dataset = PlantDataset(train_samples, transform=train_transform)
    valid_dataset = PlantDataset(valid_samples, transform=valid_transform)

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=0)
    valid_loader = DataLoader(valid_dataset, batch_size=32, shuffle=False, num_workers=0)

    # Instantiate model with 19 classes
    model = Network(num_classes=19)

    # Load pretrained weights from existing model.pth
    old_model_path = os.path.join(base_dir, 'api', 'src', 'model_files', 'model.pth')
    if os.path.exists(old_model_path):
        print(f"Loading pretrained weights from {old_model_path}...")
        old_state = torch.load(old_model_path, map_location='cpu')
        new_state = model.state_dict()

        for k in ['conv1.weight', 'conv1.bias', 'conv2.weight', 'conv2.bias',
                  'conv3.weight', 'conv3.bias', 'conv4.weight', 'conv4.bias',
                  'fc1.weight', 'fc1.bias', 'fc2.weight', 'fc2.bias']:
            if k in old_state:
                new_state[k] = old_state[k]

        # Transfer existing 17 class weights to out layer
        if 'out.weight' in old_state:
            new_state['out.weight'][:17, :] = old_state['out.weight'][:17, :]
        if 'out.bias' in old_state:
            new_state['out.bias'][:17] = old_state['out.bias'][:17]

        model.load_state_dict(new_state)
        print("Pretrained weights successfully transferred!")

    # Set up optimizer and loss
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0008, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=4, gamma=0.5)

    num_epochs = 10
    print(f"\nStarting training for {num_epochs} epochs on CPU...")

    best_val_acc = 0.0
    best_state_dict = None

    for epoch in range(1, num_epochs + 1):
        model.train()
        train_loss = 0.0
        train_correct = 0
        total_train = 0

        for x, y in train_loader:
            optimizer.zero_grad()
            outputs = model(x)
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * x.size(0)
            preds = outputs.argmax(dim=1)
            train_correct += (preds == y).sum().item()
            total_train += x.size(0)

        scheduler.step()

        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        total_val = 0

        with torch.no_grad():
            for x, y in valid_loader:
                outputs = model(x)
                loss = criterion(outputs, y)
                val_loss += loss.item() * x.size(0)
                preds = outputs.argmax(dim=1)
                val_correct += (preds == y).sum().item()
                total_val += x.size(0)

        train_acc = 100.0 * train_correct / total_train
        val_acc = 100.0 * val_correct / total_val
        avg_train_loss = train_loss / total_train
        avg_val_loss = val_loss / total_val

        print(f"Epoch [{epoch:02d}/{num_epochs:02d}] "
              f"Train Loss: {avg_train_loss:.4f} | Train Acc: {train_acc:.2f}% | "
              f"Val Loss: {avg_val_loss:.4f} | Val Acc: {val_acc:.2f}%")

        if val_acc > best_val_acc or best_state_dict is None:
            best_val_acc = val_acc
            best_state_dict = model.state_dict()

    print(f"\nTraining complete! Best Validation Accuracy: {best_val_acc:.2f}%")

    # Backup old weights and labels
    api_model_dir = os.path.join(base_dir, 'api', 'src', 'model_files')
    backup_model_path = os.path.join(api_model_dir, 'model_17class_backup.pth')
    backup_labels_path = os.path.join(api_model_dir, 'labels_17class_backup.json')

    if os.path.exists(old_model_path) and not os.path.exists(backup_model_path):
        shutil.copyfile(old_model_path, backup_model_path)
        print(f"Backed up old model to {backup_model_path}")

    current_labels_path = os.path.join(api_model_dir, 'labels.json')
    if os.path.exists(current_labels_path) and not os.path.exists(backup_labels_path):
        shutil.copyfile(current_labels_path, backup_labels_path)
        print(f"Backed up old labels to {backup_labels_path}")

    # Save new model state dict & labels
    torch.save(best_state_dict, old_model_path)
    print(f"Saved new 19-class model to {old_model_path}")

    with open(current_labels_path, 'wb') as f:
        pickle.dump(labels_map, f)
    print(f"Saved new 19-class labels mapping to {current_labels_path}")


if __name__ == '__main__':
    main()
