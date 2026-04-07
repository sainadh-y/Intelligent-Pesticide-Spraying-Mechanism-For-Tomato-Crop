from __future__ import annotations

import time

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
        print(f"[Phase 7] simulated {label} for {duration:.2f}s")
        time.sleep(duration)
        return
    device.on()
    time.sleep(duration)
    device.off()


def run_phase(context: dict) -> dict:
    dry_run = bool(context.get("dry_run", False)) or OutputDevice is None

    spray_device = None
    belt_in1 = None
    belt_in2 = None
    belt_ena = None
    relay_active_high = bool(context.get("relay_active_high", True))
    if not dry_run:
        spray_device = (
            OutputDevice(context["spray_pin"], active_high=relay_active_high)
            if context.get("spray_pin") is not None
            else None
        )
        belt_in1 = OutputDevice(context["belt_in1_pin"]) if context.get("belt_in1_pin") is not None else None
        belt_in2 = OutputDevice(context["belt_in2_pin"]) if context.get("belt_in2_pin") is not None else None
        belt_ena = _create_enable_device(context.get("belt_ena_pin"))
        if spray_device is not None:
            spray_device.off()

    spray_pulse = float(context.get("spray_pulse", 0.6))
    base_spray_ml = float(context.get("base_spray_ml", 5.0))
    pump_settle_delay = float(context.get("pump_settle_delay", 0.5))
    spray_action = context.get("spray_action", "spray_pesticide")
    applied_output = float(context.get("applied_output", context.get("spray_ml_per_plant", 0.0)))
    belt_speed = float(context.get("belt_speed", 0.10))
    plant_index = int(context.get("plant_index", 1))
    total_plants = int(context.get("total_plants", 3))
    move_next_time = _next_move_duration(context, plant_index)
    spray_flow_rate_ml_per_sec = (
        base_spray_ml / spray_pulse if spray_pulse > 0 and base_spray_ml > 0 else 0.0
    )
    spray_duration_seconds = (
        applied_output / spray_flow_rate_ml_per_sec if spray_flow_rate_ml_per_sec > 0 else 0.0
    )

    print(f"[Phase 7] plant {context.get('plant_id')} action: {spray_action}")
    print(f"[Phase 7] applied output: {applied_output} ml")
    if spray_action == "spray_pesticide":
        print(f"[Phase 7] spray duration: {spray_duration_seconds:.3f} s")
        _pulse(spray_device, spray_duration_seconds, spray_action, dry_run)
        execution_note = "pump relay triggered for pesticide spray"
    else:
        print("[Phase 7] color-marking case recorded in output only, no pump action executed")
        execution_note = "color-marking noted in output only; no physical spray executed"

    if spray_device is not None and not dry_run:
        spray_device.off()
        if pump_settle_delay > 0:
            print(f"[Phase 7] waiting {pump_settle_delay:.2f}s for pump/relay to settle before movement")
            time.sleep(pump_settle_delay)

    if plant_index < total_plants:
        print(f"[Phase 7] moving from plant {plant_index} to plant {plant_index + 1}")
        _run_belt_forward(
            belt_in1=belt_in1,
            belt_in2=belt_in2,
            belt_ena=belt_ena,
            duration=move_next_time,
            speed=belt_speed,
            dry_run=dry_run,
        )
        next_step = f"move_to_plant_{plant_index + 1}"
    else:
        print("[Phase 7] plant 3 reached, stopping at end position")
        next_step = "stop_after_plant_3"

    context["phase_7_output"] = {
        "plant_index": plant_index,
        "spray_mode": context.get("spray_mode"),
        "spray_ml_per_plant": context.get("spray_ml_per_plant"),
        "applied_output": applied_output,
        "applied_output_unit": "ml",
        "spray_duration_seconds": round(spray_duration_seconds, 3) if spray_action == "spray_pesticide" else 0.0,
        "spray_flow_rate_ml_per_sec": round(spray_flow_rate_ml_per_sec, 3) if spray_action == "spray_pesticide" else 0.0,
        "pump_settle_delay": round(pump_settle_delay, 3) if spray_action == "spray_pesticide" else 0.0,
        "action": spray_action,
        "execution_note": execution_note,
        "next_step": next_step,
        "move_next_seconds": round(move_next_time, 3) if plant_index < total_plants else 0.0,
        "execution_status": "completed",
    }

    return context


def _create_enable_device(pin: int | None) -> OutputDevice | PWMOutputDevice | None:
    if pin is None or OutputDevice is None:
        return None
    if PWMOutputDevice is not None:
        try:
            return PWMOutputDevice(pin)
        except PinPWMUnsupported:
            print(f"[Phase 7] PWM unsupported on GPIO{pin}, using simple enable output instead")
    return OutputDevice(pin)


def _next_move_duration(context: dict, plant_index: int) -> float:
    next_map = {
        1: float(context.get("plant1_to_plant2_time", 5.0)),
        2: float(context.get("plant2_to_plant3_time", 5.0)),
        3: float(context.get("plant3_to_end_time", 5.0)),
    }
    return next_map.get(plant_index, float(context.get("move_next_time", 5.0)))


def _run_belt_forward(
    belt_in1: OutputDevice | None,
    belt_in2: OutputDevice | None,
    belt_ena: OutputDevice | PWMOutputDevice | None,
    duration: float,
    speed: float,
    dry_run: bool,
) -> None:
    if dry_run or belt_in1 is None or belt_in2 is None:
        print(f"[Phase 7] simulated belt forward for {duration:.2f}s at speed {speed:.2f}")
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

    if belt_ena is not None:
        if hasattr(belt_ena, "off"):
            belt_ena.off()


def explain_phase() -> dict:
    return {
        "phase": 7,
        "title": "Execute Spray And Move",
        "description": (
            "The selected spray mode is executed for the current plant, and then the belt moves the system "
            "to the next plant position."
        ),
        "sample_input": {
            "plant_id": "plant_001",
            "plant_index": 1,
            "total_plants": 3,
            "spray_mode": "scaled_spray",
            "spray_ml_per_plant": 18.5,
            "applied_output": 18.5,
            "action": "spray_pesticide",
            "base_spray_ml": 5.0,
            "spray_pulse": 0.6,
            "belt_in1_pin": 17,
            "belt_in2_pin": 27,
            "belt_ena_pin": 22,
            "spray_pin": 23,
            "relay_active_high": True,
            "plant1_to_plant2_time": 1.0,
            "belt_speed": 0.10,
        },
        "sample_output": {
            "next_step": "move_to_plant_2",
            "execution_note": "pump relay triggered for pesticide spray",
            "applied_output": 18.5,
            "applied_output_unit": "ml",
            "spray_duration_seconds": 2.22,
            "execution_status": "completed",
        },
    }
