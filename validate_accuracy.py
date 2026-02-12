"""
Model Validation & Accuracy Testing Program
Validates the trained plant disease detection model on the validation dataset
"""

import torch
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
from plant_disease_cnn import PlantDiseaseCNN
import os
from tqdm import tqdm
import json

class ModelValidator:
    def __init__(self, model_path='best_plant_disease_model.pth', dataset_path='dataset/val'):
        """
        Initialize the validator
        
        Args:
            model_path: Path to the trained model weights
            dataset_path: Path to validation dataset
        """
        self.model_path = model_path
        self.dataset_path = dataset_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize model
        print("Loading model...")
        self.model = PlantDiseaseCNN(num_classes=38, confidence_threshold=0.7)
        
        # Try to load model weights
        try:
            self.model.load_model(model_path)
            self.model.model.eval()
            print("✅ Model weights loaded successfully")
        except RuntimeError as e:
            if "size mismatch" in str(e):
                print(f"\n⚠️  WARNING: Saved model has different number of classes!")
                print(f"   Saved model appears to have a different architecture.")
                print(f"   Current model: 38 classes")
                print(f"   You need to train a new model with 38 classes first.")
                print(f"\n❌ Cannot validate without a trained model. Please run train.py first.\n")
                raise ValueError("Model architecture mismatch - training required")
            else:
                raise
        
        # Load validation dataset
        print("Loading validation dataset...")
        self.val_loader, self.class_names = self._load_dataset()
        
    def _load_dataset(self):
        """Load validation dataset"""
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        val_dataset = datasets.ImageFolder(self.dataset_path, transform=transform)
        
        # Get class names from model (38 classes)
        model_class_names = self.model.class_names
        dataset_class_names = val_dataset.classes
        
        print(f"Model supports {len(model_class_names)} classes")
        print(f"Dataset contains {len(dataset_class_names)} classes")
        
        # Filter dataset to only include classes that the model supports
        # Create a mapping from dataset class index to model class index
        class_mapping = {}
        skipped_classes = []
        
        for dataset_idx, dataset_class in enumerate(dataset_class_names):
            if dataset_class in model_class_names:
                model_idx = model_class_names.index(dataset_class)
                class_mapping[dataset_idx] = model_idx
            else:
                skipped_classes.append(dataset_class)
        
        if skipped_classes:
            print(f"\n⚠️  Skipping {len(skipped_classes)} classes not in the model:")
            for cls in skipped_classes:
                print(f"   - {cls}")
        
        # Filter the dataset samples
        filtered_samples = []
        for path, label in val_dataset.samples:
            if label in class_mapping:
                # Remap the label to the model's class index
                new_label = class_mapping[label]
                filtered_samples.append((path, new_label))
        
        val_dataset.samples = filtered_samples
        val_dataset.targets = [s[1] for s in filtered_samples]
        
        val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=2)
        
        print(f"\n✅ Loaded {len(val_dataset)} validation images for testing")
        print(f"✅ Testing on {len(model_class_names)} classes\n")
        
        return val_loader, model_class_names
    
    def validate(self):
        """
        Run validation on the entire validation dataset
        
        Returns:
            dict: Validation results with metrics
        """
        all_preds = []
        all_labels = []
        all_probs = []
        
        print("\nRunning validation...")
        with torch.no_grad():
            for images, labels in tqdm(self.val_loader, desc="Validating"):
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                # Get predictions
                outputs = self.model.model(images)
                probabilities = F.softmax(outputs, dim=1)
                _, predicted = torch.max(outputs, 1)
                
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                all_probs.extend(probabilities.cpu().numpy())
        
        # Convert to numpy arrays
        all_preds = np.array(all_preds)
        all_labels = np.array(all_labels)
        all_probs = np.array(all_probs)
        
        # Calculate metrics
        results = self._calculate_metrics(all_labels, all_preds, all_probs)
        
        return results, all_labels, all_preds
    
    def _calculate_metrics(self, labels, preds, probs):
        """Calculate accuracy metrics"""
        # Overall accuracy
        accuracy = accuracy_score(labels, preds)
        
        # Per-class accuracy
        per_class_accuracy = {}
        for i, class_name in enumerate(self.class_names):
            mask = labels == i
            if mask.sum() > 0:
                class_acc = (preds[mask] == labels[mask]).sum() / mask.sum()
                per_class_accuracy[class_name] = float(class_acc)
        
        # Average confidence
        max_probs = probs.max(axis=1)
        avg_confidence = max_probs.mean()
        
        results = {
            'overall_accuracy': float(accuracy),
            'average_confidence': float(avg_confidence),
            'per_class_accuracy': per_class_accuracy,
            'total_samples': len(labels)
        }
        
        return results
    
    def print_results(self, results):
        """Print validation results in a nice format"""
        print("\n" + "="*70)
        print("MODEL VALIDATION RESULTS")
        print("="*70)
        print(f"Total Samples: {results['total_samples']}")
        print(f"Overall Accuracy: {results['overall_accuracy']*100:.2f}%")
        print(f"Average Confidence: {results['average_confidence']*100:.2f}%")
        print("="*70)
        
        print("\nPER-CLASS ACCURACY:")
        print("-"*70)
        
        # Sort by accuracy
        sorted_classes = sorted(
            results['per_class_accuracy'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for class_name, acc in sorted_classes:
            plant, disease = self._parse_class_name(class_name)
            print(f"{plant:20s} | {disease:30s} | {acc*100:6.2f}%")
        
        print("-"*70)
        
        # Show best and worst performing classes
        print(f"\n✅ BEST: {sorted_classes[0][0]} ({sorted_classes[0][1]*100:.2f}%)")
        print(f"❌ WORST: {sorted_classes[-1][0]} ({sorted_classes[-1][1]*100:.2f}%)")
    
    def _parse_class_name(self, class_name):
        """Parse class name into plant and disease"""
        parts = class_name.split('___')
        if len(parts) == 2:
            return parts[0], parts[1]
        return class_name, ''
    
    def generate_classification_report(self, labels, preds):
        """Generate detailed classification report"""
        print("\n" + "="*70)
        print("DETAILED CLASSIFICATION REPORT")
        print("="*70)
        
        report = classification_report(
            labels, 
            preds, 
            target_names=self.class_names,
            digits=4,
            zero_division=0
        )
        
        print(report)
        
        return report
    
    def plot_confusion_matrix(self, labels, preds, save_path='confusion_matrix.png'):
        """Generate and save confusion matrix plot"""
        print(f"\nGenerating confusion matrix...")
        
        # Calculate confusion matrix
        cm = confusion_matrix(labels, preds)
        
        # Create figure
        plt.figure(figsize=(20, 18))
        
        # Plot with seaborn
        sns.heatmap(
            cm, 
            annot=False,  # Too many classes for annotations
            fmt='d',
            cmap='Blues',
            xticklabels=self.class_names,
            yticklabels=self.class_names,
            cbar_kws={'label': 'Number of Predictions'}
        )
        
        plt.title('Confusion Matrix - Plant Disease Classification', fontsize=16, pad=20)
        plt.xlabel('Predicted Class', fontsize=12)
        plt.ylabel('True Class', fontsize=12)
        plt.xticks(rotation=90, fontsize=8)
        plt.yticks(rotation=0, fontsize=8)
        plt.tight_layout()
        
        # Save figure
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Confusion matrix saved to: {save_path}")
        
        plt.close()
    
    def plot_accuracy_distribution(self, results, save_path='accuracy_distribution.png'):
        """Plot per-class accuracy distribution"""
        print(f"\nGenerating accuracy distribution plot...")
        
        classes = list(results['per_class_accuracy'].keys())
        accuracies = [results['per_class_accuracy'][c] * 100 for c in classes]
        
        # Sort by accuracy
        sorted_indices = np.argsort(accuracies)
        classes = [classes[i] for i in sorted_indices]
        accuracies = [accuracies[i] for i in sorted_indices]
        
        # Create figure
        plt.figure(figsize=(14, 10))
        
        # Create horizontal bar chart
        colors = ['#d32f2f' if acc < 70 else '#ff9800' if acc < 85 else '#4caf50' 
                  for acc in accuracies]
        
        plt.barh(range(len(classes)), accuracies, color=colors, alpha=0.8)
        plt.yticks(range(len(classes)), classes, fontsize=8)
        plt.xlabel('Accuracy (%)', fontsize=12)
        plt.title('Per-Class Accuracy Distribution', fontsize=16, pad=20)
        plt.axvline(x=results['overall_accuracy']*100, color='blue', 
                   linestyle='--', linewidth=2, label=f"Overall Accuracy ({results['overall_accuracy']*100:.2f}%)")
        plt.legend()
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        # Save figure
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Accuracy distribution saved to: {save_path}")
        
        plt.close()
    
    def save_results(self, results, save_path='validation_results.json'):
        """Save validation results to JSON file"""
        with open(save_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {save_path}")


def main():
    """Main function to run validation"""
    print("="*70)
    print("PLANT DISEASE MODEL VALIDATION")
    print("="*70)
    
    # Check if model exists
    if not os.path.exists('best_plant_disease_model.pth'):
        print("\n❌ Error: Model file 'best_plant_disease_model.pth' not found!")
        print("Please train the model first using train.py")
        return
    
    # Check if validation dataset exists
    if not os.path.exists('dataset/val'):
        print("\n❌ Error: Validation dataset not found at 'dataset/val'!")
        print("Please ensure the dataset is properly set up.")
        return
    
    # Initialize validator
    validator = ModelValidator(
        model_path='best_plant_disease_model.pth',
        dataset_path='dataset/val'
    )
    
    # Run validation
    results, all_labels, all_preds = validator.validate()
    
    # Print results
    validator.print_results(results)
    
    # Generate classification report
    validator.generate_classification_report(all_labels, all_preds)
    
    # Generate visualizations
    validator.plot_confusion_matrix(all_labels, all_preds)
    validator.plot_accuracy_distribution(results)
    
    # Save results
    validator.save_results(results)
    
    print("\n" + "="*70)
    print("✅ Validation Complete!")
    print("="*70)
    print("\nGenerated files:")
    print("  - validation_results.json")
    print("  - confusion_matrix.png")
    print("  - accuracy_distribution.png")
    print("="*70)


if __name__ == "__main__":
    main()
