from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from torch import nn
from torch.optim import Adam
from torch.utils.data import DataLoader

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from phase_2_disease_detection.classes import TOMATO_DISEASE_CLASSES
from phase_2_disease_detection.dataset import PlantSegTomatoDataset
from phase_2_disease_detection.model import UNet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train phase 2 tomato disease segmentation model.")
    parser.add_argument("--dataset-root", type=Path, required=True, help="PlantSeg tomato subset root.")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--image-size", type=int, nargs=2, default=(256, 256))
    parser.add_argument("--output", type=Path, default=Path("phase_2_weights.pt"))
    return parser.parse_args()


def evaluate(model: UNet, loader: DataLoader, criterion: nn.Module, device: torch.device) -> float:
    model.eval()
    total_loss = 0.0
    batches = 0
    with torch.no_grad():
        for images, masks in loader:
            images = images.to(device)
            masks = masks.to(device)
            logits = model(images)
            loss = criterion(logits, masks)
            total_loss += float(loss.item())
            batches += 1
    return total_loss / max(1, batches)


def main() -> None:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_dataset = PlantSegTomatoDataset(args.dataset_root, "train", tuple(args.image_size))
    val_dataset = PlantSegTomatoDataset(args.dataset_root, "val", tuple(args.image_size))

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)

    model = UNet(in_channels=3, out_channels=len(TOMATO_DISEASE_CLASSES)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=args.learning_rate)

    history = []
    best_val = float("inf")

    for epoch in range(1, args.epochs + 1):
        model.train()
        running_loss = 0.0
        batches = 0

        for images, masks in train_loader:
            images = images.to(device)
            masks = masks.to(device)

            optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = criterion(logits, masks)
            loss.backward()
            optimizer.step()

            running_loss += float(loss.item())
            batches += 1

        train_loss = running_loss / max(1, batches)
        val_loss = evaluate(model, val_loader, criterion, device)
        history.append({"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss})
        print(f"Epoch {epoch}/{args.epochs} - train_loss={train_loss:.4f} val_loss={val_loss:.4f}")

        if val_loss < best_val:
            best_val = val_loss
            args.output.parent.mkdir(parents=True, exist_ok=True)
            torch.save(
                {
                    "model_state": model.state_dict(),
                    "class_names": TOMATO_DISEASE_CLASSES,
                    "image_size": list(args.image_size),
                    "history": history,
                },
                args.output,
            )

    history_path = args.output.with_suffix(".history.json")
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    print(f"Saved best weights to {args.output}")
    print(f"Saved training history to {history_path}")


if __name__ == "__main__":
    main()
