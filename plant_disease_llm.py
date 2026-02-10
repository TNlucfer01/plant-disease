"""
LLM Integration for Plant Disease Advice
Uses local Ollama for generating treatment recommendations
"""

import requests
import json
from typing import Dict, Optional


class PlantDiseaseLLM:
    def __init__(self, model_name="llama3.2:1b", ollama_url="http://localhost:11434"):
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
        is_confident = prediction_result.get('is_confident', True)
        
        # Check if plant is healthy
        is_healthy = disease.lower() == 'healthy'
        
        if is_healthy:
            prompt = f"""You are an expert agricultural advisor. A farmer has submitted a leaf image for analysis.

DETECTION RESULT:
- Plant: {plant}
- Status: {disease}
- Confidence: {confidence:.1%}

The plant appears to be HEALTHY. Please provide encouragement and maintenance advice in this format:

**WELCOME NOTE**
A warm, encouraging message congratulating the farmer on maintaining healthy {plant} plants.

**CURRENT STATUS**
Brief confirmation that the plant shows no signs of disease.

**MAINTENANCE RECOMMENDATIONS**
Best practices to keep the {plant} healthy:
- Watering schedule
- Fertilization tips
- Preventive care
- Monitoring practices

Keep the response positive, practical, and under 250 words."""

        else:
            # Disease detected - always provide full advice
            confidence_note = ""
            if not is_confident:
                confidence_note = f"\n\n⚠️ Note: Detection confidence is {confidence:.1%}. Please verify symptoms and consider professional consultation if unsure."
            
            prompt = f"""You are an expert agricultural advisor. A farmer has submitted a leaf image showing disease symptoms.

DETECTION RESULT:
- Plant: {plant}
- Disease: {disease}
- Confidence: {confidence:.1%}

Please provide comprehensive advice in this EXACT format:

**WELCOME NOTE**
A brief, empathetic greeting acknowledging the farmer's concern about their {plant} plant.

**DISEASE OVERVIEW**
- What is {disease}?
- Why does it affect {plant}?
- How serious is this disease?

**CAUSES OF THE DISEASE**
List the main factors that cause {disease}:
- Environmental conditions (humidity, temperature, etc.)
- Poor agricultural practices
- Pathogen spread mechanisms
- Other contributing factors

**SYMPTOMS TO CONFIRM**
Visual signs the farmer should check on their plants to confirm this diagnosis.

**TREATMENT & REMEDY**
Provide specific, actionable treatments:

1. **Immediate Actions** (within 24-48 hours):
   - What to do RIGHT NOW

2. **Chemical Treatment**:
   - Recommended fungicides/pesticides with active ingredients
   - Application instructions
   - Safety precautions

3. **Organic/Natural Alternatives**:
   - Home remedies and organic solutions
   - Natural fungicides or pesticides

4. **Cultural Practices**:
   - Farm management changes
   - Pruning and sanitation
   - Crop rotation suggestions

**PREVENTION**
How to prevent {disease} from occurring again in the future.

{confidence_note}

Keep the language simple, practical, and farmer-friendly. Total length: 300-400 words."""

        return prompt

    def get_advice(self, prediction_result: Dict, temperature=0.3) -> Dict:
        """
        Get LLM-generated advice based on CNN prediction
        ALWAYS generates advice for top prediction regardless of confidence
        
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
                "num_predict": 600  # Increased for structured format
            }
        }
        
        try:
            # Call Ollama API
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=90  # Increased timeout for longer responses
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
                'confidence': prediction_result['confidence'],
                'is_confident': prediction_result.get('is_confident', True)
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
        Provide structured basic advice when LLM is unavailable
        """
        plant = prediction_result['plant']
        disease = prediction_result['disease']
        confidence = prediction_result['confidence']
        is_confident = prediction_result.get('is_confident', True)
        
        if disease.lower() == 'healthy':
            return f"""**WELCOME NOTE**
Great news! Your {plant} plant appears to be in good health.

**CURRENT STATUS**
No disease symptoms detected (Confidence: {confidence:.1%})

**MAINTENANCE RECOMMENDATIONS**
To keep your {plant} healthy:
- Water regularly but avoid overwatering
- Ensure good drainage and air circulation
- Apply balanced fertilizer as needed
- Monitor leaves regularly for any changes
- Remove dead or damaged leaves promptly

⚠️ LLM service unavailable - showing basic guidance only."""

        confidence_warning = ""
        if not is_confident:
            confidence_warning = f"\n\n⚠️ **Low Confidence Warning** ({confidence:.1%})\nThe detection system is not very confident. Please verify symptoms and consider professional diagnosis."

        return f"""**WELCOME NOTE**
We understand your concern about your {plant} plant showing signs of {disease}.

**DISEASE OVERVIEW**
{disease} has been detected on your {plant} plant with {confidence:.1%} confidence.

**CAUSES OF THE DISEASE**
Common causes include:
- High humidity and poor air circulation
- Overhead watering
- Infected plant material or soil
- Favorable weather conditions for pathogen growth

**TREATMENT & REMEDY**

**Immediate Actions:**
1. Isolate affected plants if possible
2. Remove and destroy severely infected leaves
3. Avoid working with plants when wet

**Chemical Treatment:**
- Consult local agricultural store for appropriate fungicide/pesticide
- Follow label instructions carefully
- Apply during cooler parts of the day

**Organic Alternatives:**
- Neem oil spray
- Copper-based fungicides
- Baking soda solution (1 tbsp per gallon of water)

**Cultural Practices:**
- Improve air circulation by proper spacing
- Water at the base of plants, not overhead
- Remove plant debris regularly
- Practice crop rotation

**PREVENTION**
- Use disease-resistant varieties
- Maintain good sanitation
- Avoid overhead irrigation
- Monitor plants regularly

{confidence_warning}

⚠️ LLM service unavailable - showing basic guidance only.
For detailed treatment, please consult a local agricultural extension officer."""

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
    
    # Example 1: High confidence disease detection
    print("\n" + "="*70)
    print("EXAMPLE 1: Potato Late Blight (High Confidence)")
    print("="*70)
    
    example1 = {
        'plant': 'Potato',
        'disease': 'Late blight',
        'confidence': 0.92,
        'is_confident': True,
        'raw_class': 'Potato___Late_blight'
    }
    
    advice1 = llm.get_advice(example1)
    if advice1['success']:
        print(advice1['advice'])
    else:
        print(f"\nError: {advice1.get('error')}")
        print("\nFallback advice:")
        print(advice1.get('fallback_advice'))
    
    # Example 2: Low confidence detection
    print("\n" + "="*70)
    print("EXAMPLE 2: Tomato Early Blight (Low Confidence)")
    print("="*70)
    
    example2 = {
        'plant': 'Tomato',
        'disease': 'Early blight',
        'confidence': 0.45,
        'is_confident': False,
        'raw_class': 'Tomato___Early_blight'
    }
    
    advice2 = llm.get_advice(example2)
    if advice2['success']:
        print(advice2['advice'])
    else:
        print(f"\nError: {advice2.get('error')}")
        print("\nFallback advice:")
        print(advice2.get('fallback_advice'))
    
    # Example 3: Healthy plant
    print("\n" + "="*70)
    print("EXAMPLE 3: Healthy Potato")
    print("="*70)
    
    example3 = {
        'plant': 'Potato',
        'disease': 'Healthy',
        'confidence': 0.88,
        'is_confident': True,
        'raw_class': 'Potato___Healthy'
    }
    
    advice3 = llm.get_advice(example3)
    if advice3['success']:
        print(advice3['advice'])
    else:
        print(f"\nError: {advice3.get('error')}")
        print("\nFallback advice:")
        print(advice3.get('fallback_advice'))