"""
Plant Disease Detection — ONNX Runtime Inference Engine

Run from the project root:
    python tools/onnx_inference.py --image images/Cherry\ Image\ 2.jpeg
    python tools/onnx_inference.py --image images/Cherry\ Image\ 2.jpeg --model models/plant_disease_model.onnx
"""

import argparse
import pathlib
import sys
import time
import numpy as np
from PIL import Image
import onnxruntime as ort

# Force UTF-8 output on Windows so progress/status chars render correctly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Auto-resolve model path relative to this file
_HERE              = pathlib.Path(__file__).parent          # tools/
_ROOT              = _HERE.parent                           # project root
_DEFAULT_MODEL     = str(_ROOT / "models" / "plant_disease_model.onnx")


# ── Class names (same order as training) ──────────────────────────────────────
CLASS_NAMES = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew',
    'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight',
    'Corn_(maize)___healthy',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy',
]

# ImageNet normalization constants (same as training)
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

CONFIDENCE_THRESHOLD = 0.7


# ── Helper functions ───────────────────────────────────────────────────────────

def preprocess(image_path: str) -> np.ndarray:
    """
    Replicate the torchvision transforms used during training:
        Resize(256) → CenterCrop(224) → ToTensor() → Normalize(mean, std)
    Returns:
        float32 numpy array of shape (1, 3, 224, 224)
    """
    img = Image.open(image_path).convert("RGB")

    # Resize shortest side to 256
    w, h   = img.size
    scale  = 256 / min(w, h)
    new_w, new_h = int(round(w * scale)), int(round(h * scale))
    img    = img.resize((new_w, new_h), Image.BILINEAR)

    # Center crop to 224×224
    left   = (new_w - 224) // 2
    top    = (new_h - 224) // 2
    img    = img.crop((left, top, left + 224, top + 224))

    # ToTensor → float32 in [0, 1]
    arr    = np.array(img, dtype=np.float32) / 255.0   # (224, 224, 3)

    # Normalize
    arr    = (arr - MEAN) / STD                         # (224, 224, 3)

    # HWC → CHW → NCHW
    arr    = arr.transpose(2, 0, 1)                     # (3, 224, 224)
    arr    = np.expand_dims(arr, axis=0)                # (1, 3, 224, 224)
    return arr


def softmax(logits: np.ndarray) -> np.ndarray:
    e = np.exp(logits - logits.max())
    return e / e.sum()


def parse_class(raw: str):
    """Split 'Tomato___Early_blight' → ('Tomato', 'Early blight')"""
    parts = raw.split("___")
    if len(parts) == 2:
        return parts[0].replace("_", " "), parts[1].replace("_", " ")
    return raw, "Unknown"


def top_k(probs: np.ndarray, k: int = 5):
    indices = probs.argsort()[::-1][:k]
    results = []
    for idx in indices:
        plant, disease = parse_class(CLASS_NAMES[idx])
        results.append({
            "rank":       len(results) + 1,
            "plant":      plant,
            "disease":    disease,
            "confidence": float(probs[idx]),
            "class_id":   int(idx),
        })
    return results


# ── ONNX Runtime session wrapper ──────────────────────────────────────────────

class PlantDiseaseONNX:
    """Wraps an ONNX Runtime session for plant disease inference."""

    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = _DEFAULT_MODEL
        # Prefer CUDA if available, fall back to CPU
        providers = (
            ["CUDAExecutionProvider", "CPUExecutionProvider"]
            if "CUDAExecutionProvider" in ort.get_available_providers()
            else ["CPUExecutionProvider"]
        )

        print(f"[*] Loading ONNX model from '{model_path}' ...")
        self.session   = ort.InferenceSession(model_path, providers=providers)
        self.input_name  = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        active = self.session.get_providers()[0]
        print(f"[OK] Session ready  |  Provider: {active}")

    def predict(self, image_path: str) -> dict:
        """
        Run inference on a single image.
        Returns a result dict with plant, disease, confidence, top_5, etc.
        """
        # Preprocess
        input_tensor = preprocess(image_path)                        # (1,3,224,224)

        # Inference
        t0 = time.perf_counter()
        logits = self.session.run(
            [self.output_name],
            {self.input_name: input_tensor}
        )[0][0]                                                       # shape: (38,)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        # Probabilities
        probs    = softmax(logits)
        best_idx = int(probs.argmax())
        confidence = float(probs[best_idx])
        plant, disease = parse_class(CLASS_NAMES[best_idx])

        return {
            "plant":        plant,
            "disease":      disease,
            "confidence":   confidence,
            "is_healthy":   "healthy" in disease.lower(),
            "is_confident": confidence >= CONFIDENCE_THRESHOLD,
            "raw_class":    CLASS_NAMES[best_idx],
            "top_5":        top_k(probs, k=5),
            "inference_ms": round(elapsed_ms, 2),
        }

    def predict_batch(self, image_paths: list) -> list:
        """Run inference on a list of images (one by one)."""
        return [self.predict(p) for p in image_paths]


# ── Pretty printer ─────────────────────────────────────────────────────────────

def print_result(result: dict, image_path: str):
    bar = "=" * 60
    print(f"\n{bar}")
    print(f"  Image     : {image_path}")
    print(f"  Plant     : {result['plant']}")
    print(f"  Disease   : {result['disease']}")
    print(f"  Confidence: {result['confidence'] * 100:.1f}%")
    status = "[HEALTHY]" if result["is_healthy"] else "[DISEASED]"
    flag   = "[Confident]" if result["is_confident"] else "[Low confidence]"
    print(f"  Status    : {status}  |  {flag}")
    print(f"  Latency   : {result['inference_ms']} ms")
    print(f"\n  Top-5 Predictions:")
    for item in result["top_5"]:
        bar_len = int(item["confidence"] * 30)
        bar_vis = "#" * bar_len + "-" * (30 - bar_len)
        print(f"    #{item['rank']}  {bar_vis}  {item['confidence']*100:5.1f}%"
              f"  {item['plant']} — {item['disease']}")
    print("=" * 60)


# ── CLI entry point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Plant Disease Detection via ONNX Runtime"
    )
    parser.add_argument(
        "--image", "-i", required=True,
        help="Path to the leaf image (jpg/png)"
    )
    parser.add_argument(
        "--model", "-m", default=None,
        help=f"Path to the ONNX model file (default: models/plant_disease_model.onnx)"
    )
    parser.add_argument(
        "--threshold", "-t", type=float, default=0.7,
        help="Confidence threshold (default: 0.7)"
    )
    args = parser.parse_args()

    global CONFIDENCE_THRESHOLD
    CONFIDENCE_THRESHOLD = args.threshold

    model  = PlantDiseaseONNX(model_path=args.model)
    result = model.predict(args.image)
    print_result(result, args.image)


if __name__ == "__main__":
    main()
