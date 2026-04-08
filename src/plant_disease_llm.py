"""
LLM Integration for Plant Disease Advice
Uses local Ollama for generating treatment recommendations
"""

import requests
from typing import Dict


class PlantDiseaseLLM:
    def __init__(
        self,
        model_name: str = "qwen3:8b",
        ollama_url: str = "http://localhost:11434",
    ):
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
        """
        plant = prediction_result["plant"]
        disease = prediction_result["disease"]
        confidence = prediction_result["confidence"]
        is_confident = prediction_result["is_confident"]

        if not is_confident:
            return f"""
You are an expert agricultural advisor.

DETECTION RESULT:
- Plant: {plant}
- Condition: {disease}
- Confidence: {confidence:.1%} (LOW)

Explain:
1. Why confidence may be low
2. What signs to check
3. General precautions
4. When to seek expert help

Keep it under 200 words and farmer-friendly.
"""

        return f"""
You are an expert agricultural advisor.

DETECTION RESULT:
- Plant: {plant}
- Disease: {disease}
- Confidence: {confidence:.1%}

Provide advice in this format:

1. DISEASE OVERVIEW
2. SYMPTOMS TO CONFIRM
3. IMMEDIATE ACTIONS
4. TREATMENT OPTIONS
   - Chemical (active ingredients)
   - Organic
   - Cultural
5. PREVENTION

Keep it under 300 words and practical.
"""

    def get_advice(self, prediction_result: Dict, temperature: float = 0.3) -> Dict:
        """
        Get LLM-generated advice from Ollama
        """
        prompt = self.create_prompt(prediction_result)

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "num_predict": 512,
            },
        }

        try:
            response = requests.post(
                self.api_endpoint, json=payload, timeout=60
            )
            response.raise_for_status()

            result = response.json()
            advice_text = result.get("response", "")

            return {
                "success": True,
                "advice": advice_text,
                "model_used": self.model_name,
                "plant": prediction_result["plant"],
                "disease": prediction_result["disease"],
                "confidence": prediction_result["confidence"],
            }

        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to Ollama. Run: ollama serve",
                "fallback_advice": self._get_fallback_advice(prediction_result),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_advice": self._get_fallback_advice(prediction_result),
            }

    def _get_fallback_advice(self, prediction_result: Dict) -> str:
        """
        Basic advice when LLM is unavailable
        """
        plant = prediction_result["plant"]
        disease = prediction_result["disease"]
        confidence = prediction_result["confidence"]

        if not prediction_result["is_confident"]:
            return f"""
⚠️ Low confidence ({confidence:.1%})

- Retake images in good lighting
- Capture multiple leaves
- Consult local agricultural officer
"""

        if disease.lower() == "healthy":
            return f"""
✅ {plant} appears healthy ({confidence:.1%})

- Continue routine care
- Monitor regularly
- Maintain airflow
"""

        return f"""
🔍 {disease} detected on {plant} ({confidence:.1%})

- Isolate affected plants
- Remove infected leaves
- Avoid overhead watering
- Consult local experts
"""

    def test_connection(self) -> bool:
        try:
            r = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return r.status_code == 200
        except:
            return False

    def list_available_models(self) -> list:
        try:
            r = requests.get(f"{self.ollama_url}/api/tags")
            if r.status_code == 200:
                return [m["name"] for m in r.json().get("models", [])]
            return []
        except:
            return []


if __name__ == "__main__":
    llm = PlantDiseaseLLM()

    if llm.test_connection():
        print("✓ Ollama is running")
        print("Models:", llm.list_available_models())
    else:
        print("✗ Ollama not running → ollama serve")

    example_result = {
        "plant": "Tomato",
        "disease": "Early blight",
        "confidence": 0.92,
        "is_confident": True,
        "raw_class": "Tomato___Early_blight",
    }

    advice = llm.get_advice(example_result)

    if advice["success"]:
        print("\nLLM ADVICE:\n")
        print(advice["advice"])
    else:
        print("Error:", advice["error"])
        print(advice["fallback_advice"])
