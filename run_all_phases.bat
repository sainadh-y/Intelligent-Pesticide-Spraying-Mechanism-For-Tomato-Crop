@echo off
setlocal

set "ROOT=%~dp0"
set "PLANT_ID=%~1"
if "%PLANT_ID%"=="" set "PLANT_ID=plant_001"

set "PLANT_INDEX=%~2"
if "%PLANT_INDEX%"=="" set "PLANT_INDEX=1"

set "INPUT_IMAGE_DIR=%~3"
if "%INPUT_IMAGE_DIR%"=="" set "INPUT_IMAGE_DIR=%ROOT%captures\test_inputs"

set "OUTPUT_DIR=%ROOT%output\launcher_runs\%PLANT_ID%"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

python "%ROOT%start\run_pipeline.py" ^
  --dry-run ^
  --plant-id "%PLANT_ID%" ^
  --plant-index %PLANT_INDEX% ^
  --input-image-dir "%INPUT_IMAGE_DIR%" ^
  --save-json "%OUTPUT_DIR%\result.json"

endlocal
