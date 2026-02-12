"""
Diagnose prediction issues
"""
from plant_disease_cnn import PlantDiseaseCNN
import os

# Load model
print("Loading model...")
model = PlantDiseaseCNN(num_classes=38, confidence_threshold=0.7)
model.load_model('best_plant_disease_model.pth')

print("\n" + "="*70)
print("MODEL CLASS NAMES (38 classes the model was trained on):")
print("="*70)
for i, name in enumerate(model.class_names):
    print(f"{i:2d}. {name}")

print("\n" + "="*70)
print("DIAGNOSIS:")
print("="*70)
print("\nYour model was trained on 38 classes (without Paddy and SugarCane).")
print("\nIf you are seeing wrong predictions:")
print("1. Make sure you're NOT testing on Paddy or SugarCane images")
print("   (model doesn't know these classes)")
print("")
print("2. Check if the image quality is good")
print("   (blurry/dark images can confuse the model)")
print("")
print("3. The bar chart shows Cherry and Tomato both have 100% accuracy")
print("   in the test, so the model should work correctly for these.")
print("")
print("To test a specific image, use:")
print("  python -c \"from plant_disease_cnn import PlantDiseaseCNN; ")
print("  m=PlantDiseaseCNN(38); m.load_model('best_plant_disease_model.pth');")
print("  print(m.predict('your_image.jpg'))\"")
print("="*70)
