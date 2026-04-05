from __future__ import annotations

import shutil
import time
from pathlib import Path

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

try:
    from picamera2 import Picamera2
except ImportError:  # pragma: no cover
    Picamera2 = None

try:
    from gpiozero import OutputDevice, PWMOutputDevice
except ImportError:  # pragma: no cover
    OutputDevice = None
    PWMOutputDevice = None

try:
    from ultralytics import YOLO
except ImportError:  # pragma: no cover
    YOLO = None


def _pulse(device: OutputDevice | None, duration: float, label: str, dry_run: bool) -> None:
    if dry_run or device is None:
        print(f"[Phase 1] simulated {label} for {duration:.2f}s")
        time.sleep(duration)
        return
    device.on()
    time.sleep(duration)
    device.off()


def _run_belt_forward(
    belt_in1: OutputDevice | None,
    belt_in2: OutputDevice | None,
    belt_ena: OutputDevice | PWMOutputDevice | None,
    duration: float,
    speed: float,
    dry_run: bool,
) -> None:
    if dry_run or belt_in1 is None or belt_in2 is None:
        print(f"[Phase 1] simulated belt forward for {duration:.2f}s at speed {speed:.2f}")
        time.sleep(duration)
        return

    belt_in1.on()
    belt_in2.off()

    if belt_ena is not None:
        if hasattr(belt_ena, "value"):
            belt_ena.value = max(0.0, min(1.0, speed))
        else:
            belt_ena.on()

    time.sleep(duration)

    belt_in1.off()
    belt_in2.off()
    if belt_ena is not None and hasattr(belt_ena, "off"):
        belt_ena.off()


def _plant_position_duration(context: dict) -> tuple[float, str]:
    plant_index = int(context.get("plant_index", 1))
    timings = {
        1: float(context.get("start_to_plant1_time", 0.8)),
        2: float(context.get("start_to_plant2_time", 1.8)),
        3: float(context.get("start_to_plant3_time", 2.8)),
    }
    labels = {
        1: "start to plant 1",
        2: "start to plant 2",
        3: "start to plant 3",
    }
    duration = timings.get(plant_index, float(context.get("belt_move_time", 0.8)))
    label = labels.get(plant_index, f"start to plant {plant_index}")
    return duration, label


def _focus_score(image_path: Path) -> float:
    if cv2 is None:
        return 0.0
    image = cv2.imread(str(image_path))
    if image is None:
        return 0.0
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def _capture_images(context: dict) -> list[Path]:
    captures_dir = Path(context["captures_dir"])
    captures_dir.mkdir(parents=True, exist_ok=True)
    image_count = int(context.get("image_count", 8))
    input_dir = context.get("input_image_dir")

    if input_dir:
        input_dir = Path(input_dir)
        images = sorted(
            [path for path in input_dir.iterdir() if path.suffix.lower() in {".jpg", ".jpeg", ".png"}]
        )[:image_count]
        print(f"[Phase 1] loaded {len(images)} images from {input_dir}")
        return images

    if Picamera2 is None:
        raise RuntimeError("[Phase 1] Picamera2 not available. Use --input-image-dir for testing.")

    camera = Picamera2()
    config = camera.create_still_configuration(main={"size": (1280, 960)})
    camera.configure(config)
    camera.start()
    time.sleep(float(context.get("capture_delay", 1.5)))

    captured = []
    for index in range(image_count):
        output_path = captures_dir / f"{context['plant_id']}_raw_{index + 1}.jpg"
        camera.capture_file(str(output_path))
        captured.append(output_path)

    camera.stop()
    camera.close()
    print(f"[Phase 1] captured {len(captured)} raw images")
    return captured


def _detect_leaf_boxes(image_path: Path, yolo_weights: Path | None) -> list[tuple[int, int, int, int]]:
    if YOLO is None or yolo_weights is None or not yolo_weights.exists():
        return []

    model = YOLO(str(yolo_weights))
    results = model.predict(source=str(image_path), verbose=False)
    boxes: list[tuple[int, int, int, int]] = []
    for result in results:
        for box in result.boxes.xyxy.tolist():
            x1, y1, x2, y2 = [int(value) for value in box]
            boxes.append((x1, y1, x2, y2))
    return boxes


def _select_best_images(raw_images: list[Path], context: dict) -> list[dict]:
    selected_dir = Path(context["selected_dir"])
    selected_dir.mkdir(parents=True, exist_ok=True)
    yolo_weights = context.get("yolo_weights")
    selected_count = int(context.get("selected_leaves", 6))

    scored = []
    for image_path in raw_images:
        boxes = _detect_leaf_boxes(image_path, Path(yolo_weights)) if yolo_weights else []
        score = _focus_score(image_path)
        scored.append(
            {
                "image_path": str(image_path.resolve()),
                "focus_score": round(score, 2),
                "leaf_boxes_found": len(boxes),
                "selection_score": round(score + (len(boxes) * 100.0), 2),
            }
        )

    scored.sort(key=lambda item: item["selection_score"], reverse=True)
    selected = scored[:selected_count]

    for index, item in enumerate(selected, start=1):
        source = Path(item["image_path"])
        target = selected_dir / f"{context['plant_id']}_leaf_{index}{source.suffix.lower()}"
        shutil.copy2(source, target)
        item["selected_path"] = str(target.resolve())

    return selected


def run_phase(context: dict) -> dict:
    dry_run = bool(context.get("dry_run", False)) or OutputDevice is None
    belt_in1 = None
    belt_in2 = None
    belt_ena = None
    if not dry_run:
        belt_in1 = OutputDevice(context["belt_in1_pin"]) if context.get("belt_in1_pin") is not None else None
        belt_in2 = OutputDevice(context["belt_in2_pin"]) if context.get("belt_in2_pin") is not None else None
        if context.get("belt_ena_pin") is not None and PWMOutputDevice is not None:
            belt_ena = PWMOutputDevice(context["belt_ena_pin"])
        elif context.get("belt_ena_pin") is not None:
            belt_ena = OutputDevice(context["belt_ena_pin"])

    belt_speed = float(context.get("belt_speed", 0.10))
    move_duration, move_label = _plant_position_duration(context)

    print(f"[Phase 1] moving belt: {move_label}")
    _run_belt_forward(
        belt_in1=belt_in1,
        belt_in2=belt_in2,
        belt_ena=belt_ena,
        duration=move_duration,
        speed=belt_speed,
        dry_run=dry_run,
    )

    raw_images = _capture_images(context)
    selected = _select_best_images(raw_images, context)

    context["phase_1_output"] = {
        "plant_id": context["plant_id"],
        "plant_index": int(context.get("plant_index", 1)),
        "movement_to_plant_seconds": round(move_duration, 3),
        "raw_image_paths": [str(path.resolve()) for path in raw_images],
        "selected_leaf_images": selected,
        "selected_count": len(selected),
    }
    context["selected_leaf_image_paths"] = [item["selected_path"] for item in selected]

    print(f"[Phase 1] selected {len(selected)} best leaf images")
    return context


def explain_phase() -> dict:
    return {
        "phase": 1,
        "title": "Image Acquisition",
        "description": (
            "The belt moves above a tomato plant, multiple images are captured, and the best leaf images "
            "are selected using clarity scoring and optional YOLO leaf detections."
        ),
        "sample_input": {
            "plant_id": "plant_001",
            "plant_index": 1,
            "image_count": 8,
            "selected_leaves": 6,
            "belt_in1_pin": 17,
            "belt_in2_pin": 27,
            "belt_ena_pin": 22,
            "belt_speed": 0.10,
            "start_to_plant1_time": 0.8,
            "capture_delay": 1.5,
            "yolo_weights": "models/leaf_detector.pt",
        },
        "sample_output": {
            "movement_to_plant_seconds": 0.8,
            "raw_image_paths": ["captures/plant_001_raw_1.jpg", "captures/plant_001_raw_2.jpg"],
            "selected_leaf_images": [
                {
                    "image_path": "captures/plant_001_raw_2.jpg",
                    "focus_score": 412.8,
                    "leaf_boxes_found": 3,
                    "selection_score": 712.8,
                    "selected_path": "selected_leaves/plant_001_leaf_1.jpg",
                }
            ],
            "selected_count": 6,
        },
    }
