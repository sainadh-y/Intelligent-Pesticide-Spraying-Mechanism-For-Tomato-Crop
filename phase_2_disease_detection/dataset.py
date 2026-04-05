from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset


class PlantSegTomatoDataset(Dataset):
    def __init__(
        self,
        dataset_root: Path,
        split: str,
        image_size: tuple[int, int],
    ) -> None:
        self.dataset_root = Path(dataset_root)
        self.split = split
        self.image_size = image_size

        self.images_dir = self.dataset_root / "images" / split
        self.masks_dir = self.dataset_root / "masks" / split
        if not self.images_dir.exists():
            raise FileNotFoundError(f"Phase 2 dataset images directory not found: {self.images_dir}")
        if not self.masks_dir.exists():
            raise FileNotFoundError(f"Phase 2 dataset masks directory not found: {self.masks_dir}")

        self.image_paths = sorted(
            [path for path in self.images_dir.iterdir() if path.suffix.lower() in {".jpg", ".jpeg", ".png"}]
        )
        if not self.image_paths:
            raise RuntimeError(f"No image files found in {self.images_dir}")

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        image_path = self.image_paths[index]
        mask_path = self.masks_dir / f"{image_path.stem}.png"
        if not mask_path.exists():
            raise FileNotFoundError(f"Expected mask file missing for {image_path.name}: {mask_path}")

        image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        if image is None or mask is None:
            raise RuntimeError(f"Failed to load image/mask pair: {image_path}, {mask_path}")

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, self.image_size, interpolation=cv2.INTER_AREA)
        mask = cv2.resize(mask, self.image_size, interpolation=cv2.INTER_NEAREST)

        image_tensor = torch.from_numpy(image.astype(np.float32) / 255.0).permute(2, 0, 1)
        mask_tensor = torch.from_numpy(mask.astype(np.int64))
        return image_tensor, mask_tensor
