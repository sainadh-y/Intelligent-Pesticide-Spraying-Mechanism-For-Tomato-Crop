from __future__ import annotations


DEFAULT_DISEASE_WEIGHTS = {
    "tomato_late_blight": 8 / 36,
    "tomato_early_blight": 7 / 36,
    "tomato_septoria_leaf_spot": 6 / 36,
    "tomato_bacterial_leaf_spot": 5 / 36,
    "tomato_leaf_mold": 4 / 36,
    "tomato_yellow_leaf_curl_virus": 3 / 36,
    "tomato_mosaic_virus": 2 / 36,
}

DEFAULT_DAMAGE_WEIGHT = 1 / 36


def run_phase(context: dict) -> dict:
    disease_output = context.get("phase_2_output", {})
    damage_output = context.get("phase_3_output", {})
    disease_percentages = disease_output.get("disease_percentages") or {}
    damage_value = damage_output.get("average_leaf_damage_percentage")
    damage_value = float(damage_value) if damage_value is not None else 0.0

    disease_weights = context.get("disease_weights") or DEFAULT_DISEASE_WEIGHTS
    damage_weight = float(context.get("damage_weight", DEFAULT_DAMAGE_WEIGHT))

    weighted_sum = 0.0
    for disease_name, weight in disease_weights.items():
        weighted_sum += float(disease_percentages.get(disease_name, 0.0)) * float(weight)

    infection_average = round(weighted_sum + (damage_value * damage_weight), 4)

    context["phase_4_output"] = {
        "disease_weights": disease_weights,
        "damage_weight": damage_weight,
        "infection_average": infection_average,
    }
    context["infection_average"] = infection_average

    print(f"[Phase 4] infection average: {infection_average}")
    return context


def explain_phase() -> dict:
    return {
        "phase": 4,
        "title": "Aggregation",
        "description": (
            "Disease percentages and damage percentage are combined using ranking-based normalized weights "
            "to produce a single infection average for the plant."
        ),
        "sample_input": {
            "disease_percentages": {
                "tomato_late_blight": 0.16,
                "tomato_early_blight": 0.24,
                "tomato_septoria_leaf_spot": 0.07,
                "tomato_bacterial_leaf_spot": 0.02,
                "tomato_leaf_mold": 0.03,
                "tomato_yellow_leaf_curl_virus": 0.01,
                "tomato_mosaic_virus": 0.0,
            },
            "average_leaf_damage_percentage": 0.18,
            "disease_weights": {
                "tomato_late_blight": 0.2222,
                "tomato_early_blight": 0.1944,
                "tomato_septoria_leaf_spot": 0.1667,
                "tomato_bacterial_leaf_spot": 0.1389,
                "tomato_leaf_mold": 0.1111,
                "tomato_yellow_leaf_curl_virus": 0.0833,
                "tomato_mosaic_virus": 0.0556,
            },
            "damage_weight": 0.0278,
        },
        "sample_output": {
            "infection_average": 0.1119,
        },
    }
