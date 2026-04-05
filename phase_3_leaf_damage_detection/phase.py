from __future__ import annotations

from pathlib import Path

try:
    import cv2
    import numpy as np
except ImportError:  # pragma: no cover
    cv2 = None
    np = None


def _require_cv() -> None:
    if cv2 is None or np is None:
        raise RuntimeError("[Phase 3] OpenCV and NumPy are required for leaf damage detection.")


def _preprocess_image(image_path: Path, image_size: tuple[int, int]) -> np.ndarray:
    _require_cv()
    image = cv2.imread(str(image_path))
    if image is None:
        raise RuntimeError(f"[Phase 3] Unable to read leaf image: {image_path}")

    resized = cv2.resize(image, image_size, interpolation=cv2.INTER_AREA)
    blurred = cv2.GaussianBlur(resized, (5, 5), 0)
    return blurred


def _segment_leaf(image: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, np.array([20, 25, 20]), np.array([95, 255, 255]))

    kernel = np.ones((5, 5), dtype=np.uint8)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return green_mask

    largest = max(contours, key=cv2.contourArea)
    mask = np.zeros_like(green_mask)
    cv2.drawContours(mask, [largest], -1, 255, thickness=cv2.FILLED)
    return mask


def _detect_damage_regions(image: np.ndarray, leaf_mask: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    brown_mask = cv2.inRange(hsv, np.array([5, 35, 20]), np.array([25, 255, 220]))
    yellow_mask = cv2.inRange(hsv, np.array([15, 25, 70]), np.array([40, 255, 255]))

    l_channel, a_channel, b_channel = cv2.split(lab)
    low_green_or_pale = cv2.inRange(a_channel, 120, 170)
    bright_holes = cv2.inRange(l_channel, 170, 255)

    candidate = cv2.bitwise_or(brown_mask, yellow_mask)
    candidate = cv2.bitwise_or(candidate, low_green_or_pale)
    candidate = cv2.bitwise_and(candidate, leaf_mask)

    # Bright gaps fully inside leaf area can indicate eaten holes on visible surface.
    inner_hole_candidates = cv2.bitwise_and(bright_holes, leaf_mask)
    candidate = cv2.bitwise_or(candidate, inner_hole_candidates)

    kernel = np.ones((3, 3), dtype=np.uint8)
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_OPEN, kernel)
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_CLOSE, kernel)
    return candidate


def _estimate_leaf_damage(image_path: Path, image_size: tuple[int, int]) -> dict:
    image = _preprocess_image(image_path, image_size)
    leaf_mask = _segment_leaf(image)
    damage_mask = _detect_damage_regions(image, leaf_mask)

    leaf_pixels = int(np.count_nonzero(leaf_mask))
    damage_pixels = int(np.count_nonzero(damage_mask))
    damage_percentage = round((damage_pixels / leaf_pixels), 4) if leaf_pixels else 0.0

    return {
        "image_path": str(image_path),
        "leaf_pixels": leaf_pixels,
        "damage_pixels": damage_pixels,
        "damage_percentage": damage_percentage,
    }


def _aggregate_damage_results(results: list[dict]) -> float | None:
    if not results:
        return None
    return round(sum(float(item["damage_percentage"]) for item in results) / len(results), 4)


def run_phase(context: dict) -> dict:
    selected_leaf_paths = [Path(path) for path in context.get("selected_leaf_image_paths", [])]
    image_size = tuple(context.get("phase_3_image_size", (256, 256)))

    if not selected_leaf_paths:
        context["phase_3_output"] = {
            "status": "no_input_images",
            "message": "No selected leaf images were provided from phase 1.",
            "per_leaf_damage": [],
            "average_leaf_damage_percentage": None,
        }
        print("[Phase 3] no selected leaf images found")
        return context

    per_leaf_damage = [_estimate_leaf_damage(path, image_size) for path in selected_leaf_paths]
    average_damage = _aggregate_damage_results(per_leaf_damage)

    context["phase_3_output"] = {
        "status": "algorithm_ready_dataset_upgrade_later",
        "message": (
            "Visible leaf damage percentage is estimated from the selected leaf images. "
            "This can later be upgraded with a trained model when the dataset is available."
        ),
        "per_leaf_damage": per_leaf_damage,
        "average_leaf_damage_percentage": average_damage,
    }
    print(f"[Phase 3] analyzed {len(per_leaf_damage)} selected leaf images")
    return context


def explain_phase() -> dict:
    return {
        "phase": 3,
        "title": "Leaf Damage Detection",
        "description": (
            "The selected leaf images are processed one by one to estimate visible leaf damage percentage, "
            "and those percentages are averaged for the plant."
        ),
        "sample_input": {
            "selected_leaf_image_paths": [
                "selected_leaves/plant_001_leaf_1.jpg",
                "selected_leaves/plant_001_leaf_2.jpg",
            ],
            "phase_3_image_size": [256, 256],
        },
        "sample_output": {
            "status": "algorithm_ready_dataset_upgrade_later",
            "per_leaf_damage": [
                {
                    "image_path": "selected_leaves/plant_001_leaf_1.jpg",
                    "leaf_pixels": 28450,
                    "damage_pixels": 3510,
                    "damage_percentage": 0.1234,
                },
                {
                    "image_path": "selected_leaves/plant_001_leaf_2.jpg",
                    "leaf_pixels": 29100,
                    "damage_pixels": 5529,
                    "damage_percentage": 0.19,
                }
            ],
            "average_leaf_damage_percentage": 0.18,
        },
    }
