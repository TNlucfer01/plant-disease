"""
prepare_dataset.py
------------------
Scans all downloaded datasets in `source_base`, normalises every class folder
name to the standard  PlantName_DiseaseName  format, then copies the images
into a unified  target_base/train  and  target_base/val  structure.

Run:
    python tools/prepare_dataset.py
    python tools/prepare_dataset.py --source <path> --target <path> --split 0.8
"""

import os
import re
import shutil
import random
from pathlib import Path
from tqdm import tqdm
import argparse

# ---------------------------------------------------------------------------
# Explicit raw-folder-name  →  PlantName_DiseaseName  mapping
# Covers all 29 downloaded datasets.  Set value to None to skip that folder.
# ---------------------------------------------------------------------------
CLASS_MAP: dict[str, str | None] = {
    # ── PlantVillage (01 / 02) ──────────────────────────────────────────────
    "Apple___Apple_scab":                              "Apple_Apple_Scab",
    "Apple___Black_rot":                               "Apple_Black_Rot",
    "Apple___Cedar_apple_rust":                        "Apple_Cedar_Apple_Rust",
    "Apple___healthy":                                 "Apple_Healthy",
    "Blueberry___healthy":                             "Blueberry_Healthy",
    "Cherry_(including_sour)___Powdery_mildew":        "Cherry_Powdery_Mildew",
    "Cherry_(including_sour)___healthy":               "Cherry_Healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Corn_Gray_Leaf_Spot",
    "Corn_(maize)___Common_rust_":                     "Corn_Common_Rust",
    "Corn_(maize)___Northern_Leaf_Blight":             "Corn_Northern_Leaf_Blight",
    "Corn_(maize)___healthy":                          "Corn_Healthy",
    "Grape___Black_rot":                               "Grape_Black_Rot",
    "Grape___Esca_(Black_Measles)":                    "Grape_Esca_Black_Measles",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)":      "Grape_Leaf_Blight",
    "Grape___healthy":                                 "Grape_Healthy",
    "Orange___Haunglongbing_(Citrus_greening)":        "Orange_Citrus_Greening",
    "Peach___Bacterial_spot":                          "Peach_Bacterial_Spot",
    "Peach___healthy":                                 "Peach_Healthy",
    "Pepper,_bell___Bacterial_spot":                   "Pepper_Bacterial_Spot",
    "Pepper,_bell___healthy":                          "Pepper_Healthy",
    "Potato___Early_blight":                           "Potato_Early_Blight",
    "Potato___Late_blight":                            "Potato_Late_Blight",
    "Potato___healthy":                                "Potato_Healthy",
    "Raspberry___healthy":                             "Raspberry_Healthy",
    "Soybean___healthy":                               "Soybean_Healthy",
    "Squash___Powdery_mildew":                         "Squash_Powdery_Mildew",
    "Strawberry___Leaf_scorch":                        "Strawberry_Leaf_Scorch",
    "Strawberry___healthy":                            "Strawberry_Healthy",
    "Tomato___Bacterial_spot":                         "Tomato_Bacterial_Spot",
    "Tomato___Early_blight":                           "Tomato_Early_Blight",
    "Tomato___Late_blight":                            "Tomato_Late_Blight",
    "Tomato___Leaf_Mold":                              "Tomato_Leaf_Mold",
    "Tomato___Septoria_leaf_spot":                     "Tomato_Septoria_Leaf_Spot",
    "Tomato___Spider_mites Two-spotted_spider_mite":   "Tomato_Spider_Mites",
    "Tomato___Target_Spot":                            "Tomato_Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus":          "Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus":                    "Tomato_Mosaic_Virus",
    "Tomato___healthy":                                "Tomato_Healthy",

    # ── PlantDoc / abdulhasib (03) / github (16) ───────────────────────────
    "Apple Scab Leaf":              "Apple_Apple_Scab",
    "Apple leaf":                   "Apple_Healthy",
    "Apple rust leaf":              "Apple_Cedar_Apple_Rust",
    "Bell_pepper leaf":             "Pepper_Healthy",
    "Bell_pepper leaf spot":        "Pepper_Bacterial_Spot",
    "Blueberry leaf":               "Blueberry_Healthy",
    "Cherry leaf":                  "Cherry_Healthy",
    "Corn Gray leaf spot":          "Corn_Gray_Leaf_Spot",
    "Corn leaf blight":             "Corn_Northern_Leaf_Blight",
    "Corn rust leaf":               "Corn_Common_Rust",
    "grape leaf":                   "Grape_Healthy",
    "grape leaf black rot":         "Grape_Black_Rot",
    "Peach leaf":                   "Peach_Healthy",
    "Potato leaf early blight":     "Potato_Early_Blight",
    "Potato leaf late blight":      "Potato_Late_Blight",
    "Raspberry leaf":               "Raspberry_Healthy",
    "Soyabean leaf":                "Soybean_Healthy",
    "Squash Powdery mildew leaf":   "Squash_Powdery_Mildew",
    "Strawberry leaf":              "Strawberry_Healthy",
    "Tomato Early blight leaf":     "Tomato_Early_Blight",
    "Tomato Septoria leaf spot":    "Tomato_Septoria_Leaf_Spot",
    "Tomato leaf":                  "Tomato_Healthy",
    "Tomato leaf bacterial spot":   "Tomato_Bacterial_Spot",
    "Tomato leaf late blight":      "Tomato_Late_Blight",
    "Tomato leaf mosaic virus":     "Tomato_Mosaic_Virus",
    "Tomato leaf yellow virus":     "Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato mold leaf":             "Tomato_Leaf_Mold",

    # ── Rice datasets (04 / 05 / 06) ───────────────────────────────────────
    "BrownSpot":            "Rice_Brown_Spot",
    "Hispa":                "Rice_Hispa",
    "LeafBlast":            "Rice_Leaf_Blast",
    "Bacterial Leaf Blight":"Rice_Bacterial_Leaf_Blight",
    "Brown Spot":           "Rice_Brown_Spot",
    "Healthy Rice Leaf":    "Rice_Healthy",
    "Leaf Blast":           "Rice_Leaf_Blast",
    "Leaf scald":           "Rice_Leaf_Scald",
    "Sheath Blight":        "Rice_Sheath_Blight",
    "Bacterial leaf blight":"Rice_Bacterial_Leaf_Blight",
    "Brown spot":           "Rice_Brown_Spot",
    "Leaf smut":            "Rice_Leaf_Smut",

    # ── Paddy disease competition (07) ─────────────────────────────────────
    "bacterial_leaf_blight": "Paddy_Bacterial_Leaf_Blight",
    "bacterial_leaf_streak": "Paddy_Bacterial_Leaf_Streak",
    "bacterial_panicle_blight": "Paddy_Bacterial_Panicle_Blight",
    "blast":                  "Paddy_Blast",
    "brown_spot":             "Paddy_Brown_Spot",
    "dead_heart":             "Paddy_Dead_Heart",
    "downy_mildew":           "Paddy_Downy_Mildew",
    "hispa":                  "Paddy_Hispa",
    "normal":                 "Paddy_Healthy",
    "tungro":                 "Paddy_Tungro",

    # ── Mango (08) ─────────────────────────────────────────────────────────
    "Anthracnose":      "Mango_Anthracnose",
    "Bacterial Canker": "Mango_Bacterial_Canker",
    "Cutting Weevil":   "Mango_Cutting_Weevil",
    "Die Back":         "Mango_Die_Back",
    "Gall Midge":       "Mango_Gall_Midge",
    "Healthy":          "Mango_Healthy",      # context: mango dataset
    "Powdery Mildew":   "Mango_Powdery_Mildew",
    "Sooty Mould":      "Mango_Sooty_Mould",

    # ── Sugarcane (09 akilesh) ─────────────────────────────────────────────
    "BacterialBlights": "Sugarcane_Bacterial_Blight",
    "Mosaic":           "Sugarcane_Mosaic",
    "RedRot":           "Sugarcane_Red_Rot",
    "Rust":             "Sugarcane_Rust",
    "Yellow":           "Sugarcane_Yellow",
    "Healthy_Leaves":   "Sugarcane_Healthy",

    # ── Sugarcane / Cotton (10 nirmal / 23 dhamur shared labels) ──────────
    "Aphids":               "Cotton_Aphids",
    "Aphids edited":        "Cotton_Aphids",
    "Army worm":            "Cotton_Army_Worm",
    "Army worm edited":     "Cotton_Army_Worm",
    "Bacterial blight":     "Cotton_Bacterial_Blight",
    "Bacterial Blight edited": "Cotton_Bacterial_Blight",
    "Healthy leaf edited":  "Cotton_Healthy",
    "Healthy leaf":         "Cotton_Healthy",   # cotton context
    "healthy leaf":         "Cotton_Healthy",
    "Powdery mildew":       "Cotton_Powdery_Mildew",
    "Powdery Mildew Edited":"Cotton_Powdery_Mildew",
    "Target spot":          "Cotton_Target_Spot",
    "Target spot edited":   "Cotton_Target_Spot",
    "Insect Pest Disease":  "Cotton_Insect_Pest",
    "Diseased Leaf":        "Cotton_Disease",
    "Small Leaf Disease":   "Cotton_Small_Leaf",
    "White Mold Disease":   "Cotton_White_Mold",
    "Wilt Disease":         "Cotton_Wilt",

    # ── Corn (11) ──────────────────────────────────────────────────────────
    "Blight":       "Corn_Northern_Leaf_Blight",
    "Common_Rust":  "Corn_Common_Rust",
    "Gray_Leaf_Spot": "Corn_Gray_Leaf_Spot",

    # ── Banana (12) ────────────────────────────────────────────────────────
    "cordana":          "Banana_Cordana",
    "healthy":          "Banana_Healthy",   # banana context
    "pestalotiopsis":   "Banana_Pestalotiopsis",
    "sigatoka":         "Banana_Sigatoka",

    # ── Tea (13 shashwat) ──────────────────────────────────────────────────
    "Anthracnose":   "Tea_Anthracnose",   # also used for Tea
    "algal leaf":    "Tea_Algal_Leaf",
    "bird eye spot": "Tea_Bird_Eye_Spot",
    "brown blight":  "Tea_Brown_Blight",
    "gray light":    "Tea_Gray_Blight",
    "red leaf spot": "Tea_Red_Leaf_Spot",
    "white spot":    "Tea_White_Spot",

    # ── Tea (14 BD) ────────────────────────────────────────────────────────
    "1. Tea algal leaf spot": "Tea_Algal_Leaf",
    "2. Brown Blight":        "Tea_Brown_Blight",
    "3. Gray Blight":         "Tea_Gray_Blight",
    "4. Helopeltis":          "Tea_Helopeltis",
    "5. Red spider":          "Tea_Red_Spider",
    "6. Green mirid bug":     "Tea_Green_Mirid_Bug",
    "7. Healthy leaf":        "Tea_Healthy",

    # ── Rubber / Coconut (15 / 28) ─────────────────────────────────────────
    "WCLWD_DryingofLeaflets": "Coconut_Drying_Of_Leaflets",
    "WCLWD_Flaccidity":       "Coconut_Flaccidity",
    "WCLWD_Yellowing":        "Coconut_Yellowing",
    "CCI_Caterpillars":       "Coconut_Caterpillars",
    "CCI_Leaflets":           "Coconut_Healthy",
    "Healthy_Leaves":         "Coconut_Healthy",

    # ── Cassava (17) ───────────────────────────────────────────────────────
    "Cassava Bacterial Blight":    "Cassava_Bacterial_Blight",
    "Cassava Brown Streak Disease":"Cassava_Brown_Streak",
    "Cassava Green Mite":          "Cassava_Green_Mite",
    "Cassava Mosaic Disease":      "Cassava_Mosaic",
    # Healthy already mapped per-dataset context

    # ── Eggplant (18 / 19) ─────────────────────────────────────────────────
    "Eggplant Healthy Leaf":            "Eggplant_Healthy",
    "Eggplant Insect Pest Disease":     "Eggplant_Insect_Pest",
    "Eggplant Leaf Spot Disease":       "Eggplant_Leaf_Spot",
    "Eggplant Mosaic Virus Disease":    "Eggplant_Mosaic_Virus",
    "Eggplant Small Leaf Disease":      "Eggplant_Small_Leaf",
    "Eggplant White Mold Disease":      "Eggplant_White_Mold",
    "Eggplant Wilt Disease":            "Eggplant_Wilt",
    "Augmented Eggplant Healthy Leaf":         "Eggplant_Healthy",
    "Augmented Eggplant Insect Pest Disease":  "Eggplant_Insect_Pest",
    "Augmented Eggplant Leaf Spot Disease":    "Eggplant_Leaf_Spot",
    "Augmented Eggplant Mosaic Virus Disease": "Eggplant_Mosaic_Virus",
    "Augmented Eggplant Small Leaf Disease":   "Eggplant_Small_Leaf",
    "Augmented Eggplant White Mold Disease":   "Eggplant_White_Mold",
    "Augmented Eggplant Wilt Disease":         "Eggplant_Wilt",
    "Augmented Healthy Leaf":       "Eggplant_Healthy",
    "Augmented Insect Pest Disease":"Eggplant_Insect_Pest",
    "Augmented Leaf Spot Disease":  "Eggplant_Leaf_Spot",
    "Augmented Mosaic Virus Disease":"Eggplant_Mosaic_Virus",
    "Augmented Small Leaf Disease": "Eggplant_Small_Leaf",
    "Augmented White Mold Disease": "Eggplant_White_Mold",
    "Augmented Wilt Disease":       "Eggplant_Wilt",

    # ── Okra (20) ──────────────────────────────────────────────────────────
    "diseased okra leaf": "Okra_Yellow_Vein_Mosaic",
    "fresh okra leaf":    "Okra_Healthy",

    # ── Onion (21) – if present ─────────────────────────────────────────────
    "Onion Anthracnose":        "Onion_Anthracnose",
    "Onion Purple Blotch":      "Onion_Purple_Blotch",
    "Onion Stemphylium Blight": "Onion_Stemphylium_Blight",
    "Onion Healthy":            "Onion_Healthy",

    # ── Cotton (22 / 23) ───────────────────────────────────────────────────
    "bacterial_blight": "Cotton_Bacterial_Blight",
    "curl_virus":        "Cotton_Curl_Virus",
    "fussarium_wilt":    "Cotton_Fusarium_Wilt",

    # ── Groundnut / Peanut (24 / 25) ───────────────────────────────────────
    "early_leaf_spot":        "Groundnut_Early_Leaf_Spot",
    "early_leaf_spot_1":      "Groundnut_Early_Leaf_Spot",
    "early_rust_1":           "Groundnut_Early_Rust",
    "healthy_leaf_1":         "Groundnut_Healthy",
    "late_leaf_spot_1":       "Groundnut_Late_Leaf_Spot",
    "late leaf spot":         "Groundnut_Late_Leaf_Spot",
    "nutrition_deficiency_1": "Groundnut_Nutrition_Deficiency",
    "nutrition deficiency":   "Groundnut_Nutrition_Deficiency",
    "rust_1":                 "Groundnut_Rust",
    "rust":                   "Groundnut_Rust",     # peanut context
    "healthy leaf":           "Groundnut_Healthy",  # peanut raw_data folder label

    # Dead Leaf / Normal from peanut (25)
    "Dead Leaf":    "Peanut_Dead_Leaf",
    "Normal Leaf":  "Peanut_Healthy",

    # ── Coffee (26 / 27) – annotation-only datasets, skip image sub-dirs ──
    # coffee-leaf-diseases uses images/ and masks/ – cannot reliably assign class
    # coffee_leaves_pest uses XML annotations – skip
    "miner_img_xml":  None,
    "rust_xml_image": None,
    "images":         None,
    "masks":          None,

    # ── Sorghum (29) ───────────────────────────────────────────────────────
    "Anthracnose and Red Rot": "Sorghum_Anthracnose_Red_Rot",
    "Cereal Grain molds":      "Sorghum_Grain_Mold",
    "Covered Kernel smut":     "Sorghum_Covered_Kernel_Smut",
    "Head Smut":               "Sorghum_Head_Smut",
    "loose smut":              "Sorghum_Loose_Smut",

    # ── Generic noise / skip ───────────────────────────────────────────────
    "Background_without_leaves": None,
    "15_rubber_leaf_disease":    None,
    "train": None, "val": None, "test": None, "valid": None, "validation": None,
    "images": None, "masks": None, "dataset": None,
    "color": None, "grayscale": None, "segmented": None,
    "AugmentedSet": None, "OriginalSet": None,
}

# Generic split-folder names to skip when climbing toward real class name
_SPLIT_FOLDERS = {
    "train", "val", "validation", "test", "valid", "images", "masks",
    "dataset", "color", "grayscale", "segmented", "augmentedset", "originalset",
    "raw_data", "data",
}

# ---------------------------------------------------------------------------
# Dataset-level context: path substring → default plant name for "Healthy" etc.
# ---------------------------------------------------------------------------
_DS_CONTEXT: dict[str, str] = {
    "04_rice_disease":    "Rice",
    "05_rice_leaf":       "Rice",
    "06_rice_diseases":   "Rice",
    "07_paddy":           "Paddy",
    "08_mango":           "Mango",
    "09_sugarcane":       "Sugarcane",
    "10_sugarcane":       "Sugarcane",
    "11_corn":            "Corn",
    "12_banana":          "Banana",
    "13_tea":             "Tea",
    "14_tea":             "Tea",
    "15_rubber":          "Rubber",
    "16_plantdoc":        None,
    "17_cassava":         "Cassava",
    "18_eggplant":        "Eggplant",
    "19_eggplant":        "Eggplant",
    "20_okra":            "Okra",
    "21_onion":           "Onion",
    "22_cotton":          "Cotton",
    "23_cotton":          "Cotton",
    "24_groundnut":       "Groundnut",
    "25_peanut":          "Peanut",
    "26_coffee":          None,   # skip
    "27_coffee":          None,   # skip
    "28_coconut":         "Coconut",
    "29_sorghum":         "Sorghum",
}

# "Healthy" class name with context fallback
_HEALTHY_CONTEXT_MAP: dict[str, str] = {
    k: f"{v}_Healthy" for k, v in _DS_CONTEXT.items() if v
}


def _dataset_context(path: Path) -> str | None:
    """Return the dataset key (e.g. '08_mango') matching path."""
    path_str = str(path).lower()
    for key in _DS_CONTEXT:
        if key.lower() in path_str:
            return key
    return None


def normalize_class_name(raw_name: str, folder_path: Path | None = None) -> str | None:
    """
    Convert a raw folder name to  PlantName_DiseaseName  format.
    Returns None if the folder should be skipped.
    """
    # Exact match first
    if raw_name in CLASS_MAP:
        mapped = CLASS_MAP[raw_name]
        # Handle ambiguous labels that depend on dataset context
        if mapped in ("Mango_Healthy", "Banana_Healthy", "Sugarcane_Healthy", "Cotton_Healthy"):
            if folder_path:
                ctx = _dataset_context(folder_path)
                if ctx and _DS_CONTEXT.get(ctx):
                    return f"{_DS_CONTEXT[ctx]}_Healthy"
        # Generic "Healthy" / "healthy" labels: use dataset context
        if mapped == "Mango_Healthy" and folder_path:
            ctx = _dataset_context(folder_path)
            if ctx and ctx not in ("08_mango",):
                plant = _DS_CONTEXT.get(ctx)
                if plant:
                    return f"{plant}_Healthy"
        return mapped

    # Case-insensitive exact match
    lower = raw_name.lower()
    for key, val in CLASS_MAP.items():
        if key.lower() == lower:
            return val

    # Generic "healthy" / "normal" labels — resolve from dataset context
    if lower in ("healthy", "normal leaf", "normal", "healthy leaf"):
        if folder_path:
            ctx = _dataset_context(folder_path)
            if ctx and _DS_CONTEXT.get(ctx):
                return f"{_DS_CONTEXT[ctx]}_Healthy"
        return None   # cannot determine plant

    # Unknown — skip
    return None


# ---------------------------------------------------------------------------
# Main preparation logic
# ---------------------------------------------------------------------------

def prepare_dataset(source_base: str, target_base: str, split_ratio: float = 0.8):
    """
    Scan *source_base* recursively for image folders, normalise class names,
    and copy images into *target_base/train* and *target_base/val*.
    """
    source_base = Path(source_base)
    target_base = Path(target_base)

    train_path = target_base / "train"
    val_path   = target_base / "val"
    train_path.mkdir(parents=True, exist_ok=True)
    val_path.mkdir(parents=True, exist_ok=True)

    print(f"\nScanning: {source_base}")

    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp",
                  ".JPG", ".JPEG", ".PNG", ".BMP", ".WEBP"}

    # class_name → list[Path]
    class_images: dict[str, list[Path]] = {}
    skipped_folders: list[str] = []

    for root, dirs, files in os.walk(source_base):
        img_files = [f for f in files if Path(f).suffix in image_exts]
        if not img_files:
            continue

        folder = Path(root)
        raw_class = folder.name

        # Climb up if this is a generic split/sub-folder
        while raw_class.lower() in _SPLIT_FOLDERS and folder.parent != source_base:
            folder = folder.parent
            raw_class = folder.name

        norm = normalize_class_name(raw_class, folder)
        if norm is None:
            skipped_folders.append(raw_class)
            continue

        if norm not in class_images:
            class_images[norm] = []
        for f in img_files:
            class_images[norm].append(Path(root) / f)

    # Report
    print(f"Found {len(class_images)} unique classes after normalisation.")
    if skipped_folders:
        unique_skipped = sorted(set(skipped_folders))
        print(f"Skipped {len(unique_skipped)} unrecognised folder names:")
        for s in unique_skipped:
            print(f"  ✗  {s}")

    # Copy files
    for class_name, images in tqdm(sorted(class_images.items()), desc="Copying classes"):
        class_train = train_path / class_name
        class_val   = val_path   / class_name
        class_train.mkdir(exist_ok=True)
        class_val.mkdir(exist_ok=True)

        random.seed(42)
        imgs = images.copy()
        random.shuffle(imgs)

        split_idx    = int(len(imgs) * split_ratio)
        train_images = imgs[:split_idx]
        val_images   = imgs[split_idx:]

        for i, img_path in enumerate(train_images):
            dest = class_train / f"{i}_{img_path.name}"
            if not dest.exists():
                try:
                    shutil.copy2(img_path, dest)
                except Exception as e:
                    print(f"  Skipping {img_path}: {e}")

        for i, img_path in enumerate(val_images):
            dest = class_val / f"{i}_{img_path.name}"
            if not dest.exists():
                try:
                    shutil.copy2(img_path, dest)
                except Exception as e:
                    print(f"  Skipping {img_path}: {e}")

    print(f"\n✅ Dataset ready!")
    print(f"   Train → {train_path}")
    print(f"   Val   → {val_path}")
    print(f"   Total classes: {len(class_images)}")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidate plant disease datasets.")
    parser.add_argument(
        "--source", type=str,
        default=r"c:\Users\udhay\Aathi\plant-disease\plant_disease_datasets",
        help="Root folder of downloaded datasets",
    )
    parser.add_argument(
        "--target", type=str,
        default=r"c:\Users\udhay\Aathi\plant-disease\dataset",
        help="Output folder for unified train/val structure",
    )
    parser.add_argument(
        "--split", type=float, default=0.8,
        help="Train split ratio (default 0.8)",
    )

    args = parser.parse_args()

    if Path(args.target).exists():
        print(f"⚠  Target exists: {args.target}  (existing files will be kept)")

    prepare_dataset(args.source, args.target, args.split)
