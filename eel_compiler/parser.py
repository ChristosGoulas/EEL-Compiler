from typing import List, Optional, Tuple, TextIO, Any
from .errors import SyntaxError, SemanticError
from .tokens import Token, TokenType
from .lexer import Lexer
from .symbols import Scope, Entity, Variable, Parameter, Function, TempVar, Argument
from .ir import IRManager
from .codegen.mips import MIPSGenerator


class Parser:
    """Recursive descent parser and semantic analyzer for EEL programming language."""

    def __init__(self, lexer: Lexer, asm_file: TextIO) -> None:
        self.lexer: Lexer = lexer
        self.asm_file: TextIO = asm_file
        self.token: Token = self.lexer.get_next_token()

        self.ir: IRManager = IRManager()
        self.scopes: List[Scope] = []

        self.main_name: str = ""
        self.main_sq: int = 0
        self.main_fl: int = 0

        self.repeat_count: int = 0
        self.return_count: int = 0
        self.temp_num: int = 0

        self.list_dec: List[str] = []
        self.list_call: List[str] = []
        self.all_fd: List[List[str]] = []

    def get_token(self) -> None:
        self.token = self.lexer.get_next_token()

    def add_new_scope(self) -> None:
        nesting = self.scopes[-1].nestingLevel + 1 if self.scopes else 0
        self.scopes.append(Scope(nesting))

    def delete_scope(self) -> None:
        if self.scopes:
            self.scopes.pop()

    def add_entity(self, name: str, typeof: str, par_mode: Optional[str] = None) -> None:
        if typeof == 'var':
            off = self.scopes[-1].get_offset()
            self.scopes[-1].EnterEntity(Variable(name, off))
        elif typeof == 'par':
            off = self.scopes[-1].get_offset()
            self.scopes[-1].EnterEntity(Parameter(name, par_mode or 'CV', off))
        elif typeof == 'func':
            target_scope = self.scopes[-2] if len(self.scopes) >= 2 else self.scopes[-1]
            target_scope.EnterEntity(Function(name, None))
        elif typeof == 'temp':
            off = self.scopes[-1].get_offset()
            self.scopes[-1].EnterEntity(TempVar(name, off))

    def add_argument(self, name: str, par_mode: str) -> None:
        mode = 'CV' if par_mode == 'in' else 'REF'
        new_arg = Argument(mode)
        fname, _ = self.search_entity(name, 'func')
        if fname:
            fname.enterArg(new_arg)

    def search_entity(self, name: str, typeof: str) -> Tuple[Optional[Entity], int]:
        for scope in self.scopes:
            for entity in scope.Entities:
                if entity.name == name and entity.typeof == typeof:
                    return entity, scope.nestingLevel
        print('Error:Entity not found')
        return None, 0

    def search_entity_1(self, name: str) -> Tuple[Optional[Entity], int]:
        for i in range(len(self.scopes) - 1, -1, -1):
            for entity in self.scopes[i].Entities:
                if entity.name == name:
                    return entity, self.scopes[i].nestingLevel
        print('Error: Entity not found')
        return None, 0

    def add_fl(self, name: str, fl: int) -> None:
        if name == self.main_name:
            self.main_fl = fl
            return
        fname, _ = self.search_entity(name, 'func')
        if fname:
            fname.setFL(fl)

    def add_sq(self, name: str, quad_id: int) -> None:
        if name == self.main_name:
            self.main_sq = quad_id
            return
        fname, _ = self.search_entity(name, 'func')
        if fname:
            fname.setSQ(quad_id)

    def new_temp(self) -> str:
        t = f'T_{self.temp_num}'
        self.temp_num += 1
        self.add_entity(t, 'temp')
        return t

    def parse(self) -> List[List[Any]]:
        self.program()
        return self.ir.quads

    def program(self) -> None:
        if self.token.type == TokenType.PROGRAM:
            self.get_token()
            if self.token.type == TokenType.ID:
                self.main_name = name = self.token.value
                self.get_token()
                self.scopes.append(Scope(0))
                self.block(name)
                if self.token.type == TokenType.ENDPROGRAM:
                    print('Program ok')
                else:
                    print('ERROR: <program> The keyword endprogram was expected in line: ', self.lexer.line)
            else:
                print('ERROR: <program> Program name expected in line: ', self.lexer.line)
        else:
            print('ERROR: <program> The keyword program was expected in line: ', self.lexer.line)

    def block(self, name: str) -> None:
        c = 0
        self.declarations()
        self.subprograms()

        qid = self.ir.gen_quad('begin_block', name, ' ', ' ')
        self.add_sq(name, qid)

        self.statements()

        if name == self.main_name:
            if self.return_count != 0:
                print('ERROR: return in main program\n')
            self.ir.gen_quad('halt', ' ', ' ', ' ')
            self.add_fl(name, self.scopes[-1].offset)

        self.ir.gen_quad('end_block', name, ' ', ' ')

        for scope in self.scopes:
            for entity in scope.Entities:
                for ch in scope.Entities:
                    if entity.name == ch.name:
                        c += 1
                if c != 1:
                    print('ERROR: Not unique variable, function or procedure name \n')
                    break
                c = 0

        self.add_fl(name, self.scopes[-1].offset)

        mips = MIPSGenerator(self.scopes, self.main_name, self.main_sq, self.main_fl, self.asm_file)
        mips.generate_block_assembly(self.ir.quads, name)

        self.delete_scope()

    def declarations(self) -> None:
        if self.token.type == TokenType.DECLARE:
            self.get_token()
            self.varlist()
            if self.token.type == TokenType.ENDDECLARE:
                self.get_token()
            else:
                print('ERROR: <declarations> The keyword enddeclare was expected in line: ', self.lexer.line)

    def varlist(self) -> None:
        if self.token.type == TokenType.ID:
            self.add_entity(self.token.value, 'var')
            self.get_token()

            while self.token.type == TokenType.COMMA:
                self.get_token()
                if self.token.type == TokenType.ID:
                    self.add_entity(self.token.value, 'var')
                    self.get_token()
                else:
                    print('ERROR: <varlist>  ID expected in line:', self.lexer.line)

    def subprograms(self) -> None:
        while self.token.type in (TokenType.PROCEDURE, TokenType.FUNCTION):
            self.procorfunc()

    def procorfunc(self) -> None:
        if self.token.type == TokenType.PROCEDURE:
            self.get_token()
            if self.token.type == TokenType.ID:
                name = self.token.value
                self.list_dec.append(name)
                self.add_entity(name, 'func')
                self.add_new_scope()
                self.get_token()
                self.procorfuncbody(name)
                if self.token.type == TokenType.ENDPROCEDURE:
                    self.get_token()
                    if self.return_count != 0:
                        print('ERROR: Return in procedure')
                    self.return_count = 0
                else:
                    print('ERROR: <procorfunc> The keyword endprocedure was expected in line: ', self.lexer.line)
            else:
                print('ERROR: <procorfunc> Procedure name expected in line: ', self.lexer.line)

        elif self.token.type == TokenType.FUNCTION:
            self.get_token()
            if self.token.type == TokenType.ID:
                name = self.token.value
                self.list_dec.append(name)
                self.add_entity(name, 'func')
                self.add_new_scope()
                self.get_token()
                self.procorfuncbody(name)
                if self.token.type == TokenType.ENDFUNCTION:
                    self.get_token()
                    if self.return_count == 0:
                        print('ERROR: Not return in function')
                    self.return_count = 0
                else:
                    print('ERROR: <procorfunc> The keyword endfunction was expected in line: ', self.lexer.line)
            else:
                print('ERROR: <procorfunc> Function name expected in line: ', self.lexer.line)

    def procorfuncbody(self, name: str) -> None:
        self.formalpars(name)
        self.block(name)

    def formalpars(self, fname: str) -> None:
        if self.token.type == TokenType.OPEN_PAREN:
            self.get_token()
            if self.token.type in (TokenType.IN, TokenType.INOUT):
                self.formalparlist(fname)
                if self.token.type == TokenType.CLOSE_PAREN:
                    self.all_fd.append(self.list_dec)
                    self.list_dec = []
                    self.get_token()
                else:
                    print('ERROR: <formalpars> The symbol ) was expected in line: ', self.lexer.line)
            else:
                print('ERROR: <formalpars> The keywords in/inout were expected in line: ', self.lexer.line)
        else:
            print('ERROR: <formalpars> The symbol ( was expected in line: ', self.lexer.line)

    def formalparlist(self, fname: str) -> None:
        self.formalparitem(fname)
        while self.token.type == TokenType.COMMA:
            self.get_token()
            self.formalparitem(fname)

    def formalparitem(self, fname: str) -> None:
        if self.token.type in (TokenType.IN, TokenType.INOUT):
            mode_val = self.token.value
            par_mode = 'CV' if mode_val == 'in' else 'REF'
            self.list_dec.append(mode_val)
            self.get_token()
            if self.token.type == TokenType.ID:
                self.add_entity(self.token.value, 'par', par_mode)
                self.add_argument(fname, mode_val)
                self.get_token()
            else:
                print('ERROR: <formalparitems> Formalparitem id was expected in line: ', self.lexer.line)
        else:
            print('ERROR: <Formalparitem> The keywords in/inout were expected in line: ', self.lexer.line)

    def statements(self) -> List[int]:
        t = self.statement()
        while self.token.type == TokenType.SEMICOLON:
            self.get_token()
            _ = self.statement()
        return t or []

    def statement(self) -> List[int]:
        if self.token.type == TokenType.ID:
            self.assigment_stat()
            return []
        elif self.token.type == TokenType.IF:
            return self.if_stat()
        elif self.token.type == TokenType.WHILE:
            return self.while_stat()
        elif self.token.type == TokenType.REPEAT:
            self.repeat_stat()
            return []
        elif self.token.type == TokenType.EXIT:
            return self.exit_stat()
        elif self.token.type == TokenType.SWITCH:
            return self.switch_stat()
        elif self.token.type == TokenType.FORCASE:
            return self.forcase_stat()
        elif self.token.type == TokenType.CALL:
            self.call_stat()
            return []
        elif self.token.type == TokenType.RETURN:
            self.return_stat()
            return []
        elif self.token.type == TokenType.INPUT:
            self.input_stat()
            return []
        elif self.token.type == TokenType.PRINT:
            self.print_stat()
            return []
        return []

    def assigment_stat(self) -> None:
        if self.token.type == TokenType.ID:
            t = self.token.value
            self.get_token()
            if self.token.type == TokenType.ASSIGN:
                k = self.token.value
                self.get_token()
                eplace = self.expression()
                self.ir.gen_quad(k, eplace, '', t)
            else:
                print('ERROR: <assigmen_stat> The symbol := was expected in line: ', self.lexer.line)
        else:
            print('ERROR: <assigmen_stat> ID expected in line: ', self.lexer.line)

    def if_stat(self) -> List[int]:
        exit_list: List[int] = []
        if self.token.type == TokenType.IF:
            self.get_token()
            cond_true, cond_false = self.condition()
            if self.token.type == TokenType.THEN:
                self.ir.backpatch(cond_true, self.ir.next_quad())
                self.get_token()
                t1 = self.statements()
                if_list = self.ir.make_list(self.ir.next_quad())
                self.ir.gen_quad('jump', '', '', '')
                self.ir.backpatch(cond_false, self.ir.next_quad())
                t2 = self.else_part()
                exit_list = self.ir.merge_list(t1, t2)
                self.ir.backpatch(if_list, self.ir.next_quad())
                if self.token.type == TokenType.ENDIF:
                    self.get_token()
                else:
                    print('ERROR: <if_stat> The keyword else was expected in line: ', self.lexer.line)
            else:
                print('ERROR: <if_stat> The keyword then was expected in line: ', self.lexer.line)
        else:
            print('ERROR: <if_stat> The keyword if was expected in line: ', self.lexer.line)

        return exit_list

    def else_part(self) -> List[int]:
        t: List[int] = []
        if self.token.type == TokenType.ELSE:
            self.get_token()
            t = self.statements()
        return t

    def repeat_stat(self) -> None:
        exit_list: List[int] = []
        if self.token.type == TokenType.REPEAT:
            self.repeat_count += 1
            self.get_token()
            s_quad = self.ir.next_quad()
            t = self.statements()
            self.ir.gen_quad('jump', '', '', s_quad)
            exit_list = self.ir.merge_list(exit_list, t)
            if self.token.type == TokenType.ENDREPEAT:
                self.repeat_count -= 1
                self.ir.backpatch(exit_list, self.ir.next_quad())
                self.get_token()
            else:
                print('ERROR: <repeat_stat> The keyword endrepeat was expected in line: ', self.lexer.line)
        else:
            print('ERROR: <repeat_stat> The keyword repeat was expected in line: ', self.lexer.line)

    def exit_stat(self) -> List[int]:
        t: List[int] = []
        if self.token.type == TokenType.EXIT:
            if self.repeat_count == 0:
                print('ERROR: exit statement outside repeat loop in line: ', self.lexer.line)
            t = self.ir.make_list(self.ir.next_quad())
            self.ir.gen_quad('jump', '', '', '')
            self.get_token()
        else:
            print('ERROR: <exit_stat> The keyword exit was expected in line: ', self.lexer.line)
        return t

    def while_stat(self) -> List[int]:
        exit_list: List[int] = []
        if self.token.type == TokenType.WHILE:
            self.get_token()
            wc = self.ir.next_quad()
            cond_true, cond_false = self.condition()
            self.ir.backpatch(cond_true, self.ir.next_quad())
            exit_list = self.statements()
            self.ir.gen_quad('jump', '', '', wc)
            self.ir.backpatch(cond_false, self.ir.next_quad())
            if self.token.type == TokenType.ENDWHILE:
                self.get_token()
            else:
                print('ERROR: <while_stat> The keyword endwhile was expected in line: ', self.lexer.line)
        else:
            print('ERROR: <whilet_stat> The keyword while was expected in line: ', self.lexer.line)

        return exit_list

    def switch_stat(self) -> List[int]:
        exit_repeat: List[int] = []
        if self.token.type == TokenType.SWITCH:
            self.get_token()
            eplace = self.expression()
            if self.token.type == TokenType.CASE:
                self.get_token()
                eplace1 = self.expression()
                false_case = self.ir.make_list(self.ir.next_quad())
                self.ir.gen_quad('<>', eplace, eplace1, '')
                true_case = self.ir.make_list(self.ir.next_quad())
                self.ir.gen_quad('=', eplace, eplace1, '')
                if self.token.type == TokenType.COLON:
                    self.get_token()
                    self.ir.backpatch(true_case, self.ir.next_quad())
                    t1 = self.statements()
                    exit_list = self.ir.make_list(self.ir.next_quad())
                    self.ir.gen_quad('jump', '', '', '')
                    self.ir.backpatch(false_case, self.ir.next_quad())
                    while self.token.type == TokenType.CASE:
                        self.get_token()
                        eplace2 = self.expression()
                        false_case1 = self.ir.make_list(self.ir.next_quad())
                        self.ir.gen_quad('<>', eplace, eplace2, '')
                        true_case1 = self.ir.make_list(self.ir.next_quad())
                        self.ir.gen_quad('=', eplace, eplace2, '')
                        if self.token.type == TokenType.COLON:
                            self.get_token()
                            self.ir.backpatch(true_case1, self.ir.next_quad())
                            t2 = self.statements()
                            exit_repeat = self.ir.merge_list(t1, t2)
                            exit_list1 = self.ir.make_list(self.ir.next_quad())
                            self.ir.gen_quad('jump', '', '', '')
                            exit_list = self.ir.merge_list(exit_list, exit_list1)
                            self.ir.backpatch(false_case1, self.ir.next_quad())

                    if self.token.type == TokenType.ENDSWITCH:
                        self.ir.backpatch(exit_list, self.ir.next_quad())
                        self.get_token()
                    else:
                        print('ERROR: <switch_stat> The keyword endswitch was expected in line: ', self.lexer.line)
                else:
                    print('ERROR: <switch_stat> The Symbol : was expected in line: ', self.lexer.line)
            else:
                print('ERROR: <switch_stat> The keyword case was expected in line: ', self.lexer.line)
        else:
            print('ERROR: <switch_stat> The keyword switch was expected in line: ', self.lexer.line)

        return exit_repeat

    def forcase_stat(self) -> List[int]:
        exit_list: List[int] = []
        if self.token.type == TokenType.FORCASE:
            self.get_token()
            fc = self.ir.next_quad()
            if self.token.type == TokenType.WHEN:
                self.get_token()
                cond_true, cond_false = self.condition()
                if self.token.type == TokenType.COLON:
                    self.get_token()
                    self.ir.backpatch(cond_true, self.ir.next_quad())
                    t1 = self.statements()
                    self.ir.gen_quad('jump', '', '', fc)
                    self.ir.backpatch(cond_false, self.ir.next_quad())
                    while self.token.type == TokenType.WHEN:
                        self.get_token()
                        cond_true, cond_false = self.condition()
                        if self.token.type == TokenType.COLON:
                            self.get_token()
                            self.ir.backpatch(cond_true, self.ir.next_quad())
                            t2 = self.statements()
                            exit_list = self.ir.merge_list(t1, t2)
                            self.ir.gen_quad('jump', '', '', fc)
                            self.ir.backpatch(cond_false, self.lexer.line)

                    if self.token.type == TokenType.ENDFORCASE:
                        self.get_token()
                    else:
                        print('ERROR: <forcase_stat> The keyword endforcase was expected in line: ', self.lexer.line)
                else:
                    print('ERROR: <forcase_stat> The Symbol : was expected in line: ', self.lexer.line)
            else:
                print('ERROR: <forcase_stat> The keyword when was expected in line: ', self.lexer.line)
        else:
            print('ERROR: <forcase_stat> The keyword forcase was expected in line: ', self.lexer.line)

        return exit_list

    def call_stat(self) -> None:
        if self.token.type == TokenType.CALL:
            self.get_token()
            if self.token.type == TokenType.ID:
                x = self.token.value
                self.list_call.append(x)
                self.get_token()
                self.actualpars()
                if self.list_call not in self.all_fd:
                    print('ERROR: function or procedure not defined')
                self.ir.gen_quad('call', x, '', '')
                self.list_call = []
            else:
                print('ERROR: <call_stat> ID was expected in line: ', self.lexer.line)
        else:
            print('ERROR: <call_stat> The keyword call was expected in line: ', self.lexer.line)

    def return_stat(self) -> None:
        if self.token.type == TokenType.RETURN:
            self.get_token()
            self.return_count += 1
            eplace = self.expression()
            self.ir.gen_quad('RET', '', '', eplace)
        else:
            print('ERROR: <return_stat> The keyword return was expected in line: ', self.lexer.line)

    def print_stat(self) -> None:
        if self.token.type == TokenType.PRINT:
            self.get_token()
            eplace = self.expression()
            self.ir.gen_quad('out', eplace, '', '')
        else:
            print('ERROR: <print_stat> The keyword print was expected in line: ', self.lexer.line)

    def input_stat(self) -> None:
        if self.token.type == TokenType.INPUT:
            self.get_token()
            if self.token.type == TokenType.ID:
                x = self.token.value
                self.get_token()
                self.ir.gen_quad('inp', x, '', '')
            else:
                print('ERROR: <input_stat> ID was expected in line: ', self.lexer.line)
        else:
            print('ERROR: <input_stat> The keyword input was expected in line: ', self.lexer.line)

    def actualpars(self) -> None:
        if self.token.type == TokenType.OPEN_PAREN:
            self.get_token()
            self.actualparlist()
            if self.token.type == TokenType.CLOSE_PAREN:
                self.get_token()
            else:
                print('ERROR: <actualpars> The Symbol ) was expected in line: ', self.lexer.line)
        else:
            print('ERROR: <actualpars> The Symbol ) was expected in line: ', self.lexer.line)

    def actualparlist(self) -> None:
        self.actualparitem()
        while self.token.type == TokenType.COMMA:
            self.get_token()
            self.actualparitem()

    def actualparitem(self) -> None:
        if self.token.type == TokenType.IN:
            self.list_call.append(self.token.value)
            self.get_token()
            x = self.expression()
            self.ir.gen_quad('par', x, 'CV', '')
        elif self.token.type == TokenType.INOUT:
            self.list_call.append(self.token.value)
            self.get_token()
            if self.token.type == TokenType.ID:
                self.ir.gen_quad('par', self.token.value, 'REF', '')
                self.get_token()
            else:
                print('ERROR: <actualparitem> ID was expected in line: ', self.lexer.line)
        else:
            print('ERROR: <actualparitem> The keywords in/out were expected in line: ', self.lexer.line)

    def condition(self) -> Tuple[List[int], List[int]]:
        cond_true1, cond_false1 = self.boolterm()
        while self.token.type == TokenType.OR:
            self.ir.backpatch(cond_false1, self.ir.next_quad())
            self.get_token()
            cond_true2, cond_false2 = self.boolterm()
            cond_true1 = self.ir.merge_list(cond_true1, cond_true2)
            cond_false1 = cond_false2

        return cond_true1, cond_false1

    def boolterm(self) -> Tuple[List[int], List[int]]:
        btrue1, bfalse1 = self.boolfactor()
        while self.token.type == TokenType.AND:
            self.ir.backpatch(btrue1, self.ir.next_quad())
            self.get_token()
            btrue2, bfalse2 = self.boolfactor()
            bfalse1 = self.ir.merge_list(bfalse1, bfalse2)
            btrue1 = btrue2

        return btrue1, bfalse1

    def boolfactor(self) -> Tuple[List[int], List[int]]:
        r_true: List[int] = []
        r_false: List[int] = []

        if self.token.type == TokenType.NOT:
            self.get_token()
            if self.token.type == TokenType.OPEN_BRACKET:
                self.get_token()
                r_true, r_false = self.condition()
                if self.token.type == TokenType.CLOSE_BRACKET:
                    self.get_token()
                else:
                    print('ERROR: <boolfactor> The Symbol ] was expected in line: ', self.lexer.line)
            else:
                print('ERROR: <boolfactor> The Symbol [ was expected in line: ', self.lexer.line)

        elif self.token.type == TokenType.OPEN_BRACKET:
            self.get_token()
            r_true, r_false = self.condition()
            if self.token.type == TokenType.CLOSE_BRACKET:
                self.get_token()
            else:
                print('ERROR: <boolfactor> The Symbol ] was expected in line: ', self.lexer.line)

        elif self.token.type == TokenType.TRUE:
            self.get_token()

        elif self.token.type == TokenType.FALSE:
            self.get_token()

        else:
            eplace1 = self.expression()
            relop = self.relational_oper()
            eplace2 = self.expression()
            r_true = self.ir.make_list(self.ir.next_quad())
            self.ir.gen_quad(relop, eplace1, eplace2, '')
            r_false = self.ir.make_list(self.ir.next_quad())
            self.ir.gen_quad('jump', '', '', '')

        return r_true, r_false

    def expression(self) -> Any:
        self.optional_sign()
        tplace1 = self.term()
        while self.token.type in (TokenType.PLUS, TokenType.MINUS):
            operation = self.add_oper()
            tplace2 = self.term()
            w = self.new_temp()
            self.ir.gen_quad(operation, tplace1, tplace2, w)
            tplace1 = w

        return tplace1

    def term(self) -> Any:
        fplace1 = self.factor()
        while self.token.type in (TokenType.MUL, TokenType.DIV):
            operation = self.mul_oper()
            fplace2 = self.factor()
            w = self.new_temp()
            self.ir.gen_quad(operation, fplace1, fplace2, w)
            fplace1 = w
        return fplace1

    def factor(self) -> Any:
        fplace: Any = ''
        if self.token.type == TokenType.OPEN_PAREN:
            self.get_token()
            fplace = self.expression()
            if self.token.type == TokenType.CLOSE_PAREN:
                self.get_token()
            else:
                print('ERROR: <factor> The Symbol ) was expected in line: ', self.lexer.line)

        elif self.token.type == TokenType.ID:
            fplace = self.token.value
            self.get_token()
            w = self.idtail(fplace)
            if w != '':
                self.ir.gen_quad('call', fplace, '', '')
                if self.list_call not in self.all_fd:
                    print('ERROR: Function or procedure not exits\n')
                self.list_call = []
                return w

        elif self.token.type == TokenType.CONST:
            fplace = self.token.value
            self.get_token()

        else:
            print('ERROR: <factor> Not ID or Conts or ( founded in line: ', self.lexer.line)

        return fplace

    def idtail(self, fplace: str) -> str:
        w = ''
        if self.token.type == TokenType.OPEN_PAREN:
            self.list_call.append(fplace)
            self.actualpars()
            w = self.new_temp()
            self.ir.gen_quad('par', w, 'RET', '')
        return w

    def relational_oper(self) -> str:
        relop = self.token.value
        if self.token.type in (
            TokenType.EQUAL, TokenType.LESSEQUAL, TokenType.GREATEREQUAL,
            TokenType.GREATER, TokenType.LESS, TokenType.NOTEQUAL
        ):
            self.get_token()
        else:
            print('ERROR: <relation_oper> == >= <= > < <> expected in line: ', self.lexer.line)
        return relop

    def add_oper(self) -> str:
        op = self.token.value
        if self.token.type in (TokenType.PLUS, TokenType.MINUS):
            self.get_token()
        else:
            print('ERROR: <add_oper> + or - expected in line: ', self.lexer.line)
        return op

    def mul_oper(self) -> str:
        op = self.token.value
        if self.token.type in (TokenType.MUL, TokenType.DIV):
            self.get_token()
        else:
            print('ERROR: <mul_oper> * or / expected in line: ', self.lexer.line)
        return op

    def optional_sign(self) -> None:
        if self.token.type in (TokenType.PLUS, TokenType.MINUS):
            self.add_oper()
