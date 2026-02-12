import torch
import sys

# Load and inspect the model
try:
    print("Loading model file...")
    state_dict = torch.load('best_plant_disease_model.pth', map_location='cpu')
    
    print("\nModel state dict keys:")
    print("="*70)
    
    for key in state_dict.keys():
        shape = state_dict[key].shape if hasattr(state_dict[key], 'shape') else 'N/A'
        print(f"{key:50s} {str(shape):30s}")
    
    print("\n" + "="*70)
    
    # Check classifier output layer
    if 'classifier.1.weight' in state_dict:
        num_classes = state_dict['classifier.1.weight'].shape[0]
        print(f"\n✅ Model was trained for {num_classes} classes")
    elif 'classifier.weight' in state_dict:
        num_classes = state_dict['classifier.weight'].shape[0]
        print(f"\n✅ Model was trained for {num_classes} classes")
    else:
        print("\n❌ Could not find classifier layer")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
