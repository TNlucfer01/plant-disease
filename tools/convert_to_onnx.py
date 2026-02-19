"""
Convert Plant Disease CNN (MobileNetV2 PyTorch) → ONNX

Run from the project root:
    python tools/convert_to_onnx.py

Or from with tools/ folder:
    python convert_to_onnx.py

Output: models/plant_disease_model.onnx
"""

import torch
import torch.nn as nn
from torchvision import models
import numpy as np
import os

# ── Configuration ─────────────────────────────────────────────────────────────
import pathlib
_HERE           = pathlib.Path(__file__).parent          # tools/
_ROOT           = _HERE.parent                           # project root

PTH_MODEL_PATH  = str(_ROOT / "models" / "best_plant_disease_model.pth")
ONNX_MODEL_PATH = str(_ROOT / "models" / "plant_disease_model.onnx")
NUM_CLASSES     = 38
INPUT_SIZE      = (1, 3, 224, 224)   # batch=1, RGB, 224×224
OPSET_VERSION   = 12                 # onnxscript required by torch>=2.0
# ──────────────────────────────────────────────────────────────────────────────


def build_model(num_classes: int) -> nn.Module:
    """Recreate the exact same architecture used during training."""
    model = models.mobilenet_v2(weights=None)          # no pretrained weights
    model.classifier = nn.Sequential(
        nn.Dropout(0.2),
        nn.Linear(1280, num_classes)
    )
    return model


def load_pytorch_model(pth_path: str, num_classes: int) -> nn.Module:
    """Load state-dict into the model."""
    if not os.path.exists(pth_path):
        raise FileNotFoundError(f"Model file not found: {pth_path}")

    device = torch.device("cpu")        # always export on CPU
    model  = build_model(num_classes)
    state  = torch.load(pth_path, map_location=device)

    # state_dict may be wrapped inside a dict
    if isinstance(state, dict) and "model_state_dict" in state:
        state = state["model_state_dict"]

    model.load_state_dict(state)
    model.eval()
    print(f"✅  Loaded PyTorch weights from  '{pth_path}'")
    return model


def export_onnx(model: nn.Module, onnx_path: str, input_size: tuple, opset: int):
    """Export the model to ONNX with named axes for dynamic batching."""
    dummy_input = torch.randn(*input_size, requires_grad=False)

    print(f"\n🔄  Exporting to ONNX  (opset {opset}) …")
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        opset_version        = opset,
        export_params        = True,
        do_constant_folding  = True,
        input_names          = ["input"],
        output_names         = ["output"],
        dynamic_axes         = {
            "input":  {0: "batch_size"},
            "output": {0: "batch_size"},
        },
    )
    size_mb = os.path.getsize(onnx_path) / (1024 ** 2)
    print(f"✅  ONNX model saved  →  '{onnx_path}'  ({size_mb:.1f} MB)")


def validate_onnx(onnx_path: str, pytorch_model: nn.Module, input_size: tuple):
    """Compare PyTorch vs ONNX Runtime outputs on a random input."""
    try:
        import onnx
        import onnxruntime as ort
    except ImportError:
        print("⚠️   onnx / onnxruntime not installed – skipping validation.")
        print("    Run:  pip install onnx onnxruntime")
        return

    # ── ONNX model check ──────────────────────────────────────────────────────
    onnx_model = onnx.load(onnx_path)
    onnx.checker.check_model(onnx_model)
    print("✅  ONNX model structure is valid")

    # ── Numerical comparison ──────────────────────────────────────────────────
    dummy_np = np.random.randn(*input_size).astype(np.float32)
    dummy_pt = torch.from_numpy(dummy_np)

    with torch.no_grad():
        pt_out = pytorch_model(dummy_pt).numpy()

    sess    = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    ort_out = sess.run(["output"], {"input": dummy_np})[0]

    max_diff = np.max(np.abs(pt_out - ort_out))
    print(f"✅  Max output difference (PyTorch vs ONNX RT): {max_diff:.2e}")
    if max_diff < 1e-4:
        print("✅  Outputs match — conversion successful!\n")
    else:
        print("⚠️   Large diff detected – check opset compatibility.\n")


def main():
    print("=" * 60)
    print("  Plant Disease CNN  →  ONNX Converter")
    print("=" * 60)

    model = load_pytorch_model(PTH_MODEL_PATH, NUM_CLASSES)
    export_onnx(model, ONNX_MODEL_PATH, INPUT_SIZE, OPSET_VERSION)
    validate_onnx(ONNX_MODEL_PATH, model, INPUT_SIZE)

    print("Done! Next step:")
    print("  python tools/onnx_inference.py --image images/<leaf.jpg>")


if __name__ == "__main__":
    main()
