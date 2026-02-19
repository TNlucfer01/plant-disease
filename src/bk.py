"""
FastAPI Backend for Plant Disease Detection
Supports BOTH file upload and direct image URL
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
import uvicorn
from PIL import Image
import io
import requests
from pathlib import Path
import tempfile
import shutil
import json
import torch
from fastapi.middleware.cors import CORSMiddleware
# Import your pipeline (adjust import path as needed)
from plant_disease_pipeline import PlantDiseaseAssistant

app = FastAPI(
    title="Plant Disease Detection API",
    description="Detect plant diseases from leaf images (file upload or URL)",
    version="1.0.0"
)
app.add_middleware(CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)
# Global assistant (loaded once at startup)
assistant = None

@app.on_event("startup")
async def startup_event():
    global assistant
    print("Loading models...")
    assistant = PlantDiseaseAssistant(
        num_classes=38,
        confidence_threshold=0.7,
        llm_model="llama3.2:1b"
    )
    print("Models loaded successfully!")

def save_image_from_bytes(image_bytes: bytes, temp_dir: Path) -> Path:
    """Helper: Save bytes to temporary file"""
    temp_path = temp_dir / "input_image.jpg"
    with open(temp_path, "wb") as f:
        f.write(image_bytes)
    return temp_path

def download_image_from_url(url: str, temp_dir: Path) -> Path:
    """Download image from public URL"""
    try:
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            raise ValueError("URL does not point to an image")
        
        temp_path = temp_dir / "downloaded_image.jpg"
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(response.raw, f)
        
        # Verify it's really an image
        Image.open(temp_path).verify()
        return temp_path
    
    except Exception as e:
        raise ValueError(f"Failed to download or validate image from URL: {str(e)}")

@app.post("/analyze", summary="Analyze plant leaf image")
async def analyze(
    # ── File upload (multipart/form-data) ──
    file: UploadFile = File(None, description="Leaf image file (jpg/png)"),
    
    # ── OR JSON body with URL ──
    payload: dict = Body(
        None,
        examples={
            "url_example": {
                "summary": "Send image URL",
                "value": {"image_url": "https://example.com/leaf.jpg"}
            }
        }
    ),
    
    confidence_threshold: float = 0.7
):
    """
    Two ways to provide the image:
    
    1. File upload (preferred in Postman → form-data)
       Key: file    Value: choose file
    
    2. JSON body with image_url
       Content-Type: application/json
       Body:
       {
         "image_url": "https://..."
       }
    """
    if file is None and (payload is None or "image_url" not in payload):
        raise HTTPException(400, detail="Provide either 'file' (upload) or 'image_url' in JSON body")

    temp_path = None
    
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        
        try:
            if file is not None:
                # ── File upload path ──
                if file.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
                    raise HTTPException(400, "Only jpg/jpeg/png allowed")
                
                image_bytes = await file.read()
                temp_path = save_image_from_bytes(image_bytes, temp_dir)
            
            else:
                # ── URL path ──
                image_url = payload["image_url"]
                if not image_url.startswith(("http://", "https://")):
                    raise HTTPException(400, "Invalid URL format")
                
                temp_path = download_image_from_url(image_url, temp_dir)
            
            # Update threshold
            assistant.cnn.confidence_threshold = confidence_threshold
            
            # Run analysis
            result = assistant.analyze(temp_path, verbose=False)
            
            return {
                "status": "success",
                "detection": result["detection"],
                "advice": result["advice"],
                "used_input": "file" if file else "url"
            }
        
        except ValueError as ve:
            raise HTTPException(400, detail=str(ve))
        except Exception as e:
            raise HTTPException(500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health():
    if assistant is None:
        return {"status": "models not loaded"}
    return {
        "status": "healthy",
        "llm_connected": assistant.llm.test_connection(),
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)