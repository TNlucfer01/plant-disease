"""
Test Script - Verify Installation and Model Functionality
Run this to check if everything is working correctly
"""

import sys
from pathlib import Path

def check_imports():
    """Check if all required packages are installed"""
    print("="*60)
    print("CHECKING PACKAGE INSTALLATIONS")
    print("="*60)
    
    required_packages = {
        'torch': 'PyTorch',
        'torchvision': 'TorchVision',
        'PIL': 'Pillow',
        'streamlit': 'Streamlit',
        'requests': 'Requests',
        'numpy': 'NumPy',
        'tqdm': 'tqdm'
    }
    
    all_installed = True
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {name:15} - Installed")
        except ImportError:
            print(f"✗ {name:15} - NOT INSTALLED")
            all_installed = False
    
    print()
    return all_installed


def check_pytorch():
    """Check PyTorch configuration"""
    print("="*60)
    print("PYTORCH CONFIGURATION")
    print("="*60)
    
    try:
        import torch
        print(f"PyTorch Version: {torch.__version__}")
        print(f"CUDA Available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"CUDA Version: {torch.version.cuda}")
            print(f"GPU Device: {torch.cuda.get_device_name(0)}")
        else:
            print("Running on CPU (this is fine!)")
        
        print()
        return True
    except Exception as e:
        print(f"Error: {e}")
        print()
        return False


def check_model_loading():
    """Test if CNN model can be loaded"""
    print("="*60)
    print("TESTING CNN MODEL LOADING")
    print("="*60)
    
    try:
        from plant_disease_cnn import PlantDiseaseCNN
        
        print("Initializing MobileNetV2...")
        model = PlantDiseaseCNN(num_classes=38)
        
        print("✓ Model loaded successfully!")
        print()
        
        model.get_model_summary()
        print()
        
        return True
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        print()
        return False


def check_ollama():
    """Check if Ollama is running"""
    print("="*60)
    print("CHECKING OLLAMA (LLM) CONNECTION")
    print("="*60)
    
    try:
        from plant_disease_llm import PlantDiseaseLLM
        
        llm = PlantDiseaseLLM()
        
        if llm.test_connection():
            print("✓ Ollama is running!")
            
            models = llm.list_available_models()
            if models:
                print(f"✓ Available models: {', '.join(models)}")
            else:
                print("⚠️  No models found. Run: ollama pull llama3.2:3b")
            
            print()
            return True
        else:
            print("✗ Ollama is not running")
            print("\nTo start Ollama:")
            print("  1. Install: https://ollama.com/download")
            print("  2. Run: ollama serve")
            print("  3. Pull model: ollama pull llama3.2:3b")
            print()
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        print()
        return False


def test_dummy_prediction():
    """Test prediction with a dummy image"""
    print("="*60)
    print("TESTING DUMMY PREDICTION")
    print("="*60)
    
    try:
        import torch
        from PIL import Image
        import numpy as np
        from plant_disease_cnn import PlantDiseaseCNN
        
        # Create a dummy RGB image
        print("Creating dummy image (224x224 RGB)...")
        dummy_image = Image.fromarray(
            np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        )
        
        # Save temporarily
        dummy_path = Path("test_dummy_image.jpg")
        dummy_image.save(dummy_path)
        
        print("Loading model...")
        model = PlantDiseaseCNN(num_classes=38)
        
        print("Running prediction...")
        result = model.predict(str(dummy_path))
        
        print("\n✓ Prediction successful!")
        print(f"  Predicted: {result['plant']} - {result['disease']}")
        print(f"  Confidence: {result['confidence']:.1%}")
        print(f"  Is confident: {result['is_confident']}")
        
        # Cleanup
        dummy_path.unlink()
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Error during prediction: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def test_llm_integration():
    """Test LLM advice generation"""
    print("="*60)
    print("TESTING LLM INTEGRATION")
    print("="*60)
    
    try:
        from plant_disease_llm import PlantDiseaseLLM
        
        llm = PlantDiseaseLLM()
        
        # Mock prediction result
        mock_prediction = {
            'plant': 'Tomato',
            'disease': 'Early blight',
            'confidence': 0.92,
            'is_confident': True,
            'raw_class': 'Tomato___Early_blight'
        }
        
        print("Generating advice for mock prediction...")
        print(f"  Plant: {mock_prediction['plant']}")
        print(f"  Disease: {mock_prediction['disease']}")
        print()
        
        advice = llm.get_advice(mock_prediction)
        
        if advice['success']:
            print("✓ Advice generated successfully!")
            print("\nGenerated Advice:")
            print("-" * 60)
            print(advice['advice'])
            print("-" * 60)
        else:
            print("⚠️  Using fallback advice (Ollama not running)")
            print("\nFallback Advice:")
            print("-" * 60)
            print(advice.get('fallback_advice', 'No advice available'))
            print("-" * 60)
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
        return False


def test_full_pipeline():
    """Test the complete pipeline"""
    print("="*60)
    print("TESTING COMPLETE PIPELINE")
    print("="*60)
    
    try:
        import numpy as np
        from PIL import Image
        from pathlib import Path
        from plant_disease_pipeline import PlantDiseaseAssistant
        
        # Create dummy image
        dummy_image = Image.fromarray(
            np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        )
        dummy_path = Path("test_pipeline_image.jpg")
        dummy_image.save(dummy_path)
        
        print("Initializing complete assistant...")
        assistant = PlantDiseaseAssistant(
            num_classes=38,
            confidence_threshold=0.7
        )
        
        print("\nRunning full analysis (CNN → LLM)...")
        result = assistant.analyze(str(dummy_path), verbose=False)
        
        print("\n✓ Pipeline executed successfully!")
        print(f"\nDetection:")
        print(f"  Plant: {result['detection']['plant']}")
        print(f"  Disease: {result['detection']['disease']}")
        print(f"  Confidence: {result['detection']['confidence']:.1%}")
        
        print(f"\nAdvice Status:")
        if result['advice']['success']:
            print("  ✓ LLM advice generated")
        else:
            print("  ⚠️  Fallback advice used")
        
        # Cleanup
        dummy_path.unlink()
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def main():
    """Run all tests"""
    print("\n" + "🌿"*30)
    print("PLANT DISEASE DETECTION SYSTEM - INSTALLATION TEST")
    print("🌿"*30 + "\n")
    
    results = {}
    
    # Run tests
    results['imports'] = check_imports()
    results['pytorch'] = check_pytorch()
    results['model'] = check_model_loading()
    results['ollama'] = check_ollama()
    results['prediction'] = test_dummy_prediction()
    results['llm'] = test_llm_integration()
    results['pipeline'] = test_full_pipeline()
    
    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name.title():20} {status}")
    
    print()
    
    all_passed = all(results.values())
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nYou're ready to go! Run the app with:")
        print("  streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("  - Install packages: pip install -r requirements.txt")
        print("  - Install Ollama: https://ollama.com/download")
        print("  - Start Ollama: ollama serve")
        print("  - Pull model: ollama pull llama3.2:3b")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
