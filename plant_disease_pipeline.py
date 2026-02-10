"""
Complete Pipeline: CNN → LLM
Connects disease detection to treatment advice
"""

import json
from pathlib import Path
from plant_disease_cnn import PlantDiseaseCNN
from plant_disease_llm import PlantDiseaseLLM

class PlantDiseaseAssistant:
    def __init__(self, 
                 num_classes=38, 
                 confidence_threshold=0.7,
                 llm_model="llama3.2:3b"):
        """
        Initialize the complete pipeline
        
        Args:
            num_classes: Number of disease classes
            confidence_threshold: Minimum confidence for diagnosis
            llm_model: Ollama model name
        """
        print("Initializing Plant Disease Assistant...")
        
        # Initialize CNN
        print("Loading CNN model (MobileNetV2)...")
        self.cnn = PlantDiseaseCNN(
            num_classes=num_classes,
            confidence_threshold=confidence_threshold
        )
        
        # Initialize LLM
        print("Connecting to LLM (Ollama)...")
        self.llm = PlantDiseaseLLM(model_name=llm_model)
        
        # Check LLM connection
        if self.llm.test_connection():
            print("✓ Ollama connected successfully")
        else:
            print("⚠️  Ollama not running - will use fallback advice")
        
        print("Assistant ready!\n")
    
    def analyze(self, image_path, verbose=True):
        """
        Complete analysis pipeline: Image → Detection → Advice
        
        Args:
            image_path: Path to leaf image
            verbose: Print intermediate steps
            
        Returns:
            dict: Complete analysis with detection and advice
        """
        if verbose:
            print(f"Analyzing: {image_path}")
            print("-" * 60)
        
        # Step 1: CNN Detection
        if verbose:
            print("Step 1: Running disease detection...")
        
        prediction = self.cnn.predict(image_path)
        
        if verbose:
            print(f"  Plant: {prediction['plant']}")
            print(f"  Disease: {prediction['disease']}")
            print(f"  Confidence: {prediction['confidence']:.1%}")
            print(f"  Status: {'CONFIDENT' if prediction['is_confident'] else 'UNCERTAIN'}")
            print()
        
        # Step 2: LLM Advice Generation
        if verbose:
            print("Step 2: Generating treatment advice...")
        
        advice = self.llm.get_advice(prediction)
        
        if verbose:
            if advice['success']:
                print("  ✓ Advice generated successfully")
            else:
                print(f"  ⚠️  Using fallback: {advice.get('error', 'Unknown error')}")
            print()
        
        # Combine results
        complete_result = {
            'detection': prediction,
            'advice': advice,
            'image_path': str(image_path)
        }
        
        return complete_result
    
    def analyze_and_display(self, image_path):
        """
        Analyze image and display formatted results
        """
        result = self.analyze(image_path, verbose=True)
        
        print("=" * 60)
        print("DETECTION RESULTS")
        print("=" * 60)
        
        detection = result['detection']
        print(f"Plant Type: {detection['plant']}")
        print(f"Condition: {detection['disease']}")
        print(f"Confidence: {detection['confidence']:.1%}")
        
        if detection['is_confident']:
            print("Status: ✓ High Confidence")
        else:
            print("Status: ⚠️  Low Confidence - Further verification needed")
        
        print("\nTop 5 Predictions:")
        for i, pred in enumerate(detection['top_5'], 1):
            print(f"  {i}. {pred['plant']} - {pred['disease']} ({pred['confidence']:.1%})")
        
        print("\n" + "=" * 60)
        print("TREATMENT ADVICE")
        print("=" * 60)
        
        advice = result['advice']
        if advice['success']:
            print(advice['advice'])
        else:
            print(f"Error: {advice.get('error')}\n")
            print(advice.get('fallback_advice', 'No advice available'))
        
        print("\n" + "=" * 60)
        
        return result
    
    def save_result(self, result, output_path='analysis_result.json'):
        """Save analysis result to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to {output_path}")
    
    def batch_analyze(self, image_folder, output_folder='results'):
        """
        Analyze multiple images in a folder
        
        Args:
            image_folder: Folder containing images
            output_folder: Where to save results
        """
        from pathlib import Path
        
        image_folder = Path(image_folder)
        output_folder = Path(output_folder)
        output_folder.mkdir(exist_ok=True)
        
        # Supported image formats
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        images = [f for f in image_folder.iterdir() 
                 if f.suffix.lower() in image_extensions]
        
        print(f"Found {len(images)} images in {image_folder}")
        print()
        
        results = []
        for i, img_path in enumerate(images, 1):
            print(f"\n[{i}/{len(images)}] Processing {img_path.name}...")
            
            try:
                result = self.analyze(img_path, verbose=False)
                results.append(result)
                
                # Save individual result
                output_file = output_folder / f"{img_path.stem}_result.json"
                self.save_result(result, output_file)
                
                # Quick summary
                det = result['detection']
                print(f"  → {det['plant']} / {det['disease']} ({det['confidence']:.1%})")
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
        
        # Save batch summary
        summary_file = output_folder / "batch_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n\nBatch analysis complete. Results saved to {output_folder}/")
        return results


# Example usage and testing
if __name__ == "__main__":
    # Initialize assistant
    assistant = PlantDiseaseAssistant(
        num_classes=38,
        confidence_threshold=0.7,
        llm_model="llama3.2:3b"  # Change to your model
    )
    
    # Print model info
    assistant.cnn.get_model_summary()
    
    print("\n" + "=" * 60)
    print("READY FOR ANALYSIS")
    print("=" * 60)
    print("\nTo analyze an image:")
    print("  result = assistant.analyze_and_display('path/to/image.jpg')")
    print("\nTo analyze a folder:")
    print("  results = assistant.batch_analyze('path/to/folder')")
    print("\n" + "=" * 60)
