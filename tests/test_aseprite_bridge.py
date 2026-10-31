import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "Python_Tools"))
import aseprite_bridge as ab


class BridgeTests(unittest.TestCase):
    def test_find_uses_env(self):
        with tempfile.NamedTemporaryFile() as f, mock.patch.dict("os.environ", {"ASEPRITE_PATH": f.name}):
            self.assertEqual(ab.find_aseprite(), Path(f.name))

    def test_find_missing(self):
        with mock.patch.dict("os.environ", {"ASEPRITE_PATH": ""}), \
                mock.patch("shutil.which", return_value=None), \
                mock.patch.object(Path, "is_file", return_value=False):
            with self.assertRaises(ab.AsepriteError):
                ab.find_aseprite()

    def test_run_lua_command(self):
        lua = ab.SCRIPTS_DIR / "test_shape.lua"
        done = mock.Mock(returncode=0, stdout="ok", stderr="")
        with mock.patch("subprocess.run", return_value=done) as run:
            ab.run_lua(lua, {"width": 32}, aseprite="/x/aseprite")
        cmd = run.call_args[0][0]
        self.assertEqual(cmd[:2], ["/x/aseprite", "--batch"])
        self.assertIn("width=32", cmd)

    def test_run_lua_failure(self):
        done = mock.Mock(returncode=1, stdout="", stderr="bad")
        with mock.patch("subprocess.run", return_value=done):
            with self.assertRaises(ab.AsepriteError):
                ab.run_lua(ab.SCRIPTS_DIR / "test_shape.lua", aseprite="/x")


if __name__ == "__main__":
    unittest.main()
