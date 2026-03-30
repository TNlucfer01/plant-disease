#!/usr/bin/env python3
"""
================================================================================
  PLANT DISEASE DATASET DOWNLOADER — PART 2 (MISSING CROPS)
  Supplements download_plant_disease_datasets.py
  
  Covers the crops from the Tamil Nadu document that were NOT in Part 1:
    ✅ Cassava (Tapioca)
    ✅ Brinjal / Eggplant
    ✅ Bhendi / Okra (Yellow Vein Mosaic)
    ✅ Onion
    ✅ Cotton
    ✅ Groundnut (Peanut)
    ✅ Coffee
    ✅ Coconut
    ✅ Sorghum (Cholam)

DATASETS INCLUDED:
  [17] Cassava Leaf Disease Classification  — Kaggle Competition — 21,397 imgs / 5 classes
  [18] Eggplant Disease Recognition         — Kaggle Dataset    — multiple classes
  [19] Eggplant Leaf Disease (High Quality) — Kaggle Dataset    — multiple classes
  [20] Okra Yellow Vein Mosaic Disease      — Kaggle Dataset    — 2 classes
  [21] Onion Datasets (kiranghule)          — Kaggle Dataset    — disease/healthy
  [22] Cotton Leaf Disease (seroshkarim)    — Kaggle Dataset    — multiple classes
  [23] Cotton Plant Disease (dhamur)        — Kaggle Dataset    — multiple classes
  [24] Groundnut Plant Leaf Data (warcoder) — Kaggle Dataset    — multiple classes
  [25] Peanut Plant Leaf Disease            — Kaggle Dataset    — multiple classes
  [26] Coffee Leaf Diseases (badasstechie) — Kaggle Dataset    — Rust, Miner, Healthy
  [27] Coffee Leaves Disease (alvarole)    — Kaggle Dataset    — disease + pest
  [28] Coconut Disease & Pest Infestation  — Kaggle Dataset    — multiple classes
  [29] Sorghum Disease Image Dataset       — Kaggle Dataset    — Anthracnose, Smuts, etc.

PREREQUISITES: Same as Part 1
  pip install kaggle tqdm requests gitpython

KAGGLE SETUP: Same as Part 1
  ~/.kaggle/kaggle.json must exist with your credentials.

USAGE:
  python download_missing_crops.py

NOTE: Run this AFTER download_plant_disease_datasets.py
      Both scripts share the same BASE_DIR and are safe to run together.
================================================================================
"""

import os
import sys
import json
import time
import shutil
import zipfile
import subprocess
import traceback
from pathlib import Path
from datetime import datetime

# ──────────────────────────────────────────────
#  CONFIGURATION
# ──────────────────────────────────────────────
CONFIG = {
    "BASE_DIR": "./plant_disease_datasets",   # Same folder as Part 1
    "RETRY_COUNT": 3,
    "RETRY_DELAY_SECONDS": 5,
    "SKIP_EXISTING": True,
    "UNZIP": True,
    "DELETE_ZIP_AFTER_UNZIP": True,
    "LOG_FILE": "download_log_part2.txt",
}

# ──────────────────────────────────────────────
#  MISSING CROP DATASET REGISTRY
# ──────────────────────────────────────────────
DATASETS = [
    # ── CASSAVA (TAPIOCA) ──────────────────────────────────────────────────
    {
        "id": 17,
        "crop": "Cassava (Tapioca)",
        "name": "Cassava Leaf Disease Classification (Competition)",
        "type": "kaggle_competition",
        "slug": "cassava-leaf-disease-classification",
        "folder": "17_cassava_competition",
        "description": "21,397 images | 5 classes: CBB, CBSD, CGM, CMD, Healthy | Crowdsourced from farmers",
        "license": "Competition rules apply",
        "source_url": "https://www.kaggle.com/competitions/cassava-leaf-disease-classification",
        "note": "Must accept competition rules at the URL above before downloading.",
    },

    # ── BRINJAL / EGGPLANT ────────────────────────────────────────────────
    {
        "id": 18,
        "crop": "Brinjal (Eggplant)",
        "name": "Eggplant Disease Recognition Dataset (sujaykapadnis)",
        "type": "kaggle_dataset",
        "slug": "sujaykapadnis/eggplant-disease-recognition-dataset",
        "folder": "18_eggplant_disease_sujay",
        "description": "Multi-class eggplant leaf disease classification dataset",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/sujaykapadnis/eggplant-disease-recognition-dataset",
    },
    {
        "id": 19,
        "crop": "Brinjal (Eggplant)",
        "name": "Eggplant Leaf Disease Dataset — High Quality (researchforus)",
        "type": "kaggle_dataset",
        "slug": "researchforus/eggplant-leaf-disease-dataset",
        "folder": "19_eggplant_leaf_hq",
        "description": "High-quality images of eggplant leaf diseases for pathology and image classification",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/researchforus/eggplant-leaf-disease-dataset",
    },

    # ── BHENDI / OKRA ─────────────────────────────────────────────────────
    {
        "id": 20,
        "crop": "Bhendi (Okra / Ladyfinger)",
        "name": "Yellow Vein Mosaic Disease — Okra (manojgadde)",
        "type": "kaggle_dataset",
        "slug": "manojgadde/yellow-vein-mosaic-disease",
        "folder": "20_okra_yellow_vein_mosaic",
        "description": "Okra/Ladyfinger Yellow Vein Mosaic Disease vs Healthy classification",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/manojgadde/yellow-vein-mosaic-disease",
    },

    # ── ONION ──────────────────────────────────────────────────────────────
    {
        "id": 21,
        "crop": "Onion",
        "name": "Onion Datasets (kiranghule)",
        "type": "kaggle_dataset",
        "slug": "kiranghule/onion-datasets",
        "folder": "21_onion_disease",
        "description": "Onion plant disease and healthy classification images",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/kiranghule/onion-datasets",
    },

    # ── COTTON ────────────────────────────────────────────────────────────
    {
        "id": 22,
        "crop": "Cotton",
        "name": "Cotton Leaf Disease Dataset (seroshkarim)",
        "type": "kaggle_dataset",
        "slug": "seroshkarim/cotton-leaf-disease-dataset",
        "folder": "22_cotton_leaf_disease",
        "description": "Cotton leaf disease detection — multiple disease classes",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/seroshkarim/cotton-leaf-disease-dataset",
    },
    {
        "id": 23,
        "crop": "Cotton",
        "name": "Cotton Plant Disease (dhamur)",
        "type": "kaggle_dataset",
        "slug": "dhamur/cotton-plant-disease",
        "folder": "23_cotton_plant_dhamur",
        "description": "Cotton plant disease images for CNN-based detection",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/dhamur/cotton-plant-disease",
    },

    # ── GROUNDNUT ─────────────────────────────────────────────────────────
    {
        "id": 24,
        "crop": "Groundnut (Peanut)",
        "name": "Groundnut Plant Leaf Data (warcoder)",
        "type": "kaggle_dataset",
        "slug": "warcoder/groundnut-plant-leaf-data",
        "folder": "24_groundnut_warcoder",
        "description": "Groundnut/Peanut leaf disease dataset with healthy and diseased classes",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/warcoder/groundnut-plant-leaf-data",
    },
    {
        "id": 25,
        "crop": "Groundnut (Peanut)",
        "name": "Peanut Plant Leaf Disease (abhimanuer)",
        "type": "kaggle_dataset",
        "slug": "abhimanuer/peanut-plant-leaf-disease",
        "folder": "25_peanut_leaf_disease",
        "description": "Peanut/groundnut leaf disease classification dataset (2024)",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/abhimanuer/peanut-plant-leaf-disease",
    },

    # ── COFFEE ────────────────────────────────────────────────────────────
    {
        "id": 26,
        "crop": "Coffee",
        "name": "Coffee Leaf Diseases (badasstechie)",
        "type": "kaggle_dataset",
        "slug": "badasstechie/coffee-leaf-diseases",
        "folder": "26_coffee_leaf_badasstechie",
        "description": "Coffee leaf diseases — Rust, Miner, Healthy",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/badasstechie/coffee-leaf-diseases",
    },
    {
        "id": 27,
        "crop": "Coffee",
        "name": "Disease and Pest in Coffee Leaves (alvarole)",
        "type": "kaggle_dataset",
        "slug": "alvarole/coffee-leaves-disease",
        "folder": "27_coffee_leaves_pest",
        "description": "Coffee leaf disease AND pest infestation images — broader coverage",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/alvarole/coffee-leaves-disease",
    },

    # ── COCONUT ───────────────────────────────────────────────────────────
    {
        "id": 28,
        "crop": "Coconut",
        "name": "Coconut Disease and Pest Infestation Dataset (samitha96)",
        "type": "kaggle_dataset",
        "slug": "samitha96/coconutdiseases",
        "folder": "28_coconut_disease_pest",
        "description": "Coconut palm disease and pest classification images",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/samitha96/coconutdiseases",
    },

    # ── SORGHUM (CHOLAM) ──────────────────────────────────────────────────
    {
        "id": 29,
        "crop": "Sorghum (Cholam)",
        "name": "Sorghum Disease Image Dataset (rogfsdafdsafdsa)",
        "type": "kaggle_dataset",
        "slug": "rogfsdafdsafdsa/sorghum",
        "folder": "29_sorghum_disease",
        "description": "Sorghum diseases — Anthracnose, Grain Molds, Smuts, and more",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/rogfsdafdsafdsa/sorghum",
    },
]

# ──────────────────────────────────────────────
#  LOGGING
# ──────────────────────────────────────────────

class Logger:
    def __init__(self, log_path):
        self.log_path = log_path
        self.entries = []

    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{level}] {msg}"
        print(line)
        self.entries.append(line)

    def save(self):
        with open(self.log_path, "w") as f:
            f.write("\n".join(self.entries))

    def info(self, msg):  self.log(msg, "INFO")
    def warn(self, msg):  self.log(msg, "WARN")
    def error(self, msg): self.log(msg, "ERROR")
    def ok(self, msg):    self.log(msg, "OK  ")


# ──────────────────────────────────────────────
#  UTILITIES
# ──────────────────────────────────────────────

def check_and_install_dependencies(logger):
    required = {"kaggle": "kaggle", "tqdm": "tqdm", "requests": "requests"}
    missing = []
    for module, pkg in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(pkg)
    if missing:
        logger.warn(f"Missing packages: {missing}. Installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install"] + missing,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        logger.ok("Packages installed.")


def validate_kaggle_credentials(logger):
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        logger.ok("Kaggle credentials found in environment variables.")
        return True
    p = Path.home() / ".kaggle" / "kaggle.json"
    if p.exists():
        try:
            with open(p) as f:
                creds = json.load(f)
            if "username" in creds and "key" in creds:
                logger.ok(f"Kaggle credentials: {p}")
                if sys.platform != "win32":
                    os.chmod(p, 0o600)
                return True
        except Exception as e:
            logger.warn(f"Could not read kaggle.json: {e}")

    logger.error("KAGGLE CREDENTIALS NOT FOUND! See Part 1 script for setup steps.")
    return False


def already_downloaded(folder_path: Path, logger) -> bool:
    if not folder_path.exists():
        return False
    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    count = sum(1 for f in folder_path.rglob("*") if f.suffix.lower() in image_exts)
    if count > 0:
        logger.info(f"  ↳ Already downloaded ({count} images). Skipping.")
        return True
    return False


def unzip_all(folder_path: Path, delete_after: bool, logger):
    for zip_path in folder_path.rglob("*.zip"):
        try:
            logger.info(f"  ↳ Unzipping: {zip_path.name}")
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(zip_path.parent)
            if delete_after:
                zip_path.unlink()
        except Exception as e:
            logger.warn(f"  ↳ Unzip failed for {zip_path.name}: {e}")


# ──────────────────────────────────────────────
#  DOWNLOADERS
# ──────────────────────────────────────────────

def download_kaggle_dataset(dataset, base_dir, config, logger) -> bool:
    folder_path = base_dir / dataset["folder"]
    folder_path.mkdir(parents=True, exist_ok=True)
    if config["SKIP_EXISTING"] and already_downloaded(folder_path, logger):
        return True

    for attempt in range(1, config["RETRY_COUNT"] + 1):
        try:
            logger.info(f"  ↳ Attempt {attempt}: kaggle datasets download -d {dataset['slug']}")
            result = subprocess.run(
                ["kaggle", "datasets", "download", "-d", dataset["slug"],
                 "--path", str(folder_path), "--unzip"],
                capture_output=True, text=True, timeout=3600
            )
            if result.returncode == 0:
                logger.ok(f"  ↳ Success → {folder_path}")
                return True
            else:
                err = result.stderr.strip() or result.stdout.strip()
                logger.warn(f"  ↳ Error: {err}")
                if "403" in err or "forbidden" in err.lower():
                    logger.warn(f"  ↳ Accept license at: {dataset['source_url']}")
                    return False
                if attempt < config["RETRY_COUNT"]:
                    time.sleep(config["RETRY_DELAY_SECONDS"])
        except subprocess.TimeoutExpired:
            logger.warn(f"  ↳ Timeout on attempt {attempt}.")
            if attempt < config["RETRY_COUNT"]:
                time.sleep(config["RETRY_DELAY_SECONDS"])
        except FileNotFoundError:
            logger.error("  ↳ 'kaggle' command not found! Run: pip install kaggle")
            return False
        except Exception as e:
            logger.warn(f"  ↳ Exception on attempt {attempt}: {e}")
            if attempt < config["RETRY_COUNT"]:
                time.sleep(config["RETRY_DELAY_SECONDS"])

    logger.error(f"  ↳ All attempts failed: {dataset['name']}")
    return False


def download_kaggle_competition(dataset, base_dir, config, logger) -> bool:
    folder_path = base_dir / dataset["folder"]
    folder_path.mkdir(parents=True, exist_ok=True)
    if config["SKIP_EXISTING"] and already_downloaded(folder_path, logger):
        return True

    for attempt in range(1, config["RETRY_COUNT"] + 1):
        try:
            logger.info(f"  ↳ Attempt {attempt}: kaggle competitions download -c {dataset['slug']}")
            result = subprocess.run(
                ["kaggle", "competitions", "download", "-c", dataset["slug"],
                 "--path", str(folder_path)],
                capture_output=True, text=True, timeout=3600
            )
            if result.returncode == 0:
                logger.ok(f"  ↳ Success → {folder_path}")
                if config["UNZIP"]:
                    unzip_all(folder_path, config["DELETE_ZIP_AFTER_UNZIP"], logger)
                return True
            else:
                err = result.stderr.strip() or result.stdout.strip()
                logger.warn(f"  ↳ Error: {err}")
                if "must accept" in err.lower() or "403" in err:
                    logger.warn(f"  ↳ Accept rules at: {dataset['source_url']}")
                    return False
                if attempt < config["RETRY_COUNT"]:
                    time.sleep(config["RETRY_DELAY_SECONDS"])
        except subprocess.TimeoutExpired:
            logger.warn(f"  ↳ Timeout on attempt {attempt}.")
            if attempt < config["RETRY_COUNT"]:
                time.sleep(config["RETRY_DELAY_SECONDS"])
        except Exception as e:
            logger.warn(f"  ↳ Exception: {e}")
            if attempt < config["RETRY_COUNT"]:
                time.sleep(config["RETRY_DELAY_SECONDS"])

    logger.error(f"  ↳ All attempts failed: {dataset['name']}")
    return False


# ──────────────────────────────────────────────
#  SUMMARY
# ──────────────────────────────────────────────

def print_summary(results, base_dir, logger):
    successful = [r for r in results if r["status"] == "SUCCESS"]
    failed     = [r for r in results if r["status"] == "FAILED"]
    skipped    = [r for r in results if r["status"] == "SKIPPED"]

    print("\n" + "=" * 70)
    print("  PART 2 — MISSING CROPS DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"  ✅  Successful : {len(successful)}")
    print(f"  ⏭️  Skipped    : {len(skipped)}")
    print(f"  ❌  Failed     : {len(failed)}")
    print("=" * 70)

    # Group by crop
    crops_seen = {}
    for r in results:
        crop = r.get("crop", "Unknown")
        if crop not in crops_seen:
            crops_seen[crop] = []
        crops_seen[crop].append(r)

    print("\n  BY CROP:")
    for crop, entries in crops_seen.items():
        statuses = [e["status"] for e in entries]
        icon = "✅" if all(s == "SUCCESS" or s == "SKIPPED" for s in statuses) else "❌"
        print(f"    {icon}  {crop}")
        for e in entries:
            status_icon = {"SUCCESS": "✅", "SKIPPED": "⏭️", "FAILED": "❌"}.get(e["status"], "?")
            print(f"         {status_icon} [{e['id']:02d}] {e['name']}")

    if failed:
        print("\n  MANUAL ACTION NEEDED FOR FAILED DATASETS:")
        for r in failed:
            print(f"\n    [{r['id']:02d}] {r['name']}")
            print(f"         Visit: {r['source_url']}")
            if "note" in r:
                print(f"         Note:  {r['note']}")

    try:
        total_size = sum(
            f.stat().st_size for f in Path(base_dir).rglob("*") if f.is_file()
        )
        print(f"\n  Total data (both parts): {total_size / (1024**3):.2f} GB")
    except Exception:
        pass

    print(f"\n  Base directory: {Path(base_dir).resolve()}")
    print("=" * 70)


# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    base_dir = Path(CONFIG["BASE_DIR"])
    base_dir.mkdir(parents=True, exist_ok=True)

    log_path = base_dir / CONFIG["LOG_FILE"]
    logger = Logger(str(log_path))

    print("=" * 70)
    print("  🌿  PLANT DISEASE DATASET DOWNLOADER — PART 2 (MISSING CROPS)")
    print(f"  📁  Output directory : {base_dir.resolve()}")
    print(f"  🌱  Crops covered    : Cassava, Eggplant, Okra, Onion, Cotton,")
    print(f"                         Groundnut, Coffee, Coconut, Sorghum")
    print(f"  📋  Datasets to fetch: {len(DATASETS)}")
    print("=" * 70 + "\n")

    check_and_install_dependencies(logger)
    kaggle_ok = validate_kaggle_credentials(logger)

    if not kaggle_ok:
        logger.warn("Kaggle credentials missing. All datasets require Kaggle. Exiting.")
        sys.exit(1)

    results = []

    for i, dataset in enumerate(DATASETS, 1):
        print(f"\n{'─'*70}")
        print(f"  [{i:02d}/{len(DATASETS)}] {dataset['name']}")
        print(f"  🌱  Crop   : {dataset['crop']}")
        print(f"  📌  Info   : {dataset['description']}")
        print(f"  🔗  Source : {dataset['source_url']}")
        if "note" in dataset:
            print(f"  ⚠️   Note   : {dataset['note']}")
        print(f"  📂  Folder : {CONFIG['BASE_DIR']}/{dataset['folder']}")
        print(f"{'─'*70}")

        result_entry = {
            "id": dataset["id"],
            "crop": dataset["crop"],
            "name": dataset["name"],
            "source_url": dataset["source_url"],
            "status": "FAILED",
        }
        if "note" in dataset:
            result_entry["note"] = dataset["note"]

        try:
            dtype = dataset["type"]
            folder_path = base_dir / dataset["folder"]

            if dtype == "kaggle_dataset":
                if CONFIG["SKIP_EXISTING"] and already_downloaded(folder_path, logger):
                    result_entry["status"] = "SKIPPED"
                else:
                    ok = download_kaggle_dataset(dataset, base_dir, CONFIG, logger)
                    result_entry["status"] = "SUCCESS" if ok else "FAILED"

            elif dtype == "kaggle_competition":
                if CONFIG["SKIP_EXISTING"] and already_downloaded(folder_path, logger):
                    result_entry["status"] = "SKIPPED"
                else:
                    ok = download_kaggle_competition(dataset, base_dir, CONFIG, logger)
                    result_entry["status"] = "SUCCESS" if ok else "FAILED"

            else:
                logger.warn(f"  ↳ Unknown type: {dtype}")
                result_entry["status"] = "SKIPPED"

        except KeyboardInterrupt:
            logger.warn("  ↳ Interrupted. Saving progress...")
            results.append(result_entry)
            break
        except Exception as e:
            logger.error(f"  ↳ Exception: {e}")
            logger.error(traceback.format_exc())

        results.append(result_entry)

    logger.save()
    print_summary(results, base_dir, logger)

    failed_count = sum(1 for r in results if r["status"] == "FAILED")
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()
