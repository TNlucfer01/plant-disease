"""
Quick test to check model configuration
"""
from plant_disease_cnn import PlantDiseaseCNN
import torch

print("="*70)
print("MODEL CONFIGURATION TEST")
print("="*70)

# Initialize model
print("\n1. Creating model with 38 classes...")
model = PlantDiseaseCNN(num_classes=38, confidence_threshold=0.7)

print(f"   ✅ Model initialized successfully")
print(f"   Number of classes: {model.num_classes}")
print(f"   Total class names: {len(model.class_names)}")

# Check model weights
print("\n2. Checking model file...")
try:
    state_dict = torch.load('best_plant_disease_model.pth', map_location=model.device)
    print(f"   ✅ Model file loaded")
    
    # Check classifier layer size
    if 'classifier.1.weight' in state_dict:
        classifier_shape = state_dict['classifier.1.weight'].shape
        print(f"   Classifier output shape: {classifier_shape}")
        print(f"   Expected shape: torch.Size([38, 1280])")
        
        if classifier_shape[0] == 38:
            print(f"   ✅ Model was trained for 38 classes - MATCHES!")
        else:
            print(f"   ❌ Model was trained for {classifier_shape[0]} classes - MISMATCH!")
            print(f"\n   This model cannot be used for validation without retraining.")
    
except Exception as e:
    print(f"   ❌ Error loading model: {e}")

print("\n3. Class names in model:")
for i, name in enumerate(model.class_names):
    print(f"   {i+1:2d}. {name}")

print("\n" + "="*70)
