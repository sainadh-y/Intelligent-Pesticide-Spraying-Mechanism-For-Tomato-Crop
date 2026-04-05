from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import torch

from phase_2_disease_detection.classes import INDEX_TO_CLASS, PLANT_OUTPUT_CLASSES, TOMATO_DISEASE_CLASSES
from phase_2_disease_detection.model import UNet


def load_model(weights_path: Path, device: torch.device) -> UNet:
    model = UNet(in_channels=3, out_channels=len(TOMATO_DISEASE_CLASSES))
    state = torch.load(weights_path, map_location=device)
    model.load_state_dict(state["model_state"] if "model_state" in state else state)
    model.to(device)
    model.eval()
    return model


def preprocess_image(image_path: Path, image_size: tuple[int, int]) -> tuple[np.ndarray, torch.Tensor]:
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"[Phase 2] Unable to read leaf image: {image_path}")

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(image_rgb, image_size, interpolation=cv2.INTER_AREA)
    tensor = torch.from_numpy(resized.astype(np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0)
    return resized, tensor


def derive_leaf_mask(image_rgb: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, np.array([20, 25, 20]), np.array([95, 255, 255]))
    kernel = np.ones((5, 5), dtype=np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


def predict_leaf(image_path: Path, model: UNet, device: torch.device, image_size: tuple[int, int]) -> dict:
    image_rgb, tensor = preprocess_image(image_path, image_size)
    leaf_mask = derive_leaf_mask(image_rgb)
    leaf_pixels = int(np.count_nonzero(leaf_mask))
    if leaf_pixels == 0:
        leaf_pixels = image_rgb.shape[0] * image_rgb.shape[1]

    with torch.no_grad():
        logits = model(tensor.to(device))
        prediction = torch.argmax(logits, dim=1).squeeze(0).cpu().numpy().astype(np.uint8)

    disease_percentages: dict[str, float] = {}
    diseased_total = 0.0
    for class_index in range(1, len(TOMATO_DISEASE_CLASSES)):
        class_name = INDEX_TO_CLASS[class_index]
        disease_pixels = int(np.count_nonzero(prediction == class_index))
        disease_percentage = round(disease_pixels / leaf_pixels, 4)
        disease_percentages[class_name] = disease_percentage
        diseased_total += disease_percentage

    disease_percentages["healthy"] = round(max(0.0, 1.0 - diseased_total), 4)
    return {
        "image_path": str(image_path),
        "leaf_pixels": leaf_pixels,
        "disease_percentages": disease_percentages,
    }


def aggregate_predictions(leaf_predictions: list[dict]) -> tuple[dict[str, float], float]:
    if not leaf_predictions:
        return {label: 0.0 for label in PLANT_OUTPUT_CLASSES}, 0.0

    aggregate = {label: 0.0 for label in PLANT_OUTPUT_CLASSES}
    for prediction in leaf_predictions:
        for label, value in prediction["disease_percentages"].items():
            aggregate[label] += float(value)

    count = float(len(leaf_predictions))
    for label in aggregate:
        aggregate[label] = round(aggregate[label] / count, 4)

    plant_disease_average = round(sum(aggregate[label] for label in aggregate if label != "healthy"), 4)
    return aggregate, plant_disease_average
