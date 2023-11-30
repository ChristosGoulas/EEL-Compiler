import os
import sys
import shutil
import tempfile
import unittest
import subprocess

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import compiler


class TestEELCompiler(unittest.TestCase):

    def setUp(self):
        compiler.reset_compiler_state()

    def test_example1_compilation(self):
        example_path = os.path.join(PROJECT_ROOT, "examples", "example1.eel")
        res = subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "compiler.py"), example_path],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Program ok", res.stdout)
        self.assertNotIn("ERROR", res.stdout)

        output_dir = os.path.join(PROJECT_ROOT, "compiler_results", "example1")
        self.assertTrue(os.path.exists(os.path.join(output_dir, "example1.int")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "example1.asm")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "example1.c")))

    def test_example2_compilation(self):
        example_path = os.path.join(PROJECT_ROOT, "examples", "example2.eel")
        res = subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "compiler.py"), example_path],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Program ok", res.stdout)
        self.assertNotIn("ERROR", res.stdout)

        output_dir = os.path.join(PROJECT_ROOT, "compiler_results", "example2")
        self.assertTrue(os.path.exists(os.path.join(output_dir, "example2.int")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "example2.asm")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "example2.c")))

    def test_example3_compilation(self):
        example_path = os.path.join(PROJECT_ROOT, "examples", "example3.eel")
        res = subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "compiler.py"), example_path],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Program ok", res.stdout)
        self.assertNotIn("ERROR", res.stdout)

        output_dir = os.path.join(PROJECT_ROOT, "compiler_results", "example3")
        self.assertTrue(os.path.exists(os.path.join(output_dir, "example3.int")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "example3.asm")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "example3.c")))

    def test_generated_c_compiles(self):
        cc = shutil.which("gcc") or shutil.which("clang")
        if not cc:
            self.skipTest("C compiler (gcc/clang) not available")

        suffix = ".exe" if sys.platform == "win32" else ".out"

        for ex in ["example1", "example2", "example3"]:
            c_file = os.path.join(PROJECT_ROOT, "compiler_results", ex, f"{ex}.c")
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                out_path = tmp.name

            try:
                res = subprocess.run([cc, "-Wall", "-Wextra", c_file, "-o", out_path],
                                     capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, f"GCC build failed for {ex}: {res.stderr}")
            finally:
                if os.path.exists(out_path):
                    os.remove(out_path)

    def test_optimized_compilation(self):
        example_path = os.path.join(PROJECT_ROOT, "examples", "example1.eel")
        res = subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "compiler.py"), example_path, "-O", "-v"],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Generated intermediate code", res.stdout)
        self.assertNotIn("ERROR", res.stdout)

    def test_exit_outside_loop_error(self):
        with tempfile.NamedTemporaryFile(mode="w+", prefix="invalid_test_", suffix=".eel", delete=False) as f:
            f.write("program test declare x enddeclare exit endprogram")
            f_path = f.name

        pure_name = os.path.splitext(os.path.basename(f_path))[0]
        out_dir = os.path.join(PROJECT_ROOT, "compiler_results", pure_name)

        try:
            res = subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "compiler.py"), f_path],
                                 capture_output=True, text=True)
            self.assertIn("ERROR: exit statement outside repeat loop", res.stdout)
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)
            if os.path.exists(out_dir):
                shutil.rmtree(out_dir)


if __name__ == "__main__":
    unittest.main()
