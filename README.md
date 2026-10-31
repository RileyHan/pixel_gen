# pixel_gen
Pixel art generator that creates aseprite files with pixel images not generated images that look like pixels.

## Phase 1: Python-to-Aseprite bridge
Set `ASEPRITE_PATH` if Aseprite is not on PATH, then run `python Python_Tools/aseprite_bridge.py [out_dir]`.
It runs `Aseprite/Scripts/test_shape.lua` (32x48 canvas, two layers, integer-coordinate rectangle),
saves `.aseprite` + PNG and validates size and transparency (needs Pillow). Tests: `python -m unittest discover -s tests`.
