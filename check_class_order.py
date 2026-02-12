"""
Check class order mismatch between dataset and code  
"""
import os
from plant_disease_cnn import PlantDiseaseCNN

# Get alphabetical order from dataset (how PyTorch ImageFolder sorts)
dataset_path = 'dataset/train'
dataset_classes = sorted([f for f in os.listdir(dataset_path) 
                         if os.path.isdir(os.path.join(dataset_path, f))])

# Get class order from code
model = PlantDiseaseCNN(num_classes=38)
code_classes = model.class_names

print("="*70)
print("CLASS ORDER COMPARISON")
print("="*70)

print(f"\nDataset has {len(dataset_classes)} classes")
print(f"Code has {len(code_classes)} classes")

# Only compare the 38 classes that match
matching_dataset_classes = [c for c in dataset_classes if c in code_classes]

print(f"\nMatching classes: {len(matching_dataset_classes)}")

mismatches = 0
for i in range(min(len(matching_dataset_classes), len(code_classes))):
    dataset_class = matching_dataset_classes[i] if i < len(matching_dataset_classes) else "N/A"
    code_class = code_classes[i]
    
    if dataset_class != code_class:
        mismatches += 1

print(f"\nMismatches found: {mismatches} out of {len(code_classes)}")

if mismatches > 0:
    print("\n*** PROBLEM FOUND ***")
    print("The model was trained with alphabetical order,")
    print("but code uses different order.")
    print("This is why predictions are wrong!\n")
    
    print("\n" + "="*70)
    print("CORRECT CLASS ORDER (Alphabetically Sorted):")
    print("="*70)
    for i, cls in enumerate(matching_dataset_classes):
        print(f"            '{cls}',")
else:
    print("\nAll classes match! Order is correct.")
