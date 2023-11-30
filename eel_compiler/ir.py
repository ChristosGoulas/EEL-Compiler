from dataclasses import dataclass
from typing import Any, List, Union


@dataclass
class Quadruple:
    id: int
    op: str
    arg1: Any
    arg2: Any
    target: Any

    def to_list(self) -> List[Any]:
        return [self.id, self.op, self.arg1, self.arg2, self.target]

    def __getitem__(self, idx: int) -> Any:
        items = self.to_list()
        return items[idx]

    def __setitem__(self, idx: int, value: Any) -> None:
        if idx == 0:
            self.id = value
        elif idx == 1:
            self.op = value
        elif idx == 2:
            self.arg1 = value
        elif idx == 3:
            self.arg2 = value
        elif idx == 4:
            self.target = value
        else:
            raise IndexError("Quadruple index out of range")

    def __len__(self) -> int:
        return 5

    def __str__(self) -> str:
        return f"[{self.id}, {repr(self.op)}, {repr(self.arg1)}, {repr(self.arg2)}, {repr(self.target)}]"


class IRManager:
    """Manages quadruple generation and backpatching lists for control flow."""

    def __init__(self) -> None:
        self.quads: List[List[Any]] = []

    def next_quad(self) -> int:
        return len(self.quads) + 1

    def gen_quad(self, op: str, x: Any, y: Any, z: Any) -> int:
        qid = self.next_quad()
        quad = [qid, op, x, y, z]
        self.quads.append(quad)
        return qid

    def backpatch(self, quad_list: List[int], z: Any) -> None:
        for target_id in quad_list:
            for q in self.quads:
                if q[0] == target_id:
                    q[4] = z
                    break

    @staticmethod
    def empty_list() -> List[int]:
        return []

    @staticmethod
    def make_list(x: int) -> List[int]:
        return [x]

    @staticmethod
    def merge_list(list1: List[int], list2: List[int]) -> List[int]:
        return list1 + list2
