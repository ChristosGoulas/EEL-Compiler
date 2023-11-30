"""EEL Compiler entrypoint script wrapper."""

import sys
import os
from eel_compiler.cli import main as cli_main
from eel_compiler import compile_file, Lexer, Parser
from eel_compiler.symbols import Scope, Variable, Parameter, Function, TempVar, Argument

# Legacy global variables for backwards compatibility
source_code = ""
position = 0
lines = 0
state = 0
tokenboard = ["", ""]
quad = []
scopes = []
allfd = []
listcall = []
listdec = []
num = 0
parameters = []
quad_id = 0
repeat_count = 0
return_count = 0
mainSQ = 0
mainFL = 0
mainname = ""
qid = 0


def reset_compiler_state():
    global allfd, listcall, listdec, num, parameters, quad, quad_id
    global repeat_count, return_count, scopes, mainSQ, mainFL, mainname, qid
    allfd = []
    listcall = []
    listdec = []
    num = 0
    parameters = []
    quad = []
    quad_id = 0
    repeat_count = 0
    return_count = 0
    scopes = []
    mainSQ = 0
    mainFL = 0
    mainname = ""
    qid = 0


def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog="compiler.py",
        description="EEL Compiler entrypoint script wrapper"
    )
    parser.add_argument("source_file", help="Path to EEL source code file (.eel)")
    parser.add_argument("-o", "--output-dir", help="Custom output directory for compiled artifacts", default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose compilation logs (quadruples and artifact paths)")
    parser.add_argument("-O", "--optimize", action="store_true", help="Enable IR quadruple optimization (constant folding and dead code elimination)")

    args = parser.parse_args()
    reset_compiler_state()
    compile_file(args.source_file, args.output_dir, verbose=args.verbose, optimize=args.optimize)


if __name__ == "__main__":
    main()
