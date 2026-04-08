"""
balance_dataset.py
------------------
Balances the prepared dataset so no single class dominates training.

Strategy:
  * Classes with MORE than max_per_class images -> randomly sample down (hard cap).
  * Classes with FEWER than min_per_class images -> duplicate images until they
    reach min_per_class (simple oversampling; augmentation happens in train.py).

Operates IN-PLACE on dataset/train and dataset/val independently.

Run:
    python tools/balance_dataset.py
    python tools/balance_dataset.py --max 1500 --min 300
    python tools/balance_dataset.py --dry-run   # shows what would change, no edits
"""

import os
import shutil
import random
import argparse
from pathlib import Path
from tqdm import tqdm


def get_class_counts(split_dir: Path) -> dict:
    return {
        cls.name: len([f for f in cls.iterdir() if f.is_file()])
        for cls in split_dir.iterdir()
        if cls.is_dir()
    }


def balance_split(split_dir, max_per_class, min_per_class, dry_run=False, seed=42):
    random.seed(seed)
    counts = get_class_counts(split_dir)

    print("\n" + "=" * 60)
    print(f"Balancing: {split_dir.name}   ({len(counts)} classes)")
    print(f"  Target range: {min_per_class} - {max_per_class} images per class")
    print("=" * 60)

    oversized  = {k: v for k, v in counts.items() if v > max_per_class}
    undersized = {k: v for k, v in counts.items() if v < min_per_class}
    already_ok = len(counts) - len(oversized) - len(undersized)

    print(f"  Over cap  (will trim)    : {len(oversized)} classes")
    print(f"  Under min (will upsample): {len(undersized)} classes")
    print(f"  Already balanced         : {already_ok} classes")

    if dry_run:
        print("\n[DRY RUN - no files will be changed]\n")
        print("Classes that WILL be trimmed:")
        for k, v in sorted(oversized.items(), key=lambda x: -x[1]):
            print(f"  {v:>6} -> {max_per_class}  {k}")
        print("\nClasses that WILL be upsampled:")
        for k, v in sorted(undersized.items(), key=lambda x: x[1]):
            print(f"  {v:>6} -> {min_per_class}  {k}")
        return

    # ── Trim oversized classes ────────────────────────────────────────────
    if oversized:
        print("\nTrimming oversized classes...")
        for cls_name in tqdm(oversized, desc="Trimming"):
            cls_dir = split_dir / cls_name
            all_files = [f for f in cls_dir.iterdir() if f.is_file()]
            random.shuffle(all_files)
            for f in all_files[max_per_class:]:
                f.unlink()

    # ── Upsample undersized classes ───────────────────────────────────────
    if undersized:
        print("\nUpsampling undersized classes...")
        for cls_name in tqdm(undersized, desc="Upsampling"):
            cls_dir = split_dir / cls_name
            existing = [f for f in cls_dir.iterdir() if f.is_file()]
            needed = min_per_class - len(existing)
            if not existing:
                print(f"  WARNING: {cls_name} has no images - skipping")
                continue
            # Cycle through existing images and duplicate with unique names
            cycle = (existing * ((needed // len(existing)) + 2))[:needed]
            for i, src in enumerate(cycle):
                dst = cls_dir / f"dup_{i}_{src.name}"
                if not dst.exists():
                    shutil.copy2(src, dst)

    # ── Summary ───────────────────────────────────────────────────────────
    new_counts = get_class_counts(split_dir)
    sizes = sorted(new_counts.values())
    print(f"\n  After balancing:")
    print(f"    Min: {min(sizes)}   Max: {max(sizes)}   Median: {sizes[len(sizes)//2]}")


def main():
    parser = argparse.ArgumentParser(description="Balance plant disease dataset classes.")
    parser.add_argument(
        "--dataset", type=str,
        default=r"c:\Users\udhay\Aathi\plant-disease\dataset",
        help="Path to the prepared dataset (must contain train/ and val/)",
    )
    parser.add_argument(
        "--max", type=int, default=1500,
        help="Max images per class (default 1500). Larger classes are trimmed.",
    )
    parser.add_argument(
        "--min", type=int, default=300,
        help="Min images per class (default 300). Smaller classes are upsampled.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without modifying any files.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    args = parser.parse_args()

    dataset_dir = Path(args.dataset)
    train_dir   = dataset_dir / "train"
    val_dir     = dataset_dir / "val"

    if not train_dir.exists():
        print(f"ERROR: {train_dir} not found. Run prepare_dataset.py first.")
        return

    # Val limits are proportionally smaller (~25% of train)
    val_max = max(50,  int(args.max * 0.25))
    val_min = max(20,  int(args.min * 0.25))

    balance_split(train_dir, max_per_class=args.max, min_per_class=args.min,
                  dry_run=args.dry_run, seed=args.seed)
    balance_split(val_dir,   max_per_class=val_max,  min_per_class=val_min,
                  dry_run=args.dry_run, seed=args.seed)

    if not args.dry_run:
        print("\nDataset balancing complete!")
        print(f"   Train: {args.min} - {args.max} images per class")
        print(f"   Val:   {val_min} - {val_max} images per class")


if __name__ == "__main__":
    main()
