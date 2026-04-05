from __future__ import annotations

from pathlib import Path

try:
    import torch
except ImportError:  # pragma: no cover
    torch = None

from phase_2_disease_detection.classes import PLANT_OUTPUT_CLASSES

DEFAULT_WEIGHTS_PATH = Path(__file__).resolve().parent / "models" / "phase_2_tomato_unet.pt"


def run_phase(context: dict) -> dict:
    selected_leaf_paths = [Path(path) for path in context.get("selected_leaf_image_paths", [])]
    image_size = tuple(context.get("phase_2_image_size", (256, 256)))
    weights_path = context.get("phase_2_weights") or DEFAULT_WEIGHTS_PATH

    if not selected_leaf_paths:
        context["phase_2_output"] = {
            "status": "no_input_images",
            "model_type": "u_net_segmentation",
            "message": "No selected leaf images were provided from phase 1.",
            "per_leaf_results": [],
            "disease_percentages": {},
            "plant_disease_average": None,
        }
        print("[Phase 2] no selected leaf images found")
        return context

    if torch is None:
        raise RuntimeError("[Phase 2] PyTorch is required for the completed phase 2 implementation.")

    if not weights_path:
        context["phase_2_output"] = {
            "status": "waiting_for_trained_weights",
            "model_type": "u_net_segmentation",
            "message": "Phase 2 code is complete, but no trained weights path was provided.",
            "per_leaf_results": [],
            "disease_percentages": {label: 0.0 for label in PLANT_OUTPUT_CLASSES},
            "plant_disease_average": None,
        }
        print("[Phase 2] trained weights not provided")
        return context

    weights = Path(weights_path)
    if not weights.exists():
        raise FileNotFoundError(f"[Phase 2] Weights file not found: {weights}")

    from phase_2_disease_detection.infer import aggregate_predictions, load_model, predict_leaf

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(weights, device)
    per_leaf_results = [predict_leaf(path, model, device, image_size) for path in selected_leaf_paths]
    disease_percentages, plant_disease_average = aggregate_predictions(per_leaf_results)

    context["phase_2_output"] = {
        "status": "completed",
        "model_type": "u_net_segmentation",
        "message": "PlantSeg tomato subset inference completed.",
        "per_leaf_results": per_leaf_results,
        "disease_percentages": disease_percentages,
        "plant_disease_average": plant_disease_average,
        "camera_condition_note": "Camera-condition mismatch intentionally neglected for now.",
    }
    print(f"[Phase 2] analyzed {len(per_leaf_results)} selected leaf images")
    return context


def explain_phase() -> dict:
    return {
        "phase": 2,
        "title": "Disease Detection",
        "description": (
            "A U-Net segmentation model trained on the PlantSeg tomato subset predicts per-pixel disease classes "
            "for each selected leaf image, converts them into per-leaf disease percentages, and averages them "
            "to produce the plant-level disease output."
        ),
        "sample_input": {
            "selected_leaf_image_paths": [
                "selected_leaves/plant_001_leaf_1.jpg",
                "selected_leaves/plant_001_leaf_2.jpg",
            ],
            "phase_2_image_size": [256, 256],
            "phase_2_weights": "models/phase_2_tomato_unet.pt",
        },
        "sample_output": {
            "status": "completed",
            "disease_percentages": {
                "tomato_bacterial_leaf_spot": 0.02,
                "tomato_early_blight": 0.24,
                "tomato_late_blight": 0.11,
                "tomato_leaf_mold": 0.03,
                "tomato_mosaic_virus": 0.0,
                "tomato_septoria_leaf_spot": 0.07,
                "tomato_yellow_leaf_curl_virus": 0.01,
                "healthy": 0.52,
            },
            "plant_disease_average": 0.48,
        },
    }
