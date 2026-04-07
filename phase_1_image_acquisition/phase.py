from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

Picamera2 = None

try:
    from gpiozero import OutputDevice, PWMOutputDevice
except ImportError:  # pragma: no cover
    OutputDevice = None
    PWMOutputDevice = None

try:
    from gpiozero.exc import PinPWMUnsupported
except ImportError:  # pragma: no cover
    PinPWMUnsupported = Exception


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
        1: float(context.get("start_to_plant1_time", 5.0)),
        2: float(context.get("start_to_plant2_time", 5.0)),
        3: float(context.get("start_to_plant3_time", 5.0)),
    }
    labels = {
        1: "start to plant 1",
        2: "start to plant 2",
        3: "start to plant 3",
    }
    duration = timings.get(plant_index, float(context.get("belt_move_time", 5.0)))
    label = labels.get(plant_index, f"start to plant {plant_index}")
    return duration, label


def _create_enable_device(pin: int | None) -> OutputDevice | PWMOutputDevice | None:
    if pin is None or OutputDevice is None:
        return None
    if PWMOutputDevice is not None:
        try:
            return PWMOutputDevice(pin)
        except PinPWMUnsupported:
            print(f"[Phase 1] PWM unsupported on GPIO{pin}, using simple enable output instead")
    return OutputDevice(pin)


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
        all_images = sorted(
            [path for path in input_dir.iterdir() if path.suffix.lower() in {".jpg", ".jpeg", ".png"}]
        )
        plant_id = str(context.get("plant_id", "")).lower()
        plant_index = int(context.get("plant_index", 1))
        matched_images = [path for path in all_images if path.name.lower().startswith(f"{plant_id}_")]
        if not matched_images:
            matched_images = [path for path in all_images if path.name.lower().startswith(f"plant_{plant_index:03d}_")]
        images = (matched_images or all_images)[:image_count]
        print(f"[Phase 1] loaded {len(images)} images from {input_dir}")
        return images

    camera_class = Picamera2
    if camera_class is None:
        try:
            from picamera2 import Picamera2 as _Picamera2
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "[Phase 1] Picamera2 not available. Use --input-image-dir for testing."
            ) from exc
        camera_class = _Picamera2

    camera = camera_class()
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


def _load_leaf_box_manifest(input_dir: Path | None) -> dict:
    if input_dir is None:
        return {}
    manifest_path = Path(input_dir) / "leaf_boxes_manifest.json"
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _crop_with_box(image, box: list[int] | tuple[int, int, int, int]):
    x1, y1, x2, y2 = [int(value) for value in box]
    return image[y1:y2, x1:x2], (x1, y1, x2, y2)


def _select_manual_leaf_crops(raw_images: list[Path], context: dict, manifest: dict) -> list[dict]:
    if cv2 is None or not manifest:
        return []

    selected_dir = Path(context["selected_dir"])
    selected_dir.mkdir(parents=True, exist_ok=True)
    selected_count = int(context.get("selected_leaves", 6))
    selected: list[dict] = []
    overlay_paths: list[str] = []

    for raw_image in raw_images:
        boxes = manifest.get(raw_image.name)
        if not boxes:
            continue

        image = cv2.imread(str(raw_image))
        if image is None:
            continue

        overlay = image.copy()
        for local_index, item in enumerate(boxes[:selected_count], start=1):
            crop, (x1, y1, x2, y2) = _crop_with_box(image, item["box"])
            if crop.size == 0:
                continue
            target = selected_dir / f"{context['plant_id']}_leaf_{local_index}.jpg"
            cv2.imwrite(str(target), crop)
            label = str(item.get("leaf_id", local_index))
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(
                overlay,
                label,
                (x1 + 6, max(28, y1 + 28)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )
            selected.append(
                {
                    "image_path": str(raw_image.resolve()),
                    "source_image_path": str(raw_image.resolve()),
                    "source_image_name": raw_image.name,
                    "leaf_id": label,
                    "crop_box": [x1, y1, x2, y2],
                    "focus_score": round(_focus_score(target), 2),
                    "leaf_boxes_found": len(boxes),
                    "selection_score": round(_focus_score(target), 2),
                    "selected_path": str(target.resolve()),
                }
            )

        overlay_path = selected_dir / f"{context['plant_id']}_selected_leaf_boxes.jpg"
        cv2.imwrite(str(overlay_path), overlay)
        overlay_paths.append(str(overlay_path.resolve()))

    if selected:
        context["selected_leaf_box_images"] = overlay_paths
    return selected


def _select_best_images(raw_images: list[Path], context: dict) -> list[dict]:
    selected_dir = Path(context["selected_dir"])
    selected_dir.mkdir(parents=True, exist_ok=True)
    selected_count = int(context.get("selected_leaves", 6))
    input_dir = Path(context["input_image_dir"]) if context.get("input_image_dir") else None

    manual_selected = _select_manual_leaf_crops(raw_images, context, _load_leaf_box_manifest(input_dir))
    if manual_selected:
        return manual_selected

    scored = []
    for image_path in raw_images:
        score = _focus_score(image_path)
        scored.append(
            {
                "image_path": str(image_path.resolve()),
                "source_image_path": str(image_path.resolve()),
                "source_image_name": image_path.name,
                "focus_score": round(score, 2),
                "leaf_boxes_found": 0,
                "selection_score": round(score, 2),
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
        belt_ena = _create_enable_device(context.get("belt_ena_pin"))

    belt_speed = float(context.get("belt_speed", 0.10))
    move_duration, move_label = _plant_position_duration(context)

    if bool(context.get("skip_phase1_move", False)):
        print(f"[Phase 1] skipping belt move for {move_label}")
        move_duration = 0.0
    else:
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
        "selected_leaf_box_images": context.get("selected_leaf_box_images", []),
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
            "are selected using clarity scoring or fixed manual leaf boxes for the no-camera 3-plant test set."
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
