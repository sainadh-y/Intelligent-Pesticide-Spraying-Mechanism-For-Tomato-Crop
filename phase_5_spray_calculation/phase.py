from __future__ import annotations


def run_phase(context: dict) -> dict:
    infection_average = float(context.get("infection_average", 0.0))
    p_ref = float(context.get("p_ref", 10.0))
    i_ref = float(context.get("i_ref", 0.10))
    d_current = float(context.get("d_current", 1.0))
    d_ref = float(context.get("d_ref", 1.0))

    if i_ref == 0 or d_ref == 0:
        raise ValueError("i_ref and d_ref must be non-zero for spray calculation")

    spray_ml = round(p_ref * (infection_average / i_ref) * (d_current / d_ref), 3)

    context["phase_5_output"] = {
        "p_ref": p_ref,
        "i_ref": i_ref,
        "d_current": d_current,
        "d_ref": d_ref,
        "spray_ml_per_plant": spray_ml,
    }
    context["spray_ml_per_plant"] = spray_ml

    print(f"[Phase 5] spray amount per plant: {spray_ml} ml")
    return context


def explain_phase() -> dict:
    return {
        "phase": 5,
        "title": "Spray Calculation",
        "description": (
            "The infection average is converted into spray quantity using your provided formula "
            "based on reference spray, reference infection, and current/reference density factors."
        ),
        "sample_input": {
            "infection_average": 0.185,
            "p_ref": 10.0,
            "i_ref": 0.10,
            "d_current": 1.0,
            "d_ref": 1.0,
        },
        "sample_output": {
            "spray_ml_per_plant": 18.5,
        },
    }
