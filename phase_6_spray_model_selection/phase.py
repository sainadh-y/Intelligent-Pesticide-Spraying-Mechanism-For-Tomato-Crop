from __future__ import annotations


def run_phase(context: dict) -> dict:
    spray_ml = float(context.get("spray_ml_per_plant", 0.0))

    if spray_ml <= 10:
        spray_mode = "standard_spray"
        applied_output = 10.0
        action = "spray_pesticide"
    elif spray_ml <= 75:
        spray_mode = "scaled_spray"
        applied_output = spray_ml
        action = "spray_pesticide"
    else:
        spray_mode = "spray_color_marking"
        applied_output = 5.0
        action = "mark_for_removal"

    context["phase_6_output"] = {
        "spray_ml_per_plant": spray_ml,
        "spray_mode": spray_mode,
        "applied_output": applied_output,
        "action": action,
    }
    context["spray_mode"] = spray_mode
    context["applied_output"] = applied_output
    context["spray_action"] = action

    print(f"[Phase 6] selected spray mode: {spray_mode}")
    return context


def explain_phase() -> dict:
    return {
        "phase": 6,
        "title": "Model Selection",
        "description": (
            "The calculated P_plant value is mapped to standard spray, scaled spray, or color marking for removal."
        ),
        "sample_input": {
            "spray_ml_per_plant": 18.5,
        },
        "sample_output": {
            "spray_mode": "scaled_spray",
            "applied_output": 18.5,
            "action": "spray_pesticide",
        },
    }
