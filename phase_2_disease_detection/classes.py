from __future__ import annotations

TOMATO_DISEASE_CLASSES = (
    "background",
    "tomato_bacterial_leaf_spot",
    "tomato_early_blight",
    "tomato_late_blight",
    "tomato_leaf_mold",
    "tomato_mosaic_virus",
    "tomato_septoria_leaf_spot",
    "tomato_yellow_leaf_curl_virus",
)

CLASS_TO_INDEX = {name: index for index, name in enumerate(TOMATO_DISEASE_CLASSES)}
INDEX_TO_CLASS = {index: name for name, index in CLASS_TO_INDEX.items()}

# Healthy is derived from visible leaf area not assigned to any disease class.
PLANT_OUTPUT_CLASSES = TOMATO_DISEASE_CLASSES[1:] + ("healthy",)
