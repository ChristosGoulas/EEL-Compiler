from typing import List, TextIO, Tuple, Any, Optional
from ..symbols import Scope, Function


class MIPSGenerator:
    """Generates MIPS 32-bit assembly code from intermediate quadruples and symbol scopes."""

    def __init__(self, scopes: List[Scope], main_name: str, main_sq: int, main_fl: int, assembly_file: TextIO) -> None:
        self.scopes = scopes
        self.main_name = main_name
        self.main_sq = main_sq
        self.main_fl = main_fl
        self.assembly_file = assembly_file
        self.parameters: List[List[Any]] = []

    def search_entity(self, name: str, typeof: str) -> Tuple[Any, int]:
        for scope in self.scopes:
            for entity in scope.Entities:
                if entity.name == name and entity.typeof == typeof:
                    return entity, scope.nestingLevel
        return None, 0

    def search_entity_1(self, name: str) -> Tuple[Any, int]:
        for i in range(len(self.scopes) - 1, -1, -1):
            for entity in self.scopes[i].Entities:
                if entity.name == name:
                    return entity, self.scopes[i].nestingLevel
        return None, 0

    def gnvlcode(self, name: str) -> None:
        fname, nest = self.search_entity_1(name)
        if fname and fname.typeof != 'func':
            self.assembly_file.write('\t lw $t0,-4($sp)\n')
            nest += 1
            while nest < self.scopes[-1].nestingLevel:
                self.assembly_file.write('\t lw $t0,-4($sp)\n')
                nest += 1
            self.assembly_file.write(f'\t addi $t0,$t0,-{fname.offset}\n')

    def loadvr(self, v: Any, r: int) -> None:
        v_str = str(v)
        if v_str.isdigit() or (v_str.startswith('-') and v_str[1:].isdigit()):
            self.assembly_file.write(f'\t li $t{r},{v_str}\n')
            return

        fname, nest = self.search_entity_1(v_str)
        if not fname:
            print('ERROR: Variable is NOT declared: ', v_str)
            return

        current_nesting = self.scopes[-1].nestingLevel if self.scopes else 0

        if fname.typeof == 'var':
            if len(self.scopes) == 0:
                self.assembly_file.write(f'\t lw $t{r},-{fname.offset}($s0)\n')
            elif nest == current_nesting:
                self.assembly_file.write(f'\t lw $t{r},-{fname.offset}($sp)\n')
            elif nest < current_nesting:
                self.gnvlcode(v_str)
                self.assembly_file.write(f'\t lw $t{r},0($t0)\n')

        elif fname.typeof == 'par':
            if fname.parMode == 'CV' and nest == current_nesting:
                self.assembly_file.write(f'\t lw $t{r},-{fname.offset}($sp)\n')
            elif fname.parMode == 'REF' and nest == current_nesting:
                self.assembly_file.write(f'\t lw $t0,-{fname.offset}($sp)\n')
                self.assembly_file.write(f'\t lw $t{r},0($t0)\n')
            elif fname.parMode == 'CV' and nest < current_nesting:
                self.gnvlcode(v_str)
                self.assembly_file.write(f'\t lw $t{r},0($t0)\n')
            elif fname.parMode == 'REF' and nest < current_nesting:
                self.gnvlcode(v_str)
                self.assembly_file.write('\t lw $t0,($t0)\n')
                self.assembly_file.write(f'\t lw $t{r},0($t0)\n')

        elif fname.typeof == 'temp':
            self.assembly_file.write(f'\t lw $t{r},-{fname.offset}($sp)\n')

    def storerv(self, r: int, v: Any) -> None:
        v_str = str(v)
        fname, nest = self.search_entity_1(v_str)
        if not fname:
            return

        current_nesting = self.scopes[-1].nestingLevel if self.scopes else 0

        if fname.typeof == 'var':
            if len(self.scopes) == 0:
                self.assembly_file.write(f'\t sw $t{r},-{fname.offset}($s0)\n')
            elif nest == current_nesting:
                self.assembly_file.write(f'\t sw $t{r},-{fname.offset}($sp)\n')
            elif nest < current_nesting:
                self.gnvlcode(fname.name)
                self.assembly_file.write(f'\t sw $t{r},($t0)\n')

        elif fname.typeof == 'par':
            if fname.parMode == 'CV' and nest == current_nesting:
                self.assembly_file.write(f'\t sw $t{r},-{fname.offset}($sp)\n')
            elif fname.parMode == 'REF' and nest == current_nesting:
                self.assembly_file.write(f'\t lw $t0,-{fname.offset}($sp)\n')
                self.assembly_file.write(f'\t sw $t{r},($t0)\n')
            elif fname.parMode == 'CV' and nest < current_nesting:
                self.gnvlcode(fname.name)
                self.assembly_file.write(f'\t sw $t{r},($t0)\n')
            elif fname.parMode == 'REF' and nest < current_nesting:
                self.gnvlcode(fname.name)
                self.assembly_file.write('\t lw $t0,($t0)\n')
                self.assembly_file.write(f'\t sw $t{r},($t0)\n')

        elif fname.typeof == 'temp':
            self.assembly_file.write(f'\t sw $t{r},-{fname.offset}($sp)\n')

    def generate_block_assembly(self, quad: List[List[Any]], block_name: str) -> None:
        if block_name == self.main_name:
            sq = self.main_sq
        else:
            fname, nest = self.search_entity(block_name, 'func')
            sq = fname.SQ if fname else 1

        for q in quad[sq - 1:]:
            qid, op, arg1, arg2, target = q[0], q[1], q[2], q[3], q[4]
            self.assembly_file.write(f'L_{qid}:\n')

            if op == 'jump':
                self.assembly_file.write(f'\t j L_{target}\n')
            elif op == '=':
                self.loadvr(arg1, 1)
                self.loadvr(arg2, 2)
                self.assembly_file.write(f'\t beq $t1,$t2,L_{target}\n')
            elif op == '<>':
                self.loadvr(arg1, 1)
                self.loadvr(arg2, 2)
                self.assembly_file.write(f'\t bne $t1,$t2,L_{target}\n')
            elif op == '>':
                self.loadvr(arg1, 1)
                self.loadvr(arg2, 2)
                self.assembly_file.write(f'\t bgt $t1,$t2,L_{target}\n')
            elif op == '<':
                self.loadvr(arg1, 1)
                self.loadvr(arg2, 2)
                self.assembly_file.write(f'\t blt $t1,$t2,L_{target}\n')
            elif op == '>=':
                self.loadvr(arg1, 1)
                self.loadvr(arg2, 2)
                self.assembly_file.write(f'\t bge $t1,$t2,L_{target}\n')
            elif op == '<=':
                self.loadvr(arg1, 1)
                self.loadvr(arg2, 2)
                self.assembly_file.write(f'\t ble $t1,$t2,L_{target}\n')
            elif op == ':=':
                self.loadvr(arg1, 1)
                self.storerv(1, target)
            elif op == '+':
                self.loadvr(arg1, 1)
                self.loadvr(arg2, 2)
                self.assembly_file.write('\t add $t1,$t1,$t2\n')
                self.storerv(1, target)
            elif op == '-':
                self.loadvr(arg1, 1)
                self.loadvr(arg2, 2)
                self.assembly_file.write('\t sub $t1,$t1,$t2\n')
                self.storerv(1, target)
            elif op == '*':
                self.loadvr(arg1, 1)
                self.loadvr(arg2, 2)
                self.assembly_file.write('\t mul $t1,$t1,$t2\n')
                self.storerv(1, target)
            elif op == '/':
                self.loadvr(arg1, 1)
                self.loadvr(arg2, 2)
                self.assembly_file.write('\t div $t1,$t1,$t2\n')
                self.storerv(1, target)
            elif op == 'out':
                self.assembly_file.write('\t li $v0,1\n')
                self.loadvr(arg1, 1)
                self.assembly_file.write('\t addi $a0,$t1,0\n')
                self.assembly_file.write('\t syscall\n')
            elif op == 'inp':
                self.assembly_file.write('\t li $v0,5\n')
                self.assembly_file.write('\t syscall\n')
            elif op == 'RET':
                self.loadvr(target, 1)
                self.assembly_file.write('\t lw $t0,-8($sp)\n')
                self.assembly_file.write('\t sw $t1,($t0)\n')
            elif op == 'par':
                if block_name == self.main_name:
                    fl = self.main_fl
                    self.assembly_file.write(f'\t addi $fp,$sp,{self.main_fl}\n')
                    level = 0
                else:
                    fname, fnest = self.search_entity(block_name, 'func')
                    fl = fname.FL if fname else 0
                    level = fnest

                if len(self.parameters) == 0:
                    self.assembly_file.write(f'\t add $fp,$sp,{fl}\n')

                self.parameters.append(q)
                distance = 12 + 4 * len(self.parameters)

                if arg2 == 'CV':
                    self.loadvr(arg1, 0)
                    self.assembly_file.write(f'\t sw $t0, -{distance}($fp)\n')
                elif arg2 == 'REF':
                    qname, qnest = self.search_entity_1(arg1)
                    if qname:
                        if qname.typeof == 'var' and qnest == level:
                            self.assembly_file.write(f'\t addi $t0, $sp,-{qname.offset}')
                            self.assembly_file.write(f'\t sw $t0, -{distance}($fp)\n')
                        if qname.typeof == 'par' and qnest == level and qname.parMode == 'CV':
                            self.assembly_file.write(f'\t addi $t0, $sp,-{qname.offset}\n')
                            self.assembly_file.write(f'\t sw $t0, -{distance}($fp)\n')
                        if qname.typeof == 'par' and qnest == level and qname.parMode == 'REF':
                            self.assembly_file.write(f'\t lw $t0,-{qname.offset}($sp)\n')
                            self.assembly_file.write(f'\t sw $t0, -{distance}($fp)\n')
                        if (qname.typeof == 'par' and qnest != level and qname.parMode == 'CV') or (qname.typeof == 'var' and qnest != level):
                            self.gnvlcode(arg1)
                            self.assembly_file.write(f'\t sw $t0, -{distance}($fp)\n')
                        if qname.typeof == 'par' and qnest != level and qname.parMode == 'REF':
                            self.gnvlcode(arg1)
                            self.assembly_file.write('\t lw $t0,($t0)\n')
                            self.assembly_file.write(f'\t sw $t0, -{distance}($fp)\n')
                elif arg2 == 'RET':
                    qname, qnest = self.search_entity_1(arg1)
                    if qname:
                        self.assembly_file.write(f'\t addi $t0,$sp,-{qname.offset}\n')
                        self.assembly_file.write('\t sw $t0,-8($fp)\n')

            elif op == 'call':
                if block_name == self.main_name:
                    fl = self.main_fl
                    self.assembly_file.write(f'\t addi $fp,$sp,{self.main_fl}\n')
                    level = 0
                else:
                    fname, fnest = self.search_entity(block_name, 'func')
                    fl = fname.FL if fname else 0
                    level = fnest

                qname, qnest = self.search_entity_1(arg1)
                if qname:
                    if qnest == level:
                        self.assembly_file.write('\t lw $t0, -4($sp)\n')
                        self.assembly_file.write('\t sw $t0, -4($fp)\n')
                    else:
                        self.assembly_file.write('\t sw $sp,-4($fp)\n')
                        self.assembly_file.write(f'\t addi $sp,$sp,{fl}\n')
                        self.assembly_file.write(f'\t jal L_{qname.SQ}\n')
                        self.assembly_file.write(f'\t addi $sp,$sp,-{fl}\n')

                self.parameters = []

            elif op == 'begin_block' and block_name != self.main_name:
                self.assembly_file.write('\t sw $ra,0($sp)\n')

            elif op == 'begin_block' and block_name == self.main_name:
                self.assembly_file.write(f'\t addi $sp,$sp,{self.main_fl}\n')
                self.assembly_file.write('\t move $s0,$sp\n')

            elif op == 'end_block':
                if block_name != self.main_name:
                    self.assembly_file.write('\t lw $ra,($sp)\n')
                    self.assembly_file.write('\t jr $ra\n')
