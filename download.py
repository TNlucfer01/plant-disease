#!/usr/bin/env python3
"""
================================================================================
  PLANT DISEASE DATASET DOWNLOADER
  For CNN Model Training — Tamil Nadu & General Agriculture Use
  Covers: Rice, Sugarcane, Mango, Banana, Tomato, Maize, Potato, Tea,
          Rubber, Cassava, and more (38+ disease classes)
================================================================================

DATASETS INCLUDED:
  [1]  New Plant Diseases Dataset       — Kaggle  — 87,000 imgs / 38 classes
  [2]  PlantVillage Dataset             — Kaggle  — 54,000+ imgs / 38 classes
  [3]  PlantDoc (Classification)        — Kaggle  — 2,598 imgs  / 27 classes (real-world)
  [4]  Rice Disease Dataset             — Kaggle  — 3,829 imgs  / 6 classes
  [5]  Rice Leaf Diseases               — Kaggle  — ~120 imgs   / 4 classes
  [6]  Rice Diseases Image Dataset      — Kaggle  — 3 classes
  [7]  Paddy Disease Classification     — Kaggle  — 10,000+ imgs / 10 classes
  [8]  Mango Leaf Disease Dataset       — Kaggle  — 4,000 imgs  / 8 classes
  [9]  Sugarcane Plant Diseases         — Kaggle  — 19,926 imgs / 6 classes
  [10] Sugarcane Leaf Disease           — Kaggle  — ~3,000 imgs / multiple classes
  [11] Corn/Maize Leaf Disease          — Kaggle  — 4 classes
  [12] Banana Leaf Spot (BananaLSD)     — Kaggle  — 4 classes
  [13] Tea Leaf Disease (shashwatwork)  — Kaggle  — 7 classes
  [14] Tea Leaf Disease (teaLeafBD)     — Kaggle  — multiple classes
  [15] Rubber Leaf Disease              — Kaggle  — 5 classes
  [16] PlantDoc (abdulhasib)            — Kaggle  — 2,598 imgs  / 27 classes
  [17] PlantDoc Classification (GitHub) — GitHub  — 2,598 imgs  / 27 classes

PREREQUISITES (run once):
  pip install kaggle tqdm requests gitpython

KAGGLE SETUP (run once):
  1. Go to https://www.kaggle.com → Account → Create New API Token
  2. This downloads kaggle.json to your ~/Downloads/
  3. Place it at:
       Linux/Mac:  ~/.kaggle/kaggle.json
       Windows:    C:/Users/<YourName>/.kaggle/kaggle.json
  4. Run: chmod 600 ~/.kaggle/kaggle.json   (Linux/Mac only)

USAGE:
  python download_plant_disease_datasets.py

  Options (edit CONFIG below):
    BASE_DIR      — where datasets are saved   (default: ./plant_disease_datasets)
    RETRY_COUNT   — download retry attempts    (default: 3)
    SKIP_EXISTING — skip already-downloaded    (default: True)
================================================================================
"""

import os
import sys
import json
import time
import shutil
import zipfile
import hashlib
import subprocess
import traceback
from pathlib import Path
from datetime import datetime

# ──────────────────────────────────────────────
#  CONFIGURATION  (edit these if needed)
# ──────────────────────────────────────────────
CONFIG = {
    "BASE_DIR": "./plant_disease_datasets",
    "RETRY_COUNT": 3,
    "RETRY_DELAY_SECONDS": 5,
    "SKIP_EXISTING": True,          # Set False to re-download everything
    "UNZIP": True,                  # Auto-unzip downloaded zips
    "DELETE_ZIP_AFTER_UNZIP": True, # Save disk space
    "LOG_FILE": "download_log.txt",
}

# ──────────────────────────────────────────────
#  DATASET REGISTRY
# ──────────────────────────────────────────────
# Format for Kaggle datasets:
#   { "type": "kaggle_dataset", "slug": "<owner>/<dataset-name>", ... }
# Format for Kaggle competitions:
#   { "type": "kaggle_competition", "slug": "<competition-name>", ... }
# Format for GitHub repos:
#   { "type": "github", "url": "<repo-url>", ... }

DATASETS = [
    {
        "id": 1,
        "name": "New Plant Diseases Dataset",
        "type": "kaggle_dataset",
        "slug": "vipoooool/new-plant-diseases-dataset",
        "folder": "01_new_plant_diseases",
        "description": "87,000 RGB images | 38 classes | Tomato, Maize, Potato, Pepper, Grape, etc.",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset",
    },
    {
        "id": 2,
        "name": "PlantVillage Dataset",
        "type": "kaggle_dataset",
        "slug": "mohitsingh1804/plantvillage",
        "folder": "02_plantvillage",
        "description": "54,000+ images | 38 classes | Controlled-lab images | Gold standard benchmark",
        "license": "CC0 Public Domain",
        "source_url": "https://www.kaggle.com/datasets/mohitsingh1804/plantvillage",
    },
    {
        "id": 3,
        "name": "PlantDoc Dataset (Classification) — abdulhasib",
        "type": "kaggle_dataset",
        "slug": "abdulhasibuddin/plant-doc-dataset",
        "folder": "03_plantdoc_abdulhasib",
        "description": "2,598 images | 27 classes | Real-world images (not lab-controlled)",
        "license": "CC BY 4.0",
        "source_url": "https://www.kaggle.com/datasets/abdulhasibuddin/plant-doc-dataset",
    },
    {
        "id": 4,
        "name": "Rice Disease Dataset (anshulm257)",
        "type": "kaggle_dataset",
        "slug": "anshulm257/rice-disease-dataset",
        "folder": "04_rice_disease_anshul",
        "description": "3,829 images | 6 classes: Bacterial Leaf Blight, Brown Spot, Healthy, Leaf Blast, Leaf Scald, Sheath Blight",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/anshulm257/rice-disease-dataset",
    },
    {
        "id": 5,
        "name": "Rice Leaf Diseases (vbookshelf)",
        "type": "kaggle_dataset",
        "slug": "vbookshelf/rice-leaf-diseases",
        "folder": "05_rice_leaf_vbookshelf",
        "description": "~120 images | 4 classes: BrownSpot, Hispa, LeafBlast, Healthy",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases",
    },
    {
        "id": 6,
        "name": "Rice Diseases Image Dataset (minhhuy2810)",
        "type": "kaggle_dataset",
        "slug": "minhhuy2810/rice-diseases-image-dataset",
        "folder": "06_rice_diseases_minhhuy",
        "description": "Multiple classes: Leaf Blast, Brown Spot, Bacterial Blight",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/minhhuy2810/rice-diseases-image-dataset",
    },
    {
        "id": 7,
        "name": "Paddy Disease Classification (Competition Dataset)",
        "type": "kaggle_competition",
        "slug": "paddy-disease-classification",
        "folder": "07_paddy_disease_competition",
        "description": "10,000+ images | 10 disease classes + 1 healthy | Competition benchmark",
        "license": "Competition rules apply",
        "source_url": "https://www.kaggle.com/competitions/paddy-disease-classification",
    },
    {
        "id": 8,
        "name": "Mango Leaf Disease Dataset (aryashah2k)",
        "type": "kaggle_dataset",
        "slug": "aryashah2k/mango-leaf-disease-dataset",
        "folder": "08_mango_leaf_disease",
        "description": "4,000 images | 8 classes: Anthracnose, Bacterial Canker, Cutting Weevil, Die Back, Gall Midge, Healthy, Powdery Mildew, Sooty Mould",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/aryashah2k/mango-leaf-disease-dataset",
    },
    {
        "id": 9,
        "name": "Sugarcane Plant Diseases Dataset (akilesh253)",
        "type": "kaggle_dataset",
        "slug": "akilesh253/sugarcane-plant-diseases-dataset",
        "folder": "09_sugarcane_akilesh",
        "description": "19,926 images | 6 classes: Bacterial Blight, Healthy, Mosaic, Red Rot, Rust, Yellow",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/akilesh253/sugarcane-plant-diseases-dataset",
    },
    {
        "id": 10,
        "name": "Sugarcane Leaf Disease Dataset (nirmalsankalana)",
        "type": "kaggle_dataset",
        "slug": "nirmalsankalana/sugarcane-leaf-disease-dataset",
        "folder": "10_sugarcane_nirmal",
        "description": "Multiple disease classes for sugarcane leaf identification",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/nirmalsankalana/sugarcane-leaf-disease-dataset",
    },
    {
        "id": 11,
        "name": "Corn/Maize Leaf Disease Dataset (smaranjitghose)",
        "type": "kaggle_dataset",
        "slug": "smaranjitghose/corn-or-maize-leaf-disease-dataset",
        "folder": "11_corn_maize_disease",
        "description": "4 classes: Common Rust, Gray Leaf Spot, Blight, Healthy | Built from PlantVillage + PlantDoc",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/smaranjitghose/corn-or-maize-leaf-disease-dataset",
    },
    {
        "id": 12,
        "name": "Banana Leaf Spot Diseases — BananaLSD (shifatearman)",
        "type": "kaggle_dataset",
        "slug": "shifatearman/bananalsd",
        "folder": "12_banana_leaf_spot",
        "description": "4 classes: Sigatoka, Cordana, Pestalotiopsis, Healthy",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/shifatearman/bananalsd",
    },
    {
        "id": 13,
        "name": "Identifying Disease in Tea Leaves (shashwatwork)",
        "type": "kaggle_dataset",
        "slug": "shashwatwork/identifying-disease-in-tea-leafs",
        "folder": "13_tea_disease_shashwat",
        "description": "7 disease classes for tea leaves",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/shashwatwork/identifying-disease-in-tea-leafs",
    },
    {
        "id": 14,
        "name": "Tea Leaf Disease Detection — teaLeafBD (bmshahriaalam)",
        "type": "kaggle_dataset",
        "slug": "bmshahriaalam/tealeafbd-tea-leaf-disease-detection",
        "folder": "14_tea_leaf_bd",
        "description": "Multiple tea leaf disease classes for Bangladesh/South Asia teas",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/bmshahriaalam/tealeafbd-tea-leaf-disease-detection",
    },
    {
        "id": 15,
        "name": "Rubber Leaf Disease Final Dataset (kongkityeesai)",
        "type": "kaggle_dataset",
        "slug": "kongkityeesai/rubber-disease-final-datasetss",
        "folder": "15_rubber_leaf_disease",
        "description": "5 classes: Anthracnose, Black Spot, Leaf Blight, Powdery Mildew, Healthy",
        "license": "Unknown (check Kaggle page)",
        "source_url": "https://www.kaggle.com/datasets/kongkityeesai/rubber-disease-final-datasetss",
    },
    {
        "id": 16,
        "name": "PlantDoc Classification — GitHub (pratikkayal)",
        "type": "github",
        "url": "https://github.com/pratikkayal/PlantDoc-Dataset.git",
        "folder": "16_plantdoc_github",
        "description": "2,598 images | 27 classes | Official IIT Gandhinagar release | Real-world images",
        "license": "CC BY 4.0",
        "source_url": "https://github.com/pratikkayal/PlantDoc-Dataset",
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
#  DEPENDENCY CHECK
# ──────────────────────────────────────────────

def check_and_install_dependencies(logger):
    required = {
        "kaggle":    "kaggle",
        "tqdm":      "tqdm",
        "requests":  "requests",
        "git":       "gitpython",
    }
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
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.ok("Packages installed successfully.")
    else:
        logger.ok("All dependencies already installed.")


# ──────────────────────────────────────────────
#  KAGGLE API VALIDATION
# ──────────────────────────────────────────────

def validate_kaggle_credentials(logger):
    """Check that kaggle.json exists and is valid."""
    kaggle_json_paths = [
        Path.home() / ".kaggle" / "kaggle.json",
        Path(os.environ.get("KAGGLE_CONFIG_DIR", "~/.kaggle")).expanduser() / "kaggle.json",
    ]
    # Also accept env vars
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        logger.ok("Kaggle credentials found in environment variables.")
        return True

    for p in kaggle_json_paths:
        if p.exists():
            try:
                with open(p) as f:
                    creds = json.load(f)
                if "username" in creds and "key" in creds:
                    logger.ok(f"Kaggle credentials found at: {p}")
                    # Fix permissions on Unix
                    if sys.platform != "win32":
                        os.chmod(p, 0o600)
                    return True
            except Exception as e:
                logger.warn(f"Could not read {p}: {e}")

    logger.error("=" * 60)
    logger.error("KAGGLE CREDENTIALS NOT FOUND!")
    logger.error("=" * 60)
    logger.error("Steps to fix:")
    logger.error("  1. Go to https://www.kaggle.com → Account → Create New API Token")
    logger.error("  2. This downloads 'kaggle.json'")
    logger.error("  3. Place it at ~/.kaggle/kaggle.json")
    logger.error("  4. Run: chmod 600 ~/.kaggle/kaggle.json  (Linux/Mac)")
    logger.error("  OR set env vars: KAGGLE_USERNAME and KAGGLE_KEY")
    logger.error("=" * 60)
    return False


# ──────────────────────────────────────────────
#  UTILITIES
# ──────────────────────────────────────────────

def already_downloaded(folder_path: Path, logger) -> bool:
    """Return True if the folder exists and has image files."""
    if not folder_path.exists():
        return False
    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    count = sum(1 for f in folder_path.rglob("*") if f.suffix.lower() in image_exts)
    if count > 0:
        logger.info(f"  ↳ Already downloaded ({count} images found). Skipping.")
        return True
    return False


def unzip_all(folder_path: Path, delete_after: bool, logger):
    """Unzip all .zip files found in folder_path recursively."""
    zips = list(folder_path.rglob("*.zip"))
    if not zips:
        return
    for zip_path in zips:
        try:
            logger.info(f"  ↳ Unzipping: {zip_path.name}")
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(zip_path.parent)
            if delete_after:
                zip_path.unlink()
                logger.info(f"  ↳ Deleted zip: {zip_path.name}")
        except Exception as e:
            logger.warn(f"  ↳ Failed to unzip {zip_path.name}: {e}")


def print_progress_bar(current, total, prefix="", length=40):
    filled = int(length * current / max(total, 1))
    bar = "█" * filled + "─" * (length - filled)
    pct = 100 * current / max(total, 1)
    print(f"\r{prefix} |{bar}| {pct:.1f}% ({current}/{total})", end="", flush=True)
    if current >= total:
        print()


# ──────────────────────────────────────────────
#  KAGGLE DATASET DOWNLOADER
# ──────────────────────────────────────────────

def download_kaggle_dataset(dataset: dict, base_dir: Path, config: dict, logger) -> bool:
    """Download a Kaggle dataset using the Kaggle CLI."""
    folder_path = base_dir / dataset["folder"]
    folder_path.mkdir(parents=True, exist_ok=True)

    if config["SKIP_EXISTING"] and already_downloaded(folder_path, logger):
        return True

    slug = dataset["slug"]
    retries = config["RETRY_COUNT"]

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"  ↳ Attempt {attempt}/{retries}: kaggle datasets download -d {slug}")
            result = subprocess.run(
                ["kaggle", "datasets", "download", "-d", slug,
                 "--path", str(folder_path), "--unzip"],
                capture_output=True, text=True, timeout=3600
            )
            if result.returncode == 0:
                logger.ok(f"  ↳ Download successful → {folder_path}")
                return True
            else:
                err = result.stderr.strip() or result.stdout.strip()
                logger.warn(f"  ↳ Kaggle CLI returned error: {err}")
                # Specific known errors
                if "403" in err or "forbidden" in err.lower():
                    logger.warn("  ↳ You may need to accept the dataset license on Kaggle first.")
                    logger.warn(f"  ↳ Visit: {dataset['source_url']}")
                    return False  # No point retrying
                if attempt < retries:
                    logger.warn(f"  ↳ Retrying in {config['RETRY_DELAY_SECONDS']}s...")
                    time.sleep(config["RETRY_DELAY_SECONDS"])
        except subprocess.TimeoutExpired:
            logger.warn(f"  ↳ Attempt {attempt} timed out (>60min). Retrying...")
            time.sleep(config["RETRY_DELAY_SECONDS"])
        except FileNotFoundError:
            logger.error("  ↳ 'kaggle' command not found! Install it: pip install kaggle")
            return False
        except Exception as e:
            logger.warn(f"  ↳ Unexpected error on attempt {attempt}: {e}")
            if attempt < retries:
                time.sleep(config["RETRY_DELAY_SECONDS"])

    logger.error(f"  ↳ All {retries} attempts failed for: {dataset['name']}")
    return False


# ──────────────────────────────────────────────
#  KAGGLE COMPETITION DOWNLOADER
# ──────────────────────────────────────────────

def download_kaggle_competition(dataset: dict, base_dir: Path, config: dict, logger) -> bool:
    """Download a Kaggle competition dataset using the Kaggle CLI."""
    folder_path = base_dir / dataset["folder"]
    folder_path.mkdir(parents=True, exist_ok=True)

    if config["SKIP_EXISTING"] and already_downloaded(folder_path, logger):
        return True

    slug = dataset["slug"]
    retries = config["RETRY_COUNT"]

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"  ↳ Attempt {attempt}/{retries}: kaggle competitions download -c {slug}")
            result = subprocess.run(
                ["kaggle", "competitions", "download", "-c", slug,
                 "--path", str(folder_path)],
                capture_output=True, text=True, timeout=3600
            )
            if result.returncode == 0:
                logger.ok(f"  ↳ Competition data downloaded → {folder_path}")
                if config["UNZIP"]:
                    unzip_all(folder_path, config["DELETE_ZIP_AFTER_UNZIP"], logger)
                return True
            else:
                err = result.stderr.strip() or result.stdout.strip()
                logger.warn(f"  ↳ Kaggle CLI error: {err}")
                if "You must accept this competition" in err or "403" in err:
                    logger.warn(f"  ↳ Accept competition rules at: {dataset['source_url']}")
                    return False
                if attempt < retries:
                    time.sleep(config["RETRY_DELAY_SECONDS"])
        except subprocess.TimeoutExpired:
            logger.warn(f"  ↳ Timeout on attempt {attempt}.")
            if attempt < retries:
                time.sleep(config["RETRY_DELAY_SECONDS"])
        except Exception as e:
            logger.warn(f"  ↳ Error on attempt {attempt}: {e}")
            if attempt < retries:
                time.sleep(config["RETRY_DELAY_SECONDS"])

    logger.error(f"  ↳ All {retries} attempts failed for competition: {dataset['name']}")
    return False


# ──────────────────────────────────────────────
#  GITHUB REPO DOWNLOADER
# ──────────────────────────────────────────────

def download_github_repo(dataset: dict, base_dir: Path, config: dict, logger) -> bool:
    """Clone or pull a GitHub repository."""
    folder_path = base_dir / dataset["folder"]

    if folder_path.exists() and config["SKIP_EXISTING"]:
        # Check if it's a valid git repo
        if (folder_path / ".git").exists():
            logger.info(f"  ↳ Repo already cloned at {folder_path}. Pulling latest...")
            try:
                result = subprocess.run(
                    ["git", "-C", str(folder_path), "pull"],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    logger.ok("  ↳ Pulled latest changes.")
                    return True
            except Exception as e:
                logger.warn(f"  ↳ Git pull failed: {e}")
        elif already_downloaded(folder_path, logger):
            return True

    folder_path.mkdir(parents=True, exist_ok=True)
    url = dataset["url"]
    retries = config["RETRY_COUNT"]

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"  ↳ Attempt {attempt}/{retries}: git clone {url}")
            result = subprocess.run(
                ["git", "clone", "--depth", "1", url, str(folder_path)],
                capture_output=True, text=True, timeout=600
            )
            if result.returncode == 0:
                logger.ok(f"  ↳ Cloned → {folder_path}")
                return True
            else:
                err = result.stderr.strip()
                logger.warn(f"  ↳ Git clone error: {err}")
                if attempt < retries:
                    time.sleep(config["RETRY_DELAY_SECONDS"])
        except subprocess.TimeoutExpired:
            logger.warn(f"  ↳ Clone timed out on attempt {attempt}.")
            if attempt < retries:
                time.sleep(config["RETRY_DELAY_SECONDS"])
        except FileNotFoundError:
            logger.error("  ↳ 'git' not found! Install Git from https://git-scm.com/")
            return False
        except Exception as e:
            logger.warn(f"  ↳ Error on attempt {attempt}: {e}")
            if attempt < retries:
                time.sleep(config["RETRY_DELAY_SECONDS"])

    logger.error(f"  ↳ All {retries} attempts failed for: {dataset['name']}")
    return False


# ──────────────────────────────────────────────
#  SUMMARY REPORT
# ──────────────────────────────────────────────

def print_summary(results: list, base_dir: Path, logger):
    successful  = [r for r in results if r["status"] == "SUCCESS"]
    failed      = [r for r in results if r["status"] == "FAILED"]
    skipped     = [r for r in results if r["status"] == "SKIPPED"]

    print("\n" + "=" * 70)
    print("  DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"  ✅  Successful : {len(successful)}")
    print(f"  ⏭️  Skipped    : {len(skipped)}")
    print(f"  ❌  Failed     : {len(failed)}")
    print("=" * 70)

    if successful:
        print("\n  SUCCESSFULLY DOWNLOADED:")
        for r in successful:
            print(f"    [{r['id']:02d}] {r['name']}")

    if skipped:
        print("\n  SKIPPED (already present):")
        for r in skipped:
            print(f"    [{r['id']:02d}] {r['name']}")

    if failed:
        print("\n  FAILED (manual action needed):")
        for r in failed:
            print(f"    [{r['id']:02d}] {r['name']}")
            print(f"         → {r['source_url']}")

    # Disk usage
    try:
        total_size = sum(
            f.stat().st_size
            for f in Path(base_dir).rglob("*")
            if f.is_file()
        )
        gb = total_size / (1024 ** 3)
        print(f"\n  Total data downloaded: {gb:.2f} GB")
    except Exception:
        pass

    print(f"\n  Base directory : {Path(base_dir).resolve()}")
    print("=" * 70)

    # Print folder structure
    print("\n  FOLDER STRUCTURE:")
    for ds in DATASETS:
        folder = Path(base_dir) / ds["folder"]
        status = "✅" if folder.exists() else "❌"
        print(f"    {status}  {ds['folder']:40s} → {ds['name']}")
    print()


# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    base_dir = Path(CONFIG["BASE_DIR"])
    base_dir.mkdir(parents=True, exist_ok=True)

    log_path = base_dir / CONFIG["LOG_FILE"]
    logger = Logger(str(log_path))

    print("=" * 70)
    print("  🌿  PLANT DISEASE DATASET DOWNLOADER")
    print(f"  📁  Output directory : {base_dir.resolve()}")
    print(f"  📋  Datasets to fetch: {len(DATASETS)}")
    print("=" * 70 + "\n")

    # 1. Install dependencies
    logger.info("Step 1/3 — Checking dependencies...")
    check_and_install_dependencies(logger)

    # 2. Validate Kaggle credentials
    logger.info("Step 2/3 — Validating Kaggle credentials...")
    kaggle_ok = validate_kaggle_credentials(logger)
    if not kaggle_ok:
        logger.warn("Kaggle credentials missing. Kaggle datasets will be skipped.")

    # 3. Download each dataset
    logger.info("Step 3/3 — Starting downloads...\n")
    results = []

    for i, dataset in enumerate(DATASETS, 1):
        print(f"\n{'─'*70}")
        print(f"  [{i:02d}/{len(DATASETS)}] {dataset['name']}")
        print(f"  📌  {dataset['description']}")
        print(f"  🔗  {dataset['source_url']}")
        print(f"  📂  → {CONFIG['BASE_DIR']}/{dataset['folder']}")
        print(f"{'─'*70}")

        result_entry = {
            "id": dataset["id"],
            "name": dataset["name"],
            "source_url": dataset["source_url"],
            "status": "FAILED",
        }

        try:
            dtype = dataset["type"]

            if dtype == "kaggle_dataset":
                if not kaggle_ok:
                    logger.warn("  ↳ Skipping — Kaggle credentials not configured.")
                    result_entry["status"] = "SKIPPED"
                else:
                    folder_path = base_dir / dataset["folder"]
                    if CONFIG["SKIP_EXISTING"] and already_downloaded(folder_path, logger):
                        result_entry["status"] = "SKIPPED"
                    else:
                        ok = download_kaggle_dataset(dataset, base_dir, CONFIG, logger)
                        result_entry["status"] = "SUCCESS" if ok else "FAILED"

            elif dtype == "kaggle_competition":
                if not kaggle_ok:
                    logger.warn("  ↳ Skipping — Kaggle credentials not configured.")
                    result_entry["status"] = "SKIPPED"
                else:
                    folder_path = base_dir / dataset["folder"]
                    if CONFIG["SKIP_EXISTING"] and already_downloaded(folder_path, logger):
                        result_entry["status"] = "SKIPPED"
                    else:
                        ok = download_kaggle_competition(dataset, base_dir, CONFIG, logger)
                        result_entry["status"] = "SUCCESS" if ok else "FAILED"

            elif dtype == "github":
                ok = download_github_repo(dataset, base_dir, CONFIG, logger)
                result_entry["status"] = "SUCCESS" if ok else "FAILED"

            else:
                logger.warn(f"  ↳ Unknown dataset type: {dtype}")
                result_entry["status"] = "SKIPPED"

        except KeyboardInterrupt:
            logger.warn("  ↳ Interrupted by user. Saving progress...")
            results.append(result_entry)
            break
        except Exception as e:
            logger.error(f"  ↳ Unexpected exception: {e}")
            logger.error(traceback.format_exc())
            result_entry["status"] = "FAILED"

        results.append(result_entry)

    # Save log
    logger.save()

    # Print summary
    print_summary(results, base_dir, logger)

    # Exit code: 0 if no failures
    failed_count = sum(1 for r in results if r["status"] == "FAILED")
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()





# pip install kaggle tqdm requests gitpython

# python download_plant_disease_datasets.py
