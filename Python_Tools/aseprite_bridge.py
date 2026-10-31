"""Python-to-Aseprite bridge (Phase 1): locate Aseprite, run Lua, validate output."""
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

log = logging.getLogger("aseprite_bridge")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "Aseprite" / "Scripts"

_WINDOWS_CANDIDATES = [
    r"C:\Program Files\Aseprite\Aseprite.exe",
    r"C:\Program Files (x86)\Aseprite\Aseprite.exe",
    r"C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe",
    r"C:\Program Files\Steam\steamapps\common\Aseprite\Aseprite.exe",
]


class AsepriteError(RuntimeError):
    pass


def find_aseprite():
    """Return the path to the Aseprite executable (ASEPRITE_PATH, PATH, then defaults)."""
    env = os.environ.get("ASEPRITE_PATH")
    if env and Path(env).is_file():
        return Path(env)
    found = shutil.which("aseprite") or shutil.which("Aseprite")
    if found:
        return Path(found)
    for cand in _WINDOWS_CANDIDATES:
        if Path(cand).is_file():
            return Path(cand)
    raise AsepriteError("Aseprite not found. Set ASEPRITE_PATH to the executable.")


def run_lua(script, params=None, aseprite=None, timeout=60):
    """Run a Lua script in batch mode with --script-param key=value pairs."""
    exe = Path(aseprite) if aseprite else find_aseprite()
    script = Path(script)
    if not script.is_file():
        raise AsepriteError(f"Lua script not found: {script}")
    cmd = [str(exe), "--batch"]
    for key, value in (params or {}).items():
        cmd += ["--script-param", f"{key}={value}"]
    cmd += ["--script", str(script)]
    log.info("Running: %s", cmd)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AsepriteError(f"Failed to run Aseprite: {exc}") from exc
    if result.returncode != 0:
        raise AsepriteError(f"Aseprite exited with {result.returncode}: {result.stderr.strip()}")
    return result.stdout


def validate_png(path, width, height):
    """Check PNG dimensions and that it has transparent pixels. Requires Pillow."""
    from PIL import Image

    path = Path(path)
    if not path.is_file():
        raise AsepriteError(f"PNG not created: {path}")
    with Image.open(path) as im:
        if im.size != (width, height):
            raise AsepriteError(f"Unexpected size {im.size}, expected {(width, height)}")
        alpha = im.convert("RGBA").getchannel("A")
        if alpha.getextrema()[0] != 0:
            raise AsepriteError("PNG has no transparent pixels")
        if alpha.getextrema()[1] == 0:
            raise AsepriteError("PNG is fully transparent")
    return True


def create_test_asset(out_dir, name="bridge_test", width=32, height=48, aseprite=None):
    """Run the Phase 1 test: 32x48 canvas, two layers, shape, .aseprite + PNG, validate."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ase, png = out_dir / f"{name}.aseprite", out_dir / f"{name}.png"
    run_lua(
        SCRIPTS_DIR / "test_shape.lua",
        {"width": width, "height": height, "out_ase": ase, "out_png": png},
        aseprite=aseprite,
    )
    if not ase.is_file():
        raise AsepriteError(f".aseprite not created: {ase}")
    validate_png(png, width, height)
    log.info("Created and validated %s and %s", ase, png)
    return ase, png


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT_ROOT / "Exports"
    try:
        create_test_asset(out)
    except (AsepriteError, ImportError) as exc:
        log.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
