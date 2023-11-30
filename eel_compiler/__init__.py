import os
from typing import List, Tuple, Any, Optional

from .lexer import Lexer
from .parser import Parser
from .codegen.c_emitter import CEmitter
from .optimizer import optimize_quads


class Compiler:
    """EEL Compiler pipeline driver."""

    def __init__(
        self,
        source_code: str,
        output_dir: str,
        pure_name: str,
        verbose: bool = False,
        optimize: bool = False
    ) -> None:
        self.source_code = source_code
        self.output_dir = output_dir
        self.pure_name = pure_name
        self.verbose = verbose
        self.optimize = optimize

    def compile(self) -> List[List[Any]]:
        os.makedirs(self.output_dir, exist_ok=True)

        int_path = os.path.join(self.output_dir, f"{self.pure_name}.int")
        c_path = os.path.join(self.output_dir, f"{self.pure_name}.c")
        asm_path = os.path.join(self.output_dir, f"{self.pure_name}.asm")

        lexer = Lexer(self.source_code)

        with open(asm_path, 'w+') as asm_file:
            asm_file.write('\t j L_  \n')
            parser = Parser(lexer, asm_file)
            quads = parser.parse()

            if self.optimize:
                quads = optimize_quads(quads)

            asm_file.seek(0)
            asm_file.write(f'\t j L_{parser.main_sq}\n')

        with open(int_path, 'w') as int_file:
            for q in quads:
                if self.verbose:
                    print(q)
                int_file.write(f"{q}\n")

        with open(c_path, 'w') as c_file:
            CEmitter.generate(quads, c_file)

        if self.verbose:
            print(f"Generated intermediate code: {int_path}")
            print(f"Generated MIPS assembly: {asm_path}")
            print(f"Generated ANSI C pseudocode: {c_path}")

        return quads


def compile_file(
    source_file_path: str,
    output_dir: Optional[str] = None,
    verbose: bool = False,
    optimize: bool = False
) -> List[List[Any]]:
    pure_name = os.path.splitext(os.path.basename(source_file_path))[0]
    if output_dir is None:
        output_dir = os.path.join('compiler_results', pure_name)

    with open(source_file_path, 'r') as f:
        code = f.read()

    compiler = Compiler(code, output_dir, pure_name, verbose=verbose, optimize=optimize)
    return compiler.compile()


__all__ = ["Compiler", "compile_file", "Lexer", "Parser", "CEmitter", "optimize_quads"]
