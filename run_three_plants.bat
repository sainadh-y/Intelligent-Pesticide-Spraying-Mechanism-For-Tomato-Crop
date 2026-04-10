@echo off
setlocal

set "ROOT=%~dp0"
set "INPUT_IMAGE_DIR=%~1"
if "%INPUT_IMAGE_DIR%"=="" set "INPUT_IMAGE_DIR=%ROOT%captures\test_inputs"

set "OUTPUT_DIR=%ROOT%output\three_plants"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

python "%ROOT%start\run_pipeline.py" --dry-run --plant-id plant_001 --plant-index 1 --input-image-dir "%INPUT_IMAGE_DIR%" --save-json "%OUTPUT_DIR%\plant_001_result.json"
python "%ROOT%start\run_pipeline.py" --dry-run --plant-id plant_002 --plant-index 2 --input-image-dir "%INPUT_IMAGE_DIR%" --save-json "%OUTPUT_DIR%\plant_002_result.json"
python "%ROOT%start\run_pipeline.py" --dry-run --plant-id plant_003 --plant-index 3 --input-image-dir "%INPUT_IMAGE_DIR%" --save-json "%OUTPUT_DIR%\plant_003_result.json"

echo.
echo Saved results to: %OUTPUT_DIR%

endlocal
