"""
LLM Integration for Plant Disease Advice
Uses local Ollama for generating treatment recommendations
"""

import requests
import json
from typing import Dict, Optional

class PlantDiseaseLLM:
    def __init__(self, 
                 model_name="mistral",  # Lightweight model
                 ollama_url="http://localhost:11434"):
        """
        Initialize LLM client
        
        Args:
            model_name: Ollama model to use (llama3.2:3b, mistral, etc.)
            ollama_url: Ollama API endpoint
        """
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.api_endpoint = f"{ollama_url}/api/generate"
    
    def create_prompt(self, prediction_result: Dict) -> str:
        """
        Convert CNN prediction to structured LLM prompt
        
        Args:
            prediction_result: Dictionary from CNN model prediction
            
        Returns:
            str: Formatted prompt for LLM
        """
        plant = prediction_result['plant']
        disease = prediction_result['disease']
        confidence = prediction_result['confidence']
        is_confident = prediction_result['is_confident']
        
        # Handle uncertain predictions
        if not is_confident:
            prompt = f"""You are an expert agricultural advisor. A farmer has submitted a leaf image for disease detection.

DETECTION RESULT:
- Most likely plant: {plant}
- Most likely condition: {disease}
- Confidence level: {confidence:.1%} (LOW CONFIDENCE)

The AI detection system has low confidence in this diagnosis. This could mean:
1. The image quality is poor
2. The symptoms are unclear or early-stage
3. The plant may have an uncommon disease
4. Multiple diseases may be present

Please provide:
1. A brief explanation of why confidence is low
2. What the farmer should look for to confirm the diagnosis
3. General precautions they should take while investigating
4. When to seek professional help

Keep the response practical, concise (under 200 words), and farmer-friendly."""
        else:
            # High confidence prompt
            prompt = f"""You are an expert agricultural advisor. A farmer's leaf image shows the following diagnosis:

DETECTION RESULT:
- Plant: {plant}
- Disease: {disease}
- Confidence: {confidence:.1%}

Please provide practical advice in this format:

1. DISEASE OVERVIEW (2-3 sentences)
Brief description of {disease} and why it affects {plant}.

2. SYMPTOMS TO CONFIRM
What visual signs the farmer should verify on their plants.

3. IMMEDIATE ACTIONS
What the farmer should do RIGHT NOW (within 24-48 hours).

4. TREATMENT OPTIONS
- Chemical: Specific fungicides/pesticides (with active ingredients)
- Organic: Natural alternatives
- Cultural: Farm management practices

5. PREVENTION
How to prevent this disease in the future.

Keep it practical, specific to {plant} and {disease}, concise (under 300 words), and use simple language for farmers."""

        return prompt
    
    def get_advice(self, prediction_result: Dict, temperature=0.3) -> Dict:
        """
        Get LLM-generated advice based on CNN prediction
        
        Args:
            prediction_result: CNN prediction dictionary
            temperature: LLM temperature (lower = more focused)
            
        Returns:
            Dict with advice text and metadata
        """
        # Create structured prompt
        prompt = self.create_prompt(prediction_result)
        
        # Prepare request payload
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "num_predict": 512  # Max tokens
            }
        }
        
        try:
            # Call Ollama API
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            advice_text = result.get('response', '')
            
            return {
                'success': True,
                'advice': advice_text,
                'model_used': self.model_name,
                'prompt': prompt,
                'plant': prediction_result['plant'],
                'disease': prediction_result['disease'],
                'confidence': prediction_result['confidence']
            }
            
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Cannot connect to Ollama. Make sure Ollama is running (ollama serve)',
                'fallback_advice': self._get_fallback_advice(prediction_result)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'fallback_advice': self._get_fallback_advice(prediction_result)
            }
    
    def _get_fallback_advice(self, prediction_result: Dict) -> str:
        """
        Provide basic advice when LLM is unavailable
        """
        plant = prediction_result['plant']
        disease = prediction_result['disease']
        confidence = prediction_result['confidence']
        
        if not prediction_result['is_confident']:
            return f"""⚠️ Low confidence detection ({confidence:.1%})

The image analysis is uncertain. Please:
1. Take clearer photos in good lighting
2. Capture multiple affected leaves
3. Consult a local agricultural extension officer
4. Consider getting a professional diagnosis"""
        
        if disease.lower() == 'healthy':
            return f"""✅ Your {plant} appears healthy!

The detection shows no signs of disease ({confidence:.1%} confidence).

Maintenance tips:
- Continue regular watering and fertilization
- Monitor for any new symptoms
- Maintain good air circulation
- Practice crop rotation if applicable"""
        
        return f"""🔍 Detected: {disease} on {plant} ({confidence:.1%} confidence)

General recommendations:
1. Isolate affected plants if possible
2. Remove and destroy infected leaves
3. Improve air circulation around plants
4. Avoid overhead watering
5. Consult local agricultural extension for specific treatments

⚠️ LLM service unavailable - showing basic guidance only."""
    
    def test_connection(self) -> bool:
        """Test if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_available_models(self) -> list:
        """List models available in Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [m['name'] for m in models]
            return []
        except:
            return []


# Example usage
if __name__ == "__main__":
    # Initialize LLM
    llm = PlantDiseaseLLM()
    
    # Test connection
    if llm.test_connection():
        print("✓ Ollama is running")
        models = llm.list_available_models()
        print(f"Available models: {models}")
    else:
        print("✗ Ollama is not running. Start it with: ollama serve")
    
    # Example prediction result from CNN
    example_result = {
        'plant': 'Tomato',
        'disease': 'Early blight',
        'confidence': 0.92,
        'is_confident': True,
        'raw_class': 'Tomato___Early_blight'
    }
    
    # Get advice
    advice = llm.get_advice(example_result)
    
    if advice['success']:
        print("\n" + "="*60)
        print("LLM ADVICE:")
        print("="*60)
        print(advice['advice'])
    else:
        print(f"\nError: {advice.get('error')}")
        print("\nFallback advice:")
        print(advice.get('fallback_advice'))