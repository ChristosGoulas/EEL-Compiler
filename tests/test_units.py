import io
import unittest
import sys
from eel_compiler.tokens import Token, TokenType
from eel_compiler.lexer import Lexer
from eel_compiler.errors import LexerError, EELError
from eel_compiler.ir import IRManager
from eel_compiler.symbols import Scope, Variable, Parameter, Function, TempVar
from eel_compiler.optimizer import optimize_quads
from eel_compiler.cli import main as cli_main


class TestErrors(unittest.TestCase):

    def test_rich_error_formatting(self):
        err = EELError("Expected ';'", line=10, column=5, source_line="x := 10 +")
        formatted = str(err)
        self.assertIn("Error (line 10, col 5): Expected ';'", formatted)
        self.assertIn("x := 10 +", formatted)
        self.assertIn("^", formatted)


class TestOptimizer(unittest.TestCase):

    def test_constant_folding(self):
        quads = [
            [1, "+", "10", "20", "T_0"],
            [2, "*", "T_0", "1", "T_1"],
            [3, "-", "50", "5", "T_2"],
        ]
        optimized = optimize_quads(quads)
        self.assertEqual(optimized[0], [1, ":=", "30", "", "T_0"])
        self.assertEqual(optimized[1], [2, ":=", "T_0", "", "T_1"])
        self.assertEqual(optimized[2], [3, ":=", "45", "", "T_2"])

    def test_dead_code_elimination(self):
        quads = [
            [1, ":=", "10", "", "x"],
            [2, "jump", "", "", 5],
            [3, ":=", "20", "", "y"],  # Dead code
            [4, ":=", "30", "", "z"],  # Dead code
            [5, "out", "x", "", ""],
        ]
        optimized = optimize_quads(quads)
        self.assertEqual(len(optimized), 3)
        self.assertEqual(optimized[0][0], 1)
        self.assertEqual(optimized[1][0], 2)
        self.assertEqual(optimized[2][0], 5)


class TestLexer(unittest.TestCase):

    def test_lexer_basic_tokens(self):
        code = "program test declare x enddeclare x := 42 ; endprogram"
        lexer = Lexer(code)

        t1 = lexer.get_next_token()
        self.assertEqual(t1.type, TokenType.PROGRAM)
        self.assertEqual(t1.value, "program")

        t2 = lexer.get_next_token()
        self.assertEqual(t2.type, TokenType.ID)
        self.assertEqual(t2.value, "test")

        t3 = lexer.get_next_token()
        self.assertEqual(t3.type, TokenType.DECLARE)

    def test_lexer_out_of_bounds_number(self):
        code = "32768"
        lexer = Lexer(code)
        with self.assertRaises(LexerError):
            lexer.get_next_token()

    def test_lexer_comment_stripping(self):
        code = "// line comment\nx := 1 /* block comment */ + 2"
        lexer = Lexer(code)

        t1 = lexer.get_next_token()
        self.assertEqual(t1.type, TokenType.ID)
        self.assertEqual(t1.value, "x")

        t2 = lexer.get_next_token()
        self.assertEqual(t2.type, TokenType.ASSIGN)

        t3 = lexer.get_next_token()
        self.assertEqual(t3.type, TokenType.CONST)
        self.assertEqual(t3.value, "1")

        t4 = lexer.get_next_token()
        self.assertEqual(t4.type, TokenType.PLUS)


class TestIRManager(unittest.TestCase):

    def test_quad_generation_and_backpatch(self):
        ir = IRManager()
        q1 = ir.gen_quad("jump", "", "", "")
        self.assertEqual(q1, 1)

        q2 = ir.gen_quad("+", "a", "b", "T_0")
        self.assertEqual(q2, 2)

        ir.backpatch([1], 10)
        self.assertEqual(ir.quads[0][4], 10)


class TestSymbols(unittest.TestCase):

    def test_scope_and_entities(self):
        scope = Scope(nesting_level=1)
        self.assertEqual(scope.get_offset(), 12)
        self.assertEqual(scope.get_offset(), 16)

        v = Variable("x", 12)
        scope.EnterEntity(v)
        self.assertEqual(len(scope.Entities), 1)
        self.assertEqual(scope.Entities[0].name, "x")


class TestCEmitter(unittest.TestCase):

    def test_c_emitter_output(self):
        from eel_compiler.codegen.c_emitter import CEmitter
        quads = [
            [1, "begin_block", "test", " ", " "],
            [2, ":=", "10", "", "x"],
            [3, "+", "x", "5", "T_0"],
            [4, "out", "T_0", "", ""],
            [5, "halt", " ", " ", " "],
            [6, "end_block", "test", " ", " "],
        ]
        out_buf = io.StringIO()
        CEmitter.generate(quads, out_buf)
        c_code = out_buf.getvalue()

        self.assertIn("#include <stdio.h>", c_code)
        self.assertIn("int main()", c_code)
        self.assertIn("int x, T_0;", c_code)
        self.assertIn("L_2: x = 10;", c_code)
        self.assertIn("L_3: T_0 = x + 5;", c_code)
        self.assertIn('L_4: printf("%d\\n", T_0);', c_code)


class TestCLI(unittest.TestCase):

    def test_cli_help(self):
        stdout_trap = io.StringIO()
        stderr_trap = io.StringIO()
        old_stdout, old_stderr = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = stdout_trap, stderr_trap
            with self.assertRaises(SystemExit) as cm:
                cli_main(["--help"])
            self.assertEqual(cm.exception.code, 0)
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

    def test_cli_verbose_and_optimize_flags(self):
        import tempfile
        import os
        import shutil

        with tempfile.NamedTemporaryFile(mode="w+", prefix="cli_test_", suffix=".eel", delete=False) as f:
            f.write("program test declare x enddeclare x := 10 + 5 ; print x ; endprogram")
            f_path = f.name

        pure_name = os.path.splitext(os.path.basename(f_path))[0]
        out_dir = tempfile.mkdtemp(prefix="cli_out_")
        stdout_trap = io.StringIO()
        old_stdout = sys.stdout

        try:
            sys.stdout = stdout_trap
            ret = cli_main([f_path, "-o", out_dir, "-v", "-O"])
            self.assertEqual(ret, 0)
            output = stdout_trap.getvalue()
            self.assertIn("Generated intermediate code", output)
            self.assertIn("Generated MIPS assembly", output)
            self.assertIn("Generated ANSI C pseudocode", output)
            self.assertTrue(os.path.exists(os.path.join(out_dir, f"{pure_name}.int")))
            self.assertTrue(os.path.exists(os.path.join(out_dir, f"{pure_name}.asm")))
            self.assertTrue(os.path.exists(os.path.join(out_dir, f"{pure_name}.c")))
        finally:
            sys.stdout = old_stdout
            if os.path.exists(f_path):
                os.remove(f_path)
            if os.path.exists(out_dir):
                shutil.rmtree(out_dir)


if __name__ == "__main__":
    unittest.main()
