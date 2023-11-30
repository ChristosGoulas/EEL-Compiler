from typing import Any, List, Set


class IROptimizer:
    """Intermediate Representation (IR) Quadruple Optimizer.

    Applies optimization passes:
    1. Constant Folding: Evaluates constant expressions at compile time.
    2. Algebraic Simplification: Simplifies identity operations (x + 0, x * 1, x * 0).
    3. Unreachable Code Elimination: Removes dead quadruples after unconditional jumps/returns.
    """

    def __init__(self, quads: List[List[Any]]) -> None:
        self.quads: List[List[Any]] = [list(q) for q in quads]

    def optimize(self) -> List[List[Any]]:
        optimized = self._fold_constants(self.quads)
        optimized = self._eliminate_dead_code(optimized)
        return optimized

    def _is_int(self, val: Any) -> bool:
        if isinstance(val, int):
            return True
        if isinstance(val, str):
            s = val.strip()
            if s.isdigit() or (s.startswith('-') and s[1:].isdigit()):
                return True
        return False

    def _to_int(self, val: Any) -> int:
        return int(str(val).strip())

    def _fold_constants(self, quads: List[List[Any]]) -> List[List[Any]]:
        result: List[List[Any]] = []

        for q in quads:
            qid, op, arg1, arg2, target = q[0], q[1], q[2], q[3], q[4]

            if op in ('+', '-', '*', '/') and self._is_int(arg1) and self._is_int(arg2):
                v1 = self._to_int(arg1)
                v2 = self._to_int(arg2)
                folded: Any = None

                if op == '+':
                    folded = v1 + v2
                elif op == '-':
                    folded = v1 - v2
                elif op == '*':
                    folded = v1 * v2
                elif op == '/' and v2 != 0:
                    folded = v1 // v2

                if folded is not None:
                    result.append([qid, ':=', str(folded), '', target])
                    continue

            # Algebraic simplifications
            if op == '+' and self._is_int(arg2) and self._to_int(arg2) == 0:
                result.append([qid, ':=', arg1, '', target])
                continue
            if op == '*' and self._is_int(arg2) and self._to_int(arg2) == 1:
                result.append([qid, ':=', arg1, '', target])
                continue
            if op == '*' and self._is_int(arg2) and self._to_int(arg2) == 0:
                result.append([qid, ':=', '0', '', target])
                continue

            result.append([qid, op, arg1, arg2, target])

        return result

    def _eliminate_dead_code(self, quads: List[List[Any]]) -> List[List[Any]]:
        if not quads:
            return quads

        # Collect jump targets
        jump_targets: Set[int] = set()
        for q in quads:
            op, target = q[1], q[4]
            if op in ('jump', '=', '<>', '<', '>', '<=', '>=') and isinstance(target, int):
                jump_targets.add(target)

        result: List[List[Any]] = []
        unreachable = False

        for q in quads:
            qid, op = q[0], q[1]

            if qid in jump_targets:
                unreachable = False

            if unreachable:
                continue

            result.append(q)

            if op in ('jump', 'halt') and not (qid + 1 in jump_targets):
                unreachable = True

        return result


def optimize_quads(quads: List[List[Any]]) -> List[List[Any]]:
    """Helper function to run the IR optimization pipeline."""
    optimizer = IROptimizer(quads)
    return optimizer.optimize()
