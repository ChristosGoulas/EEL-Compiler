import argparse
import sys
from typing import Optional, List

from . import compile_file


def main(args: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="eel-compiler",
        description="Single-pass compiler for EEL (Educational Imperative Language) targeting MIPS assembly, quadruples, and ANSI C."
    )
    parser.add_argument("source_file", help="Path to EEL source code file (.eel)")
    parser.add_argument("-o", "--output-dir", help="Custom output directory for compiled artifacts", default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose compilation logs (quadruples and artifact paths)")
    parser.add_argument("-O", "--optimize", action="store_true", help="Enable IR quadruple optimization (constant folding and dead code elimination)")

    parsed_args = parser.parse_args(args)

    try:
        compile_file(
            parsed_args.source_file,
            parsed_args.output_dir,
            verbose=parsed_args.verbose,
            optimize=parsed_args.optimize
        )
        return 0
    except Exception as e:
        print(f"Compilation failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
