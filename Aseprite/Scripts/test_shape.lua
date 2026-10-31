-- Phase 1 bridge test: canvas, two layers, integer-coordinate shape, save, export.
-- Parameters (passed with --script-param): width, height, out_ase, out_png
local width = tonumber(app.params["width"]) or 32
local height = tonumber(app.params["height"]) or 48
local out_ase = app.params["out_ase"]
local out_png = app.params["out_png"]
assert(out_ase and out_png, "out_ase and out_png are required")

local sprite = Sprite(width, height, ColorMode.RGB)
local base = sprite.layers[1]
base.name = "Base"
local outline = sprite:newLayer()
outline.name = "Outline"
local cel_base = sprite:newCel(base, 1)
local cel_outline = sprite:newCel(outline, 1)

local fill = Color{ r = 90, g = 90, b = 100, a = 255 }
local edge = Color{ r = 20, g = 20, b = 30, a = 255 }
local x0, y0, x1, y1 = 8, 12, 23, 35

local img = cel_base.image
local img_o = cel_outline.image
for y = y0, y1 do
  for x = x0, x1 do
    img:putPixel(x, y, fill)
    if x == x0 or x == x1 or y == y0 or y == y1 then
      img_o:putPixel(x, y, edge)
    end
  end
end

sprite:saveAs(out_ase)
sprite:saveCopyAs(out_png)
