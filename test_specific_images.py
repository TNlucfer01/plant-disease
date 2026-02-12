"""
Test specific images to debug misclassification
"""
from plant_disease_cnn import PlantDiseaseCNN
import os
import glob

# Load model
print("Loading model...")
model = PlantDiseaseCNN(num_classes=38, confidence_threshold=0.7)
model.load_model('best_plant_disease_model.pth')

print("\n" + "="*70)
print("TESTING SPECIFIC IMAGES")
print("="*70)

# Test cherry images
cherry_dir = "dataset/val/Cherry_(including_sour)___healthy"
if os.path.exists(cherry_dir):
    cherry_images = glob.glob(os.path.join(cherry_dir, "*.jpg")) + glob.glob(os.path.join(cherry_dir, "*.JPG"))
    if cherry_images:
        test_image = cherry_images[0]
        print(f"\nTesting Cherry Image: {os.path.basename(test_image)}")
        print(f"Expected: Cherry_(including_sour)___healthy")
        result = model.predict(test_image)
        print(f"Predicted: {result['raw_class']}")
        print(f"Confidence: {result['confidence']*100:.2f}%")
        print(f"Match: {'YES' if 'Cherry' in result['raw_class'] else 'NO - WRONG!'}")

# Test tomato images
tomato_dir = "dataset/val/Tomato___healthy"
if os.path.exists(tomato_dir):
    tomato_images = glob.glob(os.path.join(tomato_dir, "*.jpg")) + glob.glob(os.path.join(tomato_dir, "*.JPG"))
    if tomato_images:
        test_image = tomato_images[0]
        print(f"\nTesting Tomato Image: {os.path.basename(test_image)}")
        print(f"Expected: Tomato___healthy")
        result = model.predict(test_image)
        print(f"Predicted: {result['raw_class']}")
        print(f"Confidence: {result['confidence']*100:.2f}%")
        print(f"Match: {'YES' if 'Tomato' in result['raw_class'] else 'NO - WRONG!'}")
print("\n" + "="*70)
print("CLASS NAMES IN MODEL (in order):")
print("="*70)
for i, name in enumerate(model.class_names):
    print(f"{i:2d}. {name}")
