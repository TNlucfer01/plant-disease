"""
Plant Disease Detection CNN Model
Uses MobileNetV2 with transfer learning
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import json

class PlantDiseaseCNN:
    def __init__(self, num_classes=127, confidence_threshold=0.7):
        """
        Initialize the CNN model

        Args:
            num_classes: Number of disease classes
                         (default 127 — covers all 29 downloaded datasets,
                          normalised to PlantName_DiseaseName format)
            confidence_threshold: Minimum confidence to return prediction
        """
        self.num_classes = num_classes
        self.confidence_threshold = confidence_threshold
        # why cudo and what does it do 
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load pretrained MobileNetV2 (ImageNet weights)
        from torchvision.models import MobileNet_V2_Weights 
        # why use this network know more bout this network 

         # why do i ;oad this particular wieghts and is there any other weights there 
        self.model = models.mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)

        # Step 1: Freeze ALL backbone layers first
        # what does this do 
        for param in self.model.parameters():
            param.requires_grad = False

# what does this do 
        # Step 2: Unfreeze last 3 inverted-residual blocks (features[15..18])
        # This lets the backbone learn disease-specific textures/patterns
        for layer in self.model.features[15:]:
            for param in layer.parameters():
                param.requires_grad = True


# what is this and why do we do this 
        # Step 3: Replace classifier with a wider 2-layer head
        # 1280 -> 512 -> num_classes  (more capacity for 114 classes)
        self.model.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(1280, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(512, num_classes)
        )
        # Classifier parameters are already trainable (new layer)
# what does this line do 
        self.model = self.model.to(self.device)
        # how are we eva;uting 
        self.model.eval()
        
        # Image preprocessing (MobileNetV2 expects 224x224)  and what does this do 
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],  # ImageNet means
                std=[0.229, 0.224, 0.225]     # ImageNet stds
            )
        ])
        
        # Disease class names (example - replace with your actual classes) what does this do 
        self.class_names = self._get_class_names()
    
    def _get_class_names(self):
        """
        Define your disease classes here.
        Attempts to load dynamically from `best_plant_disease_model_classes.json`
        if it exists. Otherwise returns the default 127 standardised classes.
        """
        import os
        import json
        
        # Try finding dynamically generated classes file
        classes_file = 'best_plant_disease_model_classes.json'
        if os.path.exists(classes_file):
            try:
                with open(classes_file, 'r') as f:
                    classes = json.load(f)
                if len(classes) == self.num_classes:
                    return classes
                else:
                    print(f"Warning: {classes_file} has {len(classes)} classes, but model num_classes={self.num_classes}")
            except Exception as e:
                print(f"Error loading {classes_file}: {e}")
                
        # Default fallback — 127 classes across all 29 datasets,
        # standardised to PlantName_DiseaseName format.
        return [
            # Apple (4)
            'Apple_Apple_Scab',
            'Apple_Black_Rot',
            'Apple_Cedar_Apple_Rust',
            'Apple_Healthy',
            # Banana (3)
            'Banana_Cordana',
            'Banana_Healthy',
            'Banana_Pestalotiopsis',
            'Banana_Sigatoka',
            # Blueberry (1)
            'Blueberry_Healthy',
            # Cassava (5)
            'Cassava_Bacterial_Blight',
            'Cassava_Brown_Streak',
            'Cassava_Green_Mite',
            'Cassava_Healthy',
            'Cassava_Mosaic',
            # Cherry (2)
            'Cherry_Healthy',
            'Cherry_Powdery_Mildew',
            # Coconut (5)
            'Coconut_Caterpillars',
            'Coconut_Drying_Of_Leaflets',
            'Coconut_Flaccidity',
            'Coconut_Healthy',
            'Coconut_Yellowing',
            # Corn (4)
            'Corn_Common_Rust',
            'Corn_Gray_Leaf_Spot',
            'Corn_Healthy',
            'Corn_Northern_Leaf_Blight',
            # Cotton (9)
            'Cotton_Aphids',
            'Cotton_Army_Worm',
            'Cotton_Bacterial_Blight',
            'Cotton_Curl_Virus',
            'Cotton_Disease',
            'Cotton_Fusarium_Wilt',
            'Cotton_Healthy',
            'Cotton_Insect_Pest',
            'Cotton_Powdery_Mildew',
            'Cotton_Small_Leaf',
            'Cotton_Target_Spot',
            'Cotton_White_Mold',
            'Cotton_Wilt',
            # Eggplant (7)
            'Eggplant_Healthy',
            'Eggplant_Insect_Pest',
            'Eggplant_Leaf_Spot',
            'Eggplant_Mosaic_Virus',
            'Eggplant_Small_Leaf',
            'Eggplant_White_Mold',
            'Eggplant_Wilt',
            # Grape (4)
            'Grape_Black_Rot',
            'Grape_Esca_Black_Measles',
            'Grape_Healthy',
            'Grape_Leaf_Blight',
            # Groundnut (6)
            'Groundnut_Early_Leaf_Spot',
            'Groundnut_Early_Rust',
            'Groundnut_Healthy',
            'Groundnut_Late_Leaf_Spot',
            'Groundnut_Nutrition_Deficiency',
            'Groundnut_Rust',
            # Mango (8)
            'Mango_Anthracnose',
            'Mango_Bacterial_Canker',
            'Mango_Cutting_Weevil',
            'Mango_Die_Back',
            'Mango_Gall_Midge',
            'Mango_Healthy',
            'Mango_Powdery_Mildew',
            'Mango_Sooty_Mould',
            # Okra (2)
            'Okra_Healthy',
            'Okra_Yellow_Vein_Mosaic',
            # Onion (4)
            'Onion_Anthracnose',
            'Onion_Healthy',
            'Onion_Purple_Blotch',
            'Onion_Stemphylium_Blight',
            # Orange (1)
            'Orange_Citrus_Greening',
            # Paddy (8)
            'Paddy_Bacterial_Leaf_Blight',
            'Paddy_Bacterial_Leaf_Streak',
            'Paddy_Bacterial_Panicle_Blight',
            'Paddy_Blast',
            'Paddy_Brown_Spot',
            'Paddy_Dead_Heart',
            'Paddy_Downy_Mildew',
            'Paddy_Healthy',
            'Paddy_Hispa',
            'Paddy_Tungro',
            # Peach (2)
            'Peach_Bacterial_Spot',
            'Peach_Healthy',
            # Peanut (2)
            'Peanut_Dead_Leaf',
            'Peanut_Healthy',
            # Pepper (2)
            'Pepper_Bacterial_Spot',
            'Pepper_Healthy',
            # Potato (3)
            'Potato_Early_Blight',
            'Potato_Healthy',
            'Potato_Late_Blight',
            # Raspberry (1)
            'Raspberry_Healthy',
            # Rice (8)
            'Rice_Bacterial_Leaf_Blight',
            'Rice_Brown_Spot',
            'Rice_Healthy',
            'Rice_Hispa',
            'Rice_Leaf_Blast',
            'Rice_Leaf_Scald',
            'Rice_Leaf_Smut',
            'Rice_Sheath_Blight',
            # Sorghum (6)
            'Sorghum_Anthracnose_Red_Rot',
            'Sorghum_Covered_Kernel_Smut',
            'Sorghum_Grain_Mold',
            'Sorghum_Head_Smut',
            'Sorghum_Loose_Smut',
            'Sorghum_Rust',
            # Soybean (1)
            'Soybean_Healthy',
            # Squash (1)
            'Squash_Powdery_Mildew',
            # Strawberry (2)
            'Strawberry_Healthy',
            'Strawberry_Leaf_Scorch',
            # Sugarcane (7)
            'Sugarcane_Bacterial_Blight',
            'Sugarcane_Healthy',
            'Sugarcane_Mosaic',
            'Sugarcane_Red_Rot',
            'Sugarcane_Rust',
            'Sugarcane_Yellow',
            # Tea (10)
            'Tea_Algal_Leaf',
            'Tea_Anthracnose',
            'Tea_Bird_Eye_Spot',
            'Tea_Brown_Blight',
            'Tea_Gray_Blight',
            'Tea_Green_Mirid_Bug',
            'Tea_Healthy',
            'Tea_Helopeltis',
            'Tea_Red_Leaf_Spot',
            'Tea_Red_Spider',
            'Tea_White_Spot',
            # Tomato (10)
            'Tomato_Bacterial_Spot',
            'Tomato_Early_Blight',
            'Tomato_Healthy',
            'Tomato_Late_Blight',
            'Tomato_Leaf_Mold',
            'Tomato_Mosaic_Virus',
            'Tomato_Septoria_Leaf_Spot',
            'Tomato_Spider_Mites',
            'Tomato_Target_Spot',
            'Tomato_Yellow_Leaf_Curl_Virus',
        ]
    
    def predict(self, image_path): # learn this things 
        """
        Make prediction on a single image.

        Returns 'Unknown' for plant and disease when the model is not
        confident enough — this happens when the image shows a plant or
        disease the model has never been trained on.

        Args:
            image_path: Path to the image file

        Returns:
            dict with keys:
                plant        – plant name, or 'Unknown'
                disease      – disease name, or 'Unknown'
                confidence   – top class probability (0–1)
                is_confident – True if confidence >= threshold
                is_unknown   – True if the input looks unfamiliar
                raw_class    – raw class string (or 'Unknown')
                top_5        – list of top-5 predictions
                all_probabilities – full softmax vector
        """
        import numpy as np

        # ── load & preprocess ──────────────────────────────────────────────  what does thi do 
        image = Image.open(image_path).convert('RGB')
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # ── forward pass ───────────────────────────────────────────────────
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            probabilities = probabilities.cpu().numpy()[0]

        # ── top prediction ─────────────────────────────────────────────────
        predicted_idx = int(probabilities.argmax())
        confidence    = float(probabilities[predicted_idx])

        # ── Unknown detection ──────────────────────────────────────────────
        # 1. Low confidence: the best guess is still weak
        low_confidence = confidence < self.confidence_threshold
 
        # 2. High entropy: probability is spread evenly across many classes
        #    (another sign the model has no idea what it's looking at)
        entropy = float(-np.sum(probabilities * np.log(probabilities + 1e-9)))
        max_entropy = float(np.log(len(probabilities)))      # entropy if uniform
        high_entropy = entropy > 0.75 * max_entropy          # >75% of max = confused

        is_unknown = low_confidence or high_entropy

        if is_unknown:
            plant_name  = 'Unknown'
            disease     = 'Unknown'
            disease_name = 'Unknown'
        else:
            disease_name = self.class_names[predicted_idx]
            plant_name, disease = self._parse_disease_name(disease_name)

        # ── top-5 predictions (always useful for debugging) ────────────────
        top_5 = self._get_top_k(probabilities, k=5)

        return {
            'plant':             plant_name,
            'disease':           disease,
            'confidence':        confidence,
            'is_confident':      not is_unknown,
            'is_unknown':        is_unknown,
            'unknown_reason':    ('low_confidence' if low_confidence else
                                  'high_entropy'   if high_entropy   else None),
            'raw_class':         disease_name,
            'top_5':             top_5,
            'all_probabilities': probabilities.tolist(),
        }
    
    def _parse_disease_name(self, class_name):
        """
        Parse class name into (plant, disease) tuple.

        Handles two formats:
          • New standard:  'Tomato_Early_Blight'  (PlantName_DiseaseName)
          • Legacy PV:     'Tomato___Early_blight' (PlantVillage triple-underscore)
        """
        # Legacy PlantVillage format
        if '___' in class_name:
            parts = class_name.split('___')
            plant = parts[0].replace('_', ' ')
            disease = parts[1].replace('_', ' ')
            return plant, disease

        # New PlantName_DiseaseName format (split on first underscore only)
        if '_' in class_name:
            idx = class_name.index('_')
            plant = class_name[:idx].replace('_', ' ')
            disease = class_name[idx + 1:].replace('_', ' ')
            return plant, disease

        return class_name, 'Unknown'
    
    def _get_top_k(self, probabilities, k=5):
        """
        Get top-k predictions
        """
        top_k_indices = probabilities.argsort()[-k:][::-1]
        top_k_results = []
        
        for idx in top_k_indices:
            plant, disease = self._parse_disease_name(self.class_names[idx])
            top_k_results.append({
                'plant': plant,
                'disease': disease,
                'confidence': float(probabilities[idx]),
                'raw_class': self.class_names[idx]
            })
        
        return top_k_results
    def save_model(self, path='plant_disease_model.pth'):
        """Save model weights"""
        torch.save(self.model.state_dict(), path)
        print(f"Model saved to {path}")
    def load_model(self, path='plant_disease_model.pth'):
        """Load model weights and automatically load class names if they exist"""
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.model.eval()
        print(f"Model loaded from {path}")
        
        # Try loading classes automatically alongside the weights
        classes_path = path.replace('.pth', '_classes.json')
        import os, json
        if os.path.exists(classes_path):
            try:
                with open(classes_path, 'r') as f:
                    self.class_names = json.load(f)
                self.num_classes = len(self.class_names)
                print(f"Auto-loaded {self.num_classes} classes from {classes_path}")
            except Exception as e:
                print(f"Could not load classes from {classes_path}: {e}")

    
    def get_model_summary(self):
        """Print model architecture summary"""
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        print("=" * 60)
        print("Plant Disease Detection CNN - MobileNetV2")
        print("=" * 60)
        print(f"Device: {self.device}")
        print(f"Total parameters: {total_params:,}")
        print(f"Trainable parameters: {trainable_params:,}")
        print(f"Frozen parameters: {total_params - trainable_params:,}")
        print(f"Number of classes: {self.num_classes}")
        print(f"Confidence threshold: {self.confidence_threshold}")
        print("=" * 60)


# Example usage
if __name__ == "__main__":
    # Initialize model
    model = PlantDiseaseCNN(num_classes=127, confidence_threshold=0.7)
    model.load_model('best_plant_disease_model.pth')


    # Print summary
    model.get_model_summary()
    
    # Example prediction (uncomment when you have an image)
    # result = model.predict('path/to/leaf_image.jpg')
    # print(json.dumps(result, indent=2))
