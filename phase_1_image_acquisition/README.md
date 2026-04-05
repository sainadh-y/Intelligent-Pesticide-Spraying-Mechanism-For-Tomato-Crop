# Phase 1: Image Acquisition

## Goal

Move the belt to the current tomato plant, capture multiple images, and keep the clearest `5-10` leaf images for later phases.

## Completion status

Completed.

## Final demo assumptions used

- 3-plant demo row
- movement flow: `start -> plant 1 -> plant 2 -> plant 3 -> stop`
- 12V `500 RPM` geared motor
- `2.5 inch` drive wheel
- practical control speed assumed in code: `5 inches/second`
- timed stopping used for plant positioning
- current leaf selection uses clarity scoring, with YOLO kept only as an optional hook

## Demo hardware target

- Raspberry Pi 4B
- Raspberry Pi Camera
- L298N motor driver for belt movement
- belt movement controlled with timed stopping for demo

## Current implementation

- supports dry-run mode
- supports reading images from an existing folder for development
- supports RaspiCam capture through `Picamera2`
- uses L298N-style `IN1/IN2/ENA` belt control
- uses plant-index based movement timing for the 3-plant demo
- computes focus score using Laplacian variance
- has a YOLO hook that can be connected later with custom weights

## 3-plant timing defaults

- start to plant 1 = `0.8 s`
- start to plant 2 = `1.8 s`
- start to plant 3 = `2.8 s`
- belt speed = `0.10`

## Output of this phase

- raw image file paths
- selected leaf image file paths
- image acquisition summary
