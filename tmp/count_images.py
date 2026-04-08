import os
from pathlib import Path
import json

def count_images_in_dataset(dataset_path):
    dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        return f"Error: {dataset_path} does not exist"

    results = {"train": {}, "val": {}}
    
    for split in ["train", "val"]:
        split_path = dataset_path / split
        if split_path.exists():
            for class_dir in split_path.iterdir():
                if class_dir.is_dir():
                    count = len(list(class_dir.glob("*.[jJ][pP][gG]"))) + \
                            len(list(class_dir.glob("*.[jJ][pP][eE][gG]"))) + \
                            len(list(class_dir.glob("*.[pP][nN][gG]")))
                    results[split][class_dir.name] = count
        else:
             print(f"Split path {split_path} not found")

    return results

if __name__ == "__main__":
    counts = count_images_in_dataset("dataset")
    print(json.dumps(counts, indent=4))
