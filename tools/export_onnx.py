"""
export_onnx.py  --  exports trained model to ONNX for Android deployment
Run from project root:  python tools/export_onnx.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import torch
import json
from pathlib import Path
from plant_disease_cnn import PlantDiseaseCNN

MODEL_PATH   = "best_plant_disease_model.pth"
CLASSES_JSON = "best_plant_disease_model_classes.json"
ONNX_OUT     = "plant_disease_model.onnx"

# ── Load classes ──────────────────────────────────────────────────────────────
if Path(CLASSES_JSON).exists():
    with open(CLASSES_JSON) as f:
        classes = json.load(f)
    num_classes = len(classes)
    print("Loaded %d classes from %s" % (num_classes, CLASSES_JSON))
else:
    num_classes = 114
    print("Warning: %s not found, using num_classes=%d" % (CLASSES_JSON, num_classes))

# ── Load model onto CPU ───────────────────────────────────────────────────────
print("Loading model from %s ..." % MODEL_PATH)
cnn = PlantDiseaseCNN(num_classes=num_classes)
cnn.load_model(MODEL_PATH)
cnn.model = cnn.model.cpu().eval()

# ── Use legacy (non-dynamo) export ────────────────────────────────────────────
dummy = torch.randn(1, 3, 224, 224)

print("Exporting to %s ..." % ONNX_OUT)
torch.onnx.export(
    cnn.model,
    dummy,
    ONNX_OUT,
    dynamo=False,                          # use legacy TorchScript-based exporter
    export_params=True,
    opset_version=17,
    do_constant_folding=True,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={
        "input":  {0: "batch_size"},
        "output": {0: "batch_size"},
    },
)

# ── Verify ────────────────────────────────────────────────────────────────────
import onnx
model_onnx = onnx.load(ONNX_OUT)
onnx.checker.check_model(model_onnx)

size_mb = Path(ONNX_OUT).stat().st_size / 1024 / 1024
print("\nExport complete!")
print("  File    : %s" % ONNX_OUT)
print("  Size    : %.1f MB" % size_mb)
print("  Classes : %d" % num_classes)
print("\nNext: copy %s to" % ONNX_OUT)
print("  PlantGuardAndroid/app/src/main/assets/")
