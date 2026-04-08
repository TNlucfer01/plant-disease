"""
merge_duplicates.py
-------------------
Post-processing step: after prepare_dataset.py has copied images into
dataset/train  and  dataset/val, run this script to merge any remaining
duplicate or oddly-named class folders into the standard
PlantName_DiseaseName format.

Run:
    python tools/merge_duplicates.py
"""

import os
import shutil
from pathlib import Path

# ── Full normalisation map (mirrors prepare_dataset.py for consistency) ──────
# raw folder name  →  PlantName_DiseaseName  (None = delete / ignore)
CLASS_NORMALIZATION: dict[str, str | None] = {
    # PlantVillage
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

    # PlantDoc
    "Apple Scab Leaf":            "Apple_Apple_Scab",
    "Apple leaf":                 "Apple_Healthy",
    "Apple rust leaf":            "Apple_Cedar_Apple_Rust",
    "Bell_pepper leaf":           "Pepper_Healthy",
    "Bell_pepper leaf spot":      "Pepper_Bacterial_Spot",
    "Blueberry leaf":             "Blueberry_Healthy",
    "Cherry leaf":                "Cherry_Healthy",
    "Corn Gray leaf spot":        "Corn_Gray_Leaf_Spot",
    "Corn leaf blight":           "Corn_Northern_Leaf_Blight",
    "Corn rust leaf":             "Corn_Common_Rust",
    "grape leaf":                 "Grape_Healthy",
    "grape leaf black rot":       "Grape_Black_Rot",
    "Peach leaf":                 "Peach_Healthy",
    "Potato leaf early blight":   "Potato_Early_Blight",
    "Potato leaf late blight":    "Potato_Late_Blight",
    "Raspberry leaf":             "Raspberry_Healthy",
    "Soyabean leaf":              "Soybean_Healthy",
    "Squash Powdery mildew leaf": "Squash_Powdery_Mildew",
    "Strawberry leaf":            "Strawberry_Healthy",
    "Tomato Early blight leaf":   "Tomato_Early_Blight",
    "Tomato Septoria leaf spot":  "Tomato_Septoria_Leaf_Spot",
    "Tomato leaf":                "Tomato_Healthy",
    "Tomato leaf bacterial spot": "Tomato_Bacterial_Spot",
    "Tomato leaf late blight":    "Tomato_Late_Blight",
    "Tomato leaf mosaic virus":   "Tomato_Mosaic_Virus",
    "Tomato leaf yellow virus":   "Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato mold leaf":           "Tomato_Leaf_Mold",

    # Rice
    "BrownSpot":             "Rice_Brown_Spot",
    "Hispa":                 "Rice_Hispa",
    "LeafBlast":             "Rice_Leaf_Blast",
    "Bacterial Leaf Blight": "Rice_Bacterial_Leaf_Blight",
    "Bacterial leaf blight": "Rice_Bacterial_Leaf_Blight",
    "Brown Spot":            "Rice_Brown_Spot",
    "Brown spot":            "Rice_Brown_Spot",
    "Healthy Rice Leaf":     "Rice_Healthy",
    "Leaf Blast":            "Rice_Leaf_Blast",
    "Leaf scald":            "Rice_Leaf_Scald",
    "Sheath Blight":         "Rice_Sheath_Blight",
    "Leaf smut":             "Rice_Leaf_Smut",
    "RiceDiseaseDataset":    None,

    # Paddy
    "bacterial_leaf_blight":      "Paddy_Bacterial_Leaf_Blight",
    "bacterial_leaf_streak":      "Paddy_Bacterial_Leaf_Streak",
    "bacterial_panicle_blight":   "Paddy_Bacterial_Panicle_Blight",
    "blast":                      "Paddy_Blast",
    "brown_spot":                 "Paddy_Brown_Spot",
    "dead_heart":                 "Paddy_Dead_Heart",
    "downy_mildew":               "Paddy_Downy_Mildew",
    "hispa":                      "Paddy_Hispa",
    "normal":                     "Paddy_Healthy",
    "tungro":                     "Paddy_Tungro",

    # Mango
    "Anthracnose":      "Mango_Anthracnose",
    "Bacterial Canker": "Mango_Bacterial_Canker",
    "Cutting Weevil":   "Mango_Cutting_Weevil",
    "Die Back":         "Mango_Die_Back",
    "Gall Midge":       "Mango_Gall_Midge",
    "Healthy":          "Mango_Healthy",
    "Powdery Mildew":   "Mango_Powdery_Mildew",
    "Sooty Mould":      "Mango_Sooty_Mould",

    # Sugarcane
    "BacterialBlights":  "Sugarcane_Bacterial_Blight",
    "Mosaic":            "Sugarcane_Mosaic",
    "RedRot":            "Sugarcane_Red_Rot",
    "Rust":              "Sugarcane_Rust",
    "Yellow":            "Sugarcane_Yellow",
    "Healthy_Leaves":    "Sugarcane_Healthy",

    # Cotton
    "bacterial_blight":     "Cotton_Bacterial_Blight",
    "Bacterial blight":     "Cotton_Bacterial_Blight",
    "Bacterial Blight edited": "Cotton_Bacterial_Blight",
    "curl_virus":            "Cotton_Curl_Virus",
    "fussarium_wilt":        "Cotton_Fusarium_Wilt",
    "healthy":               "Cotton_Healthy",
    "Aphids":                "Cotton_Aphids",
    "Aphids edited":         "Cotton_Aphids",
    "Army worm":             "Cotton_Army_Worm",
    "Army worm edited":      "Cotton_Army_Worm",
    "Powdery mildew":        "Cotton_Powdery_Mildew",
    "Powdery Mildew Edited": "Cotton_Powdery_Mildew",
    "Target spot":           "Cotton_Target_Spot",
    "Target spot edited":    "Cotton_Target_Spot",
    "Insect Pest Disease":   "Cotton_Insect_Pest",
    "Diseased Leaf":         "Cotton_Disease",
    "Healthy leaf":          "Cotton_Healthy",
    "healthy leaf":          "Cotton_Healthy",
    "Healthy leaf edited":   "Cotton_Healthy",
    "Small Leaf Disease":    "Cotton_Small_Leaf",
    "White Mold Disease":    "Cotton_White_Mold",
    "Wilt Disease":          "Cotton_Wilt",

    # Corn
    "Blight":         "Corn_Northern_Leaf_Blight",
    "Common_Rust":    "Corn_Common_Rust",
    "Gray_Leaf_Spot": "Corn_Gray_Leaf_Spot",

    # Banana
    "cordana":        "Banana_Cordana",
    "pestalotiopsis": "Banana_Pestalotiopsis",
    "sigatoka":       "Banana_Sigatoka",
    "Banana_Healthy": "Banana_Healthy",

    # Tea
    "algal leaf":    "Tea_Algal_Leaf",
    "bird eye spot": "Tea_Bird_Eye_Spot",
    "brown blight":  "Tea_Brown_Blight",
    "gray light":    "Tea_Gray_Blight",
    "red leaf spot": "Tea_Red_Leaf_Spot",
    "white spot":    "Tea_White_Spot",
    "Tea_Healthy":   "Tea_Healthy",
    "1. Tea algal leaf spot": "Tea_Algal_Leaf",
    "2. Brown Blight":        "Tea_Brown_Blight",
    "3. Gray Blight":         "Tea_Gray_Blight",
    "4. Helopeltis":          "Tea_Helopeltis",
    "5. Red spider":          "Tea_Red_Spider",
    "6. Green mirid bug":     "Tea_Green_Mirid_Bug",
    "7. Healthy leaf":        "Tea_Healthy",

    # Coconut
    "WCLWD_DryingofLeaflets": "Coconut_Drying_Of_Leaflets",
    "WCLWD_Flaccidity":       "Coconut_Flaccidity",
    "WCLWD_Yellowing":        "Coconut_Yellowing",
    "CCI_Caterpillars":       "Coconut_Caterpillars",
    "CCI_Leaflets":           "Coconut_Healthy",

    # Eggplant
    "Eggplant Healthy Leaf":           "Eggplant_Healthy",
    "Eggplant Insect Pest Disease":    "Eggplant_Insect_Pest",
    "Eggplant Leaf Spot Disease":      "Eggplant_Leaf_Spot",
    "Eggplant Mosaic Virus Disease":   "Eggplant_Mosaic_Virus",
    "Eggplant Small Leaf Disease":     "Eggplant_Small_Leaf",
    "Eggplant White Mold Disease":     "Eggplant_White_Mold",
    "Eggplant Wilt Disease":           "Eggplant_Wilt",
    "Augmented Eggplant Healthy Leaf":        "Eggplant_Healthy",
    "Augmented Eggplant Insect Pest Disease": "Eggplant_Insect_Pest",
    "Augmented Eggplant Leaf Spot Disease":   "Eggplant_Leaf_Spot",
    "Augmented Eggplant Mosaic Virus Disease":"Eggplant_Mosaic_Virus",
    "Augmented Eggplant Small Leaf Disease":  "Eggplant_Small_Leaf",
    "Augmented Eggplant White Mold Disease":  "Eggplant_White_Mold",
    "Augmented Eggplant Wilt Disease":        "Eggplant_Wilt",
    "Augmented Healthy Leaf":        "Eggplant_Healthy",
    "Augmented Insect Pest Disease": "Eggplant_Insect_Pest",
    "Augmented Leaf Spot Disease":   "Eggplant_Leaf_Spot",
    "Augmented Mosaic Virus Disease":"Eggplant_Mosaic_Virus",
    "Augmented Small Leaf Disease":  "Eggplant_Small_Leaf",
    "Augmented White Mold Disease":  "Eggplant_White_Mold",
    "Augmented Wilt Disease":        "Eggplant_Wilt",

    # Okra
    "diseased okra leaf": "Okra_Yellow_Vein_Mosaic",
    "fresh okra leaf":    "Okra_Healthy",

    # Onion
    "Onion Anthracnose":        "Onion_Anthracnose",
    "Onion Purple Blotch":      "Onion_Purple_Blotch",
    "Onion Stemphylium Blight": "Onion_Stemphylium_Blight",
    "Onion Healthy":            "Onion_Healthy",

    # Groundnut / Peanut
    "early_leaf_spot":        "Groundnut_Early_Leaf_Spot",
    "early_leaf_spot_1":      "Groundnut_Early_Leaf_Spot",
    "early_rust_1":           "Groundnut_Early_Rust",
    "healthy_leaf_1":         "Groundnut_Healthy",
    "late_leaf_spot_1":       "Groundnut_Late_Leaf_Spot",
    "late leaf spot":         "Groundnut_Late_Leaf_Spot",
    "nutrition_deficiency_1": "Groundnut_Nutrition_Deficiency",
    "nutrition deficiency":   "Groundnut_Nutrition_Deficiency",
    "rust_1":                 "Groundnut_Rust",
    "rust":                   "Groundnut_Rust",
    "Dead Leaf":              "Peanut_Dead_Leaf",
    "Normal Leaf":            "Peanut_Healthy",

    # Sorghum
    "Anthracnose and Red Rot": "Sorghum_Anthracnose_Red_Rot",
    "Cereal Grain molds":      "Sorghum_Grain_Mold",
    "Covered Kernel smut":     "Sorghum_Covered_Kernel_Smut",
    "Head Smut":               "Sorghum_Head_Smut",
    "loose smut":              "Sorghum_Loose_Smut",

    # Skip / noise
    "Background_without_leaves": None,
    "miner_img_xml":  None,
    "rust_xml_image": None,
}


def process_directory(base_dir: Path):
    """Rename/merge class folders in base_dir to PlantName_DiseaseName."""
    if not base_dir.exists():
        print(f"  Directory not found: {base_dir}")
        return

    print(f"\nProcessing: {base_dir}")

    # Snapshot current folders before we start mutating
    folders = [f for f in base_dir.iterdir() if f.is_dir()]

    moves = 0
    removed = 0
    skipped = []

    for folder in folders:
        raw_name = folder.name

        # Already normalised (contains exactly one underscore and TitleCase) → skip
        if raw_name in CLASS_NORMALIZATION.values():
            continue

        # Look up mapping
        mapped = CLASS_NORMALIZATION.get(raw_name)
        if mapped is None:
            # Try case-insensitive
            lower = raw_name.lower()
            mapped = next(
                (v for k, v in CLASS_NORMALIZATION.items() if k.lower() == lower),
                "UNKNOWN",
            )

        if mapped == "UNKNOWN":
            skipped.append(raw_name)
            continue

        target = base_dir / mapped
        if target == folder:
            continue

        target.mkdir(exist_ok=True)

        for img in folder.iterdir():
            if img.is_file():
                dest = target / f"{raw_name}_{img.name}"
                shutil.move(str(img), str(dest))
                moves += 1

        try:
            folder.rmdir()
            removed += 1
            print(f"  ✓  '{raw_name}'  →  '{mapped}'")
        except OSError:
            print(f"  ⚠  Could not remove '{folder}' (not empty?)")

    print(f"  Moved {moves} files, removed {removed} old folders.")
    if skipped:
        print(f"  Skipped (unmapped): {skipped}")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    DATASET_DIR = Path(r"c:\Users\udhay\Aathi\plant-disease\dataset")

    print("=" * 60)
    print("Plant Disease Class Deduplication & Standardisation")
    print("=" * 60)

    process_directory(DATASET_DIR / "train")
    process_directory(DATASET_DIR / "val")

    print("\n✅ All class folders standardised to PlantName_DiseaseName!")
