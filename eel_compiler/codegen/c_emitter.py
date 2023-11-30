from typing import List, TextIO, Any


class CEmitter:
    """Generates ANSI C debug representation from intermediate quadruples."""

    @staticmethod
    def generate(quads: List[List[Any]], out_file: TextIO) -> None:
        var_list: List[str] = []

        for x in quads:
            op = x[1]
            for operand in (x[2], x[3], x[4]):
                if isinstance(operand, str):
                    s = str(operand).strip()
                    if s and not s.isdigit() and (s[0].isalpha() or s[0] == '_') and all(c.isalnum() or c == '_' for c in s):
                        if s not in ('CV', 'REF', 'RET') and op not in ('call', 'begin_block', 'end_block') and s not in var_list:
                            var_list.append(s)

        out_file.write('#include <stdio.h>\n\n')
        out_file.write('int main()\n{\n')

        if var_list:
            out_file.write('  int ' + ', '.join(var_list) + ';\n\n')

        out_file.write('  L_0: ;\n')

        for x in quads:
            qid, op, arg1, arg2, target = x[0], x[1], str(x[2]), str(x[3]), str(x[4])

            if op == 'jump':
                out_file.write(f'  L_{qid}: goto L_{target}; // ({op}, {arg1}, {arg2}, {target})\n')
            elif op in ('+', '-', '*', '/'):
                out_file.write(f'  L_{qid}: {target} = {arg1} {op} {arg2}; // ({op}, {arg1}, {arg2}, {target})\n')
            elif op == ':=':
                out_file.write(f'  L_{qid}: {target} = {arg1}; // ({op}, {arg1}, {arg2}, {target})\n')
            elif op == '=':
                out_file.write(f'  L_{qid}: if ({arg1} == {arg2}) goto L_{target}; // ({op}, {arg1}, {arg2}, {target})\n')
            elif op == '<>':
                out_file.write(f'  L_{qid}: if ({arg1} != {arg2}) goto L_{target}; // ({op}, {arg1}, {arg2}, {target})\n')
            elif op in ('<', '>', '<=', '>='):
                out_file.write(f'  L_{qid}: if ({arg1} {op} {arg2}) goto L_{target}; // ({op}, {arg1}, {arg2}, {target})\n')
            elif op == 'out':
                out_file.write(f'  L_{qid}: printf("%d\\n", {arg1}); // ({op}, {arg1}, {arg2}, {target})\n')
            elif op == 'inp':
                out_file.write(f'  L_{qid}: scanf("%d", &{arg1}); // ({op}, {arg1}, {arg2}, {target})\n')
            elif op == 'halt':
                out_file.write(f'  L_{qid}: ; // halt\n')
            else:
                out_file.write(f'  L_{qid}: ; // ({op}, {arg1}, {arg2}, {target})\n')

        out_file.write('}\n')
