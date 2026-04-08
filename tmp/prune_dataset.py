import os
import random
import argparse

def prune_dataset(base_dir, split_config, dry_run=True):
    """
    Prunes the dataset to keep image counts within specified ranges.
    
    Args:
        base_dir (str): Path to the dataset folder (containing train/val).
        split_config (dict): Target ranges for each split. e.g. {'train': (300, 500), 'val': (100, 200)}
        dry_run (bool): If True, don't delete files, just report.
    """
    print(f"{'Dry Run' if dry_run else 'EXECUTION'} - Pruning dataset at: {base_dir}")
    print("-" * 60)
    
    total_removed = 0
    
    for split, (min_target, max_target) in split_config.items():
        split_path = os.path.join(base_dir, split)
        if not os.path.exists(split_path):
            print(f"Warning: Split path {split_path} not found. Skipping.")
            continue
            
        print(f"\nProcessing split: {split.upper()} (Target: {min_target}-{max_target})")
        
        classes = sorted(os.listdir(split_path))
        for class_name in classes:
            class_path = os.path.join(split_path, class_name)
            if not os.path.isdir(class_path):
                continue
                
            files = [f for f in os.listdir(class_path) if os.path.isfile(os.path.join(class_path, f))]
            current_count = len(files)
            
            if current_count > max_target:
                num_to_remove = current_count - max_target
                files_to_remove = random.sample(files, num_to_remove)
                
                print(f"  {class_name:<30} | Current: {current_count:>4} | Removing: {num_to_remove:>4} | Final: {max_target}")
                
                if not dry_run:
                    for f in files_to_remove:
                        os.remove(os.path.join(class_path, f))
                
                total_removed += num_to_remove
            else:
                status = "OK" if current_count >= min_target else "UNDER LIMIT"
                print(f"  {class_name:<30} | Current: {current_count:>4} | Removing:    0 | Status: {status}")

    print("-" * 60)
    print(f"Total files {'to be removed' if dry_run else 'removed'}: {total_removed}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prune dataset to target ranges.")
    parser.add_argument("--execute", action="store_true", help="Actually delete the files.")
    args = parser.parse_args()
    
    DATASET_DIR = r"c:\Users\udhay\Aathi\plant-disease\dataset"
    CONFIG = {
        "train": (300, 500),
        "val": (100, 200)
    }
    
    prune_dataset(DATASET_DIR, CONFIG, dry_run=not args.execute)
