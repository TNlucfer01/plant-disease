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
    def __init__(self, num_classes=38, confidence_threshold=0.7):
        """
        Initialize the CNN model
        
        Args:
            num_classes: Number of disease classes (default 38 for PlantVillage dataset)
            confidence_threshold: Minimum confidence to return prediction
        """
        self.num_classes = num_classes
        self.confidence_threshold = confidence_threshold
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load pretrained MobileNetV2
        self.model = models.mobilenet_v2(pretrained=True)
        
        # Freeze backbone (all layers except classifier)
        for param in self.model.parameters():
            param.requires_grad = False
        
        # Replace classifier for your disease classes
        # MobileNetV2 has a classifier with 1280 input features
        self.model.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(1280, num_classes)
        )
        
        # Unfreeze only the new classifier
        for param in self.model.classifier.parameters():
            param.requires_grad = True
        
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Image preprocessing (MobileNetV2 expects 224x224)
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],  # ImageNet means
                std=[0.229, 0.224, 0.225]     # ImageNet stds
            )
        ])
        
        # Disease class names (example - replace with your actual classes)
        self.class_names = self._get_class_names()
    
    def _get_class_names(self):
        """
        Define your disease classes here
        This is a sample - replace with your actual classes
        """
        return [
            'Apple___Apple_scab',
            'Apple___Black_rot',
            'Apple___Cedar_apple_rust',
            'Apple___healthy',
            'Tomato___Bacterial_spot',
            'Tomato___Early_blight',
            'Tomato___Late_blight',
            'Tomato___Leaf_Mold',
            'Tomato___Septoria_leaf_spot',
            'Tomato___Spider_mites',
            'Tomato___Target_Spot',
            'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
            'Tomato___Tomato_mosaic_virus',
            'Tomato___healthy',
            'Potato___Early_blight',
            'Potato___Late_blight',
            'Potato___healthy',
            'Corn___Common_rust',
            'Corn___Northern_Leaf_Blight',
            'Corn___healthy',
            'Grape___Black_rot',
            'Grape___Esca',
            'Grape___Leaf_blight',
            'Grape___healthy',
            'Pepper___Bacterial_spot',
            'Pepper___healthy',
            'Strawberry___Leaf_scorch',
            'Strawberry___healthy',
            'Cherry___Powdery_mildew',
            'Cherry___healthy',
            'Peach___Bacterial_spot',
            'Peach___healthy',
            'Blueberry___healthy',
            'Raspberry___healthy',
            'Soybean___healthy',
            'Squash___Powdery_mildew',
            'Orange___Haunglongbing',
            'Cotton___diseased'
        ]
    
    def predict(self, image_path):
        """
        Make prediction on a single image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            dict: Prediction results with disease, confidence, all probabilities
        """
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            probabilities = probabilities.cpu().numpy()[0]
        
        # Get top prediction
        predicted_idx = probabilities.argmax()
        confidence = float(probabilities[predicted_idx])
        disease_name = self.class_names[predicted_idx]
        
        # Parse disease name
        plant_name, disease = self._parse_disease_name(disease_name)
        
        # Create result dictionary
        result = {
            'plant': plant_name,
            'disease': disease,
            'confidence': confidence,
            'is_confident': confidence >= self.confidence_threshold,
            'raw_class': disease_name,
            'all_probabilities': probabilities.tolist(),
            'top_5': self._get_top_k(probabilities, k=5)
        }
        
        return result
    
    def _parse_disease_name(self, class_name):
        """
        Parse class name like 'Tomato___Early_blight' into plant and disease
        """
        parts = class_name.split('___')
        if len(parts) == 2:
            plant = parts[0].replace('_', ' ')
            disease = parts[1].replace('_', ' ')
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
        """Load model weights"""
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.model.eval()
        print(f"Model loaded from {path}")
    
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
    model = PlantDiseaseCNN(num_classes=38, confidence_threshold=0.7)
    
    # Print summary
    model.get_model_summary()
    
    # Example prediction (uncomment when you have an image)
    # result = model.predict('path/to/leaf_image.jpg')
    # print(json.dumps(result, indent=2))
