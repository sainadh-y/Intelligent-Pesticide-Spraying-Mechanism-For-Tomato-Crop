from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

import cv2
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from phase_2_disease_detection.classes import CLASS_TO_INDEX


TOMATO_CLASS_PREFIXES = (
    "tomato_bacterial_leaf_spot",
    "tomato_early_blight",
    "tomato_late_blight",
    "tomato_leaf_mold",
    "tomato_mosaic_virus",
    "tomato_septoria_leaf_spot",
    "tomato_yellow_leaf_curl_virus",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare PlantSeg tomato subset for phase 2 training.")
    parser.add_argument(
        "--zip-path",
        type=Path,
        default=Path(__file__).resolve().parent / "plantseg.zip",
        help="Path to PlantSeg zip archive.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(__file__).resolve().parent / "phase_2_dataset",
        help="Output folder for prepared tomato subset.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete existing prepared dataset before writing.",
    )
    return parser.parse_args()


def infer_class_from_name(stem: str) -> str | None:
    for prefix in TOMATO_CLASS_PREFIXES:
        if stem.startswith(prefix):
            return prefix
    return None


def write_mask(mask_bytes: bytes, class_name: str, output_path: Path) -> None:
    array = np.frombuffer(mask_bytes, dtype=np.uint8)
    mask = cv2.imdecode(array, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise RuntimeError(f"Failed to decode mask for {output_path.name}")

    class_index = CLASS_TO_INDEX[class_name]
    remapped = np.where(mask > 0, class_index, 0).astype(np.uint8)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), remapped)


def main() -> None:
    args = parse_args()
    if not args.zip_path.exists():
        raise FileNotFoundError(f"PlantSeg archive not found: {args.zip_path}")

    if args.output_root.exists() and args.overwrite:
        shutil.rmtree(args.output_root)

    image_counts = {"train": 0, "val": 0, "test": 0}
    mask_counts = {"train": 0, "val": 0, "test": 0}

    with zipfile.ZipFile(args.zip_path) as archive:
        image_names = [
            name
            for name in archive.namelist()
            if name.startswith("plantseg/images/") and name.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        for image_name in image_names:
            parts = image_name.split("/")
            split = parts[2]
            filename = parts[-1]
            stem = Path(filename).stem
            class_name = infer_class_from_name(stem)
            if class_name is None:
                continue

            mask_name = f"plantseg/annotations/{split}/{stem}.png"
            if mask_name not in archive.namelist():
                continue

            image_output = args.output_root / "images" / split / filename
            image_output.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(image_name) as source, image_output.open("wb") as target:
                shutil.copyfileobj(source, target)
            image_counts[split] += 1

            mask_output = args.output_root / "masks" / split / f"{stem}.png"
            write_mask(archive.read(mask_name), class_name, mask_output)
            mask_counts[split] += 1

    summary = {
        split: {"images": image_counts[split], "masks": mask_counts[split]}
        for split in ("train", "val", "test")
    }
    print("Prepared PlantSeg tomato subset")
    for split, counts in summary.items():
        print(f"{split}: {counts['images']} images, {counts['masks']} masks")


if __name__ == "__main__":
    main()
