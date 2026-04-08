"""
Training Script for Plant Disease CNN
Fine-tunes MobileNetV2 on your dataset
"""
#imports 
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, datasets
from pathlib import Path
import time
from tqdm import tqdm
import json

import sys
import os
# adding the root dir 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from plant_disease_cnn import PlantDiseaseCNN


class PlantDiseaseTrainer:
    def __init__(self, 
                 data_dir,
                 num_classes=38,
                 batch_size=32,
                 learning_rate=0.01,
                 num_epochs=10,
                 device=None):
        """
        Initialize trainer
        
        Args:
            data_dir: Path to dataset (should have train/val subdirectories)
            num_classes: Number of disease classes
            batch_size: Batch size for training
            learning_rate: Learning rate
            num_epochs: Number of training epochs
            device: torch device (auto-detect if None)
        """

        self.data_dir = Path(data_dir)
        self.num_classes = num_classes
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        
        # Set device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
        
        print(f"Using device: {self.device}")
        
        # Initialize model
        self.model = PlantDiseaseCNN(num_classes=num_classes)
        
        # Stronger data augmentation for training
        self.train_transform = transforms.Compose([
            transforms.Resize(256),
            transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),  # random zoom
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(p=0.15),
            transforms.RandomRotation(20),
            transforms.ColorJitter(brightness=0.3, contrast=0.3,
                                   saturation=0.3, hue=0.05),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            transforms.RandomErasing(p=0.2, scale=(0.02, 0.15)),  # hide random patches
        ])
        
        # Validation transform (no augmentation)
        self.val_transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Load datasets
        self.train_dataset = None
        self.val_dataset = None
        self.train_loader = None
        self.val_loader = None
        
        # Training history
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
    
    def load_data(self):
        """Load training and validation datasets with class-balanced sampling."""
        from torch.utils.data import WeightedRandomSampler
        import torch

        train_dir = self.data_dir / 'train'
        val_dir   = self.data_dir / 'val'

        if not train_dir.exists():
            raise FileNotFoundError(f"Training directory not found: {train_dir}")
        if not val_dir.exists():
            raise FileNotFoundError(f"Validation directory not found: {val_dir}")

        # Load datasets
        self.train_dataset = datasets.ImageFolder(
            root=train_dir,
            transform=self.train_transform
        )

        self.val_dataset = datasets.ImageFolder(
            root=val_dir,
            transform=self.val_transform
        )

        # ── Weighted sampler: give every class equal training probability ──
        # 1. Count how many samples each class has
        class_counts = torch.zeros(len(self.train_dataset.classes))
        for _, label in self.train_dataset.samples:
            class_counts[label] += 1

        # 2. Weight = 1 / class_count  (rare classes get higher weight)
        class_weights = 1.0 / class_counts.clamp(min=1)

        # 3. Assign per-sample weight
        sample_weights = torch.tensor(
            [class_weights[label] for _, label in self.train_dataset.samples]
        )

        sampler = WeightedRandomSampler(
            weights=sample_weights,
            num_samples=len(sample_weights),
            replacement=True          # allow oversampling of rare classes
        )

        # Print imbalance info
        print(f"\nClass balance info:")
        print(f"  Min samples per class : {int(class_counts.min())}")
        print(f"  Max samples per class : {int(class_counts.max())}")
        print(f"  Median                : {int(class_counts.median())}")
        imbalance_ratio = class_counts.max() / class_counts.min()
        status = 'HIGH - consider more balancing' if imbalance_ratio > 10 else 'ok'
        print(f"  Imbalance ratio       : {imbalance_ratio:.1f}x  ({status})")
        print("  WeightedRandomSampler active: all classes trained equally\n")

        # ── Data loaders ───────────────────────────────────────────────────
        self.train_loader = DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            sampler=sampler,           # replaces shuffle=True
            num_workers=4,
            pin_memory=True if self.device.type == 'cuda' else False,
            persistent_workers=True
        )

        self.val_loader = DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=4,
            pin_memory=True if self.device.type == 'cuda' else False,
            persistent_workers=True
        )

        # Update class names in model
        self.model.class_names = self.train_dataset.classes

        print(f"Training samples  : {len(self.train_dataset)}")
        print(f"Validation samples: {len(self.val_dataset)}")
        print(f"Number of classes : {len(self.train_dataset.classes)}")
        print(f"Classes (first 5) : {self.train_dataset.classes[:5]} ...")
    
    def train_epoch(self, optimizer, criterion):
        """Train for one epoch"""
        self.model.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(self.train_loader, desc='Training')
        for inputs, labels in pbar:
            inputs, labels = inputs.to(self.device), labels.to(self.device)
            
            # Zero gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model.model(inputs)
            loss = criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Statistics
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # Update progress bar
            pbar.set_postfix({
                'loss': running_loss / (pbar.n + 1),
                'acc': 100. * correct / total
            })
        
        epoch_loss = running_loss / len(self.train_loader)
        epoch_acc = 100. * correct / total
        
        return epoch_loss, epoch_acc
    
    def validate(self, criterion):
        """Validate the model"""
        self.model.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            pbar = tqdm(self.val_loader, desc='Validation')
            for inputs, labels in pbar:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                
                outputs = self.model.model(inputs)
                loss = criterion(outputs, labels)
                
                running_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
                
                pbar.set_postfix({
                    'loss': running_loss / (pbar.n + 1),
                    'acc': 100. * correct / total
                })
        
        epoch_loss = running_loss / len(self.val_loader)
        epoch_acc = 100. * correct / total
        
        return epoch_loss, epoch_acc
    
    def train(self, save_path='best_model.pth'):
        """
        Main training loop
        
        Args:
            save_path: Path to save best model
        """
        # ── Loss: label smoothing reduces overconfidence on noisy labels ──
        criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

        # ── Differential learning rates ────────────────────────────────────
        # Backbone (unfrozen layers) gets 10x lower LR than the classifier.
        # This prevents catastrophic forgetting of ImageNet features.
        backbone_params = [
            p for p in self.model.model.features[15:].parameters()
            if p.requires_grad
        ]
        classifier_params = list(self.model.model.classifier.parameters())

        optimizer = optim.AdamW(
            [
                {'params': classifier_params, 'lr': self.learning_rate},
                {'params': backbone_params,   'lr': self.learning_rate * 0.1},
            ],
            weight_decay=1e-4
        )

        # ── Cosine Annealing LR: smoothly decays LR each epoch ────────────
        scheduler = optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=self.num_epochs, eta_min=1e-6
        )
        
        best_val_acc = 0.0
        
        print("\n" + "="*60)
        print("Starting Training")
        print("="*60)
        
        for epoch in range(self.num_epochs):
            print(f"\nEpoch {epoch + 1}/{self.num_epochs}")
            print("-" * 60)
            
            # Train
            train_loss, train_acc = self.train_epoch(optimizer, criterion)
            
            # Validate
            val_loss, val_acc = self.validate(criterion)
            
            # Update scheduler (cosine annealing steps once per epoch)
            scheduler.step()
            
            # Save history
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            
            # Print summary
            current_lr = optimizer.param_groups[0]['lr']
            print(f"\nEpoch {epoch + 1} Summary:")
            print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
            print(f"  Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")
            print(f"  LR (classifier): {current_lr:.6f}")
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                self.model.save_model(save_path)
                print(f"  ✓ New best model saved! (Val Acc: {val_acc:.2f}%)")
        
        print("\n" + "="*60)
        print("Training Complete!")
        print("="*60)
        print(f"Best Validation Accuracy: {best_val_acc:.2f}%")
        print(f"Model saved to: {save_path}")
        
        # Save training history
        history_path = save_path.replace('.pth', '_history.json')
        with open(history_path, 'w') as f:
            json.dump(self.history, f, indent=2)
        print(f"Training history saved to: {history_path}")
        
        # Save class list
        classes_path = save_path.replace('.pth', '_classes.json')
        with open(classes_path, 'w') as f:
            json.dump(self.train_dataset.classes, f, indent=2)
        print(f"Classes list saved to: {classes_path}")
    
    def plot_history(self, save_path='training_history.png'):
        """Plot training history"""
        try:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
            
            # Loss plot
            ax1.plot(self.history['train_loss'], label='Train Loss')
            ax1.plot(self.history['val_loss'], label='Val Loss')
            ax1.set_xlabel('Epoch')
            ax1.set_ylabel('Loss')
            ax1.set_title('Training and Validation Loss')
            ax1.legend()
            ax1.grid(True)
            
            # Accuracy plot
            ax2.plot(self.history['train_acc'], label='Train Acc')
            ax2.plot(self.history['val_acc'], label='Val Acc')
            ax2.set_xlabel('Epoch')
            ax2.set_ylabel('Accuracy (%)')
            ax2.set_title('Training and Validation Accuracy')
            ax2.legend()
            ax2.grid(True)
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Training plots saved to: {save_path}")
            
        except ImportError:
            print("Matplotlib not installed. Skipping plot generation.")

# Example usage
if __name__ == "__main__":
    """
    Dataset structure expected:
    
    dataset/
    ├── train/
    │   ├── Apple___Apple_scab/
    │   │   ├── image1.jpg
    │   │   └── image2.jpg
    │   ├── Tomato___Early_blight/
    │   └── ...
    └── val/
        ├── Apple___Apple_scab/
        ├── Tomato___Early_blight/
        └── ...
    """
    
    # Configuration
    DATA_DIR = 'dataset'  # Change to your dataset path
    
    # Auto-detect number of classes from train directory
    train_dir = Path(DATA_DIR) / 'train'
    if train_dir.exists():
        detected_classes = [d.name for d in train_dir.iterdir() if d.is_dir()]
        NUM_CLASSES = len(detected_classes)
        print(f"Auto-detected {NUM_CLASSES} classes from {train_dir}")
    else:
        print(f"Warning: {train_dir} not found. Using default NUM_CLASSES=127")
        NUM_CLASSES = 127     # Fallback — matches all 29 datasets
    BATCH_SIZE = 128       # 8 GB VRAM on RTX 5050 — increase to 96/128 if memory allows
    LEARNING_RATE = 0.001  # Lower LR — AdamW + cosine scheduler handles decay
    NUM_EPOCHS = 20        # More epochs — model was still improving at epoch 10
    # Initialize trainer
    trainer = PlantDiseaseTrainer(
        data_dir=DATA_DIR,
        num_classes=NUM_CLASSES,
        batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        num_epochs=NUM_EPOCHS
    )
    
    # Load data
    trainer.load_data()
    
    # Train model
    trainer.train(save_path='best_plant_disease_model.pth')
    
    # Plot training history
    trainer.plot_history()
