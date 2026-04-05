# Phase 2: Disease Detection

## Goal

Run a tomato-only disease segmentation model on the selected leaf images and return plant-level disease percentages.

## Completion status

Completed.

## Dataset used

This phase uses the `PlantSeg` dataset, filtered to the tomato subset only.

Reference sources:

- [PlantSeg Scientific Data article](https://www.nature.com/articles/s41597-025-06513-4)
- [PlantSeg Zenodo DOI](https://doi.org/10.5281/zenodo.17719108)

## Tomato-only classes used

- `tomato_bacterial_leaf_spot`
- `tomato_early_blight`
- `tomato_late_blight`
- `tomato_leaf_mold`
- `tomato_mosaic_virus`
- `tomato_septoria_leaf_spot`
- `tomato_yellow_leaf_curl_virus`

The `healthy` percentage is derived during inference from the visible leaf area that is not assigned to any disease class.

## What was done

- added the PlantSeg archive locally as [plantseg.zip](C:\Users\sai-y\Downloads\plant\phase_2_disease_detection\plantseg.zip)
- inspected the real archive layout
- confirmed tomato images and matching annotation masks exist in the dataset
- created a tomato-only dataset preparation script in [prepare_dataset.py](C:\Users\sai-y\Downloads\plant\phase_2_disease_detection\prepare_dataset.py)
- extracted and filtered the archive into a local prepared dataset
- converted binary lesion masks into class-index masks based on the tomato disease class inferred from each filename
- created a dataset loader for training and validation
- implemented a U-Net segmentation model
- implemented training code
- trained an initial model locally
- saved model weights and training history
- integrated phase 2 inference into the main pipeline

## Folder structure used in phase 2

```text
phase_2_disease_detection/
  plantseg.zip
  classes.py
  dataset.py
  infer.py
  model.py
  phase.py
  prepare_dataset.py
  train.py
  models/
    phase_2_tomato_unet.pt
    phase_2_tomato_unet.history.json
  phase_2_dataset/
    images/
      train/
      val/
      test/
    masks/
      train/
      val/
      test/
```

## Local prepared dataset

Prepared dataset folder:

- [phase_2_dataset](C:\Users\sai-y\Downloads\plant\phase_2_disease_detection\phase_2_dataset)

Prepared split counts:

- train: 460 images
- val: 74 images
- test: 133 images

Prepared dataset structure:

```text
phase_2_dataset/
  images/
    train/
      tomato_*.jpg
    val/
      tomato_*.jpg
    test/
      tomato_*.jpg
  masks/
    train/
      tomato_*.png
    val/
      tomato_*.png
    test/
      tomato_*.png
```

## Local trained weights

Weights file:

- [phase_2_tomato_unet.pt](C:\Users\sai-y\Downloads\plant\phase_2_disease_detection\models\phase_2_tomato_unet.pt)

Training history:

- [phase_2_tomato_unet.history.json](C:\Users\sai-y\Downloads\plant\phase_2_disease_detection\models\phase_2_tomato_unet.history.json)

## Implemented algorithm

The implemented phase-2 algorithm is:

1. take the `5-10` selected clear leaf images from phase 1
2. preprocess each leaf image to the target training size
3. run a tomato-only U-Net segmentation model
4. predict a per-pixel disease map for that leaf
5. derive a visible leaf mask from the image
6. calculate disease percentage for each tomato class using:

```text
disease_percentage = disease_pixels / visible_leaf_pixels
```

7. derive the healthy percentage from the remaining visible leaf area
8. repeat this for every selected leaf image
9. average the per-leaf disease percentages across the selected leaves
10. use that average as the disease output for the plant

## Pseudocode

### Dataset preparation

```text
INPUT: plantseg.zip
OUTPUT: phase_2_dataset/images/* and phase_2_dataset/masks/*

for each image in plantseg/images/{train,val,test}:
    if filename starts with a tomato disease class:
        copy image into phase_2_dataset/images/{split}
        find matching annotation mask
        infer tomato disease class from filename
        convert binary mask into class-index mask
        save mask into phase_2_dataset/masks/{split}
```

### Training

```text
INPUT: phase_2_dataset
OUTPUT: trained U-Net weights

load train and val image-mask pairs
initialize U-Net model
for each epoch:
    for each batch:
        preprocess images
        forward pass through U-Net
        compute segmentation loss
        backpropagate
        update model weights
    evaluate on validation set
    save best model weights
```

### Inference on one plant

```text
INPUT: 5-10 selected leaf images from phase 1
OUTPUT: plant-level disease percentages

load trained U-Net weights
for each selected leaf image:
    preprocess image
    predict disease segmentation map
    derive visible leaf mask
    for each tomato disease class:
        count disease pixels
        compute disease_percentage = disease_pixels / visible_leaf_pixels
    compute healthy percentage from remaining visible area
average all per-leaf percentages
return plant-level disease percentages
```

## Code-style pseudocode

### Dataset preparation structure

```python
def prepare_tomato_subset(zip_path, output_root):
    for split in ["train", "val", "test"]:
        for image_file in list_images_from_zip(zip_path, split):
            class_name = infer_tomato_class(image_file.name)
            if class_name is None:
                continue

            mask_file = find_matching_annotation(zip_path, split, image_file)
            copy_image(image_file, output_root / "images" / split)
            remapped_mask = convert_binary_mask_to_class_index(mask_file, class_name)
            save_mask(remapped_mask, output_root / "masks" / split)
```

### Training structure

```python
def train_phase_2(dataset_root, weights_output):
    train_dataset = PlantSegTomatoDataset(dataset_root, split="train")
    val_dataset = PlantSegTomatoDataset(dataset_root, split="val")

    model = UNet(in_channels=3, out_channels=num_classes)
    optimizer = Adam(model.parameters(), lr=learning_rate)
    loss_fn = CrossEntropyLoss()

    for epoch in range(num_epochs):
        model.train()
        for images, masks in train_dataset:
            predictions = model(images)
            loss = loss_fn(predictions, masks)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

        val_loss = evaluate(model, val_dataset)
        save_best_model_if_needed(model, val_loss, weights_output)
```

### Inference structure

```python
def infer_one_plant(selected_leaf_image_paths, weights_path):
    model = load_model(weights_path)
    all_leaf_results = []

    for image_path in selected_leaf_image_paths:
        image = preprocess_image(image_path)
        disease_map = model.predict(image)
        leaf_mask = derive_visible_leaf_mask(image)
        disease_percentages = compute_percentages(disease_map, leaf_mask)
        all_leaf_results.append(disease_percentages)

    plant_percentages = average_leaf_percentages(all_leaf_results)
    return plant_percentages
```

### Runtime integration structure

```python
def run_phase_2(context):
    selected_leaf_paths = context["selected_leaf_image_paths"]
    weights_path = context["phase_2_weights"]

    per_leaf_results = []
    for image_path in selected_leaf_paths:
        leaf_result = predict_leaf(image_path, weights_path)
        per_leaf_results.append(leaf_result)

    disease_percentages = aggregate_predictions(per_leaf_results)
    context["phase_2_output"] = disease_percentages
    return context
```

## Files

- [classes.py](C:\Users\sai-y\Downloads\plant\phase_2_disease_detection\classes.py): tomato class mapping
- [dataset.py](C:\Users\sai-y\Downloads\plant\phase_2_disease_detection\dataset.py): PlantSeg tomato subset loader
- [prepare_dataset.py](C:\Users\sai-y\Downloads\plant\phase_2_disease_detection\prepare_dataset.py): prepares the local tomato-only subset
- [model.py](C:\Users\sai-y\Downloads\plant\phase_2_disease_detection\model.py): U-Net segmentation model
- [train.py](C:\Users\sai-y\Downloads\plant\phase_2_disease_detection\train.py): training entrypoint
- [infer.py](C:\Users\sai-y\Downloads\plant\phase_2_disease_detection\infer.py): inference helpers
- [phase.py](C:\Users\sai-y\Downloads\plant\phase_2_disease_detection\phase.py): runtime integration with the full pipeline

## Current note

Camera-condition mismatch is intentionally neglected for now, as decided in the project discussion.
