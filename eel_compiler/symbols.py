from typing import List, Optional, Tuple


class Argument:
    def __init__(self, par_mode: str, arg_next: Optional['Argument'] = None):
        self.par_mode = par_mode
        self.arg_next = arg_next

    @property
    def parMode(self) -> str:
        return self.par_mode

    def set_next(self, arg_next: 'Argument') -> None:
        self.arg_next = arg_next

    def __str__(self) -> str:
        return f" parMode: {self.par_mode} Argnext: {self.arg_next}"


class Entity:
    def __init__(self, name: str, typeof: str):
        self.name = name
        self.typeof = typeof
        self.nextEntity: Optional['Entity'] = None

    def __str__(self) -> str:
        return f" Typeof: {self.typeof} Name: {self.name}"


class Function(Entity):
    def __init__(self, name: str, sq: int = -1):
        super().__init__(name, 'func')
        self.FL: int = -1
        self.SQ: int = sq
        self.arglist: List[Argument] = []

    def enterArg(self, arg: Argument) -> None:
        self.arglist.append(arg)

    def setFL(self, fl: int) -> None:
        self.FL = fl

    def setSQ(self, quad_id: int) -> None:
        self.SQ = quad_id

    def __str__(self) -> str:
        return f"{super().__str__()}, RETV: {self.typeof}, SQ: {self.SQ}, FL: {self.FL}"


class Parameter(Entity):
    def __init__(self, name: str, par_mode: str, offset: int = -1):
        super().__init__(name, 'par')
        self.parMode: str = par_mode
        self.offset: int = offset

    def __str__(self) -> str:
        return f"{super().__str__()} Offset: {self.offset} ParMode: {self.parMode}"


class Variable(Entity):
    def __init__(self, name: str, offset: int = -1):
        super().__init__(name, 'var')
        self.offset: int = offset

    def __str__(self) -> str:
        return f"{super().__str__()} Offset: {self.offset}"


class TempVar(Entity):
    def __init__(self, name: str, offset: int = -1):
        super().__init__(name, 'temp')
        self.offset: int = offset

    def __str__(self) -> str:
        return f"{super().__str__()} Offset: {self.offset}"


class Scope:
    def __init__(self, nesting_level: int = 0):
        self.Entities: List[Entity] = []
        self.nestingLevel: int = nesting_level
        self.offset: int = 12

    def EnterEntity(self, entity: Entity) -> None:
        self.Entities.append(entity)

    def get_offset(self) -> int:
        temp = self.offset
        self.offset += 4
        return temp

    def __str__(self) -> str:
        return f"NestingLevel: {self.nestingLevel} Offset: {self.offset}"
