from dataclasses import dataclass
from enum import Enum
from typing import Set


class TokenType(str, Enum):
    # Keywords
    PROGRAM = "programtk"
    ENDPROGRAM = "endprogramtk"
    DECLARE = "declaretk"
    ENDDECLARE = "enddeclaretk"
    IF = "iftk"
    THEN = "thentk"
    ELSE = "elsetk"
    ENDIF = "endiftk"
    WHILE = "whiletk"
    ENDWHILE = "endwhiletk"
    REPEAT = "repeattk"
    ENDREPEAT = "endrepeattk"
    EXIT = "exittk"
    SWITCH = "switchtk"
    CASE = "casetk"
    ENDSWITCH = "endswitchtk"
    FORCASE = "forcasetk"
    WHEN = "whentk"
    ENDFORCASE = "endforcasetk"
    PROCEDURE = "proceduretk"
    ENDPROCEDURE = "endproceduretk"
    FUNCTION = "functiontk"
    ENDFUNCTION = "endfunctiontk"
    CALL = "calltk"
    RETURN = "returntk"
    IN = "intk"
    INOUT = "inouttk"
    AND = "andtk"
    OR = "ortk"
    NOT = "nottk"
    TRUE = "truetk"
    FALSE = "falsetk"
    INPUT = "inputtk"
    PRINT = "printtk"

    # Literals and Identifiers
    ID = "idtk"
    CONST = "consttk"

    # Operators & Punctuation
    PLUS = "plustk"
    MINUS = "minustk"
    MUL = "mulstk"
    DIV = "divtk"
    EQUAL = "equalstk"
    NOTEQUAL = "notequalstk"
    LESS = "mintk"
    GREATER = "maxtk"
    LESSEQUAL = "minequalstk"
    GREATEREQUAL = "maxequalstk"
    ASSIGN = "assigmenttk"
    COLON = "doubledottk"
    COMMA = "commatk"
    SEMICOLON = "questiontk"
    OPEN_PAREN = "openbtk"
    CLOSE_PAREN = "closebtk"
    OPEN_BRACKET = "openptk"
    CLOSE_BRACKET = "closeptk"

    # Special
    EOF = "eoftk"
    COMMENT_LINE = "commenttk"
    COMMENT_OPEN = "commentotk"
    COMMENT_CLOSE = "commentctk"


KEYWORDS: Set[str] = {
    "program", "endprogram", "declare", "enddeclare", "if", "then", "else", "endif",
    "while", "endwhile", "repeat", "endrepeat", "exit", "switch", "case", "endswitch",
    "forcase", "when", "endforcase", "procedure", "endprocedure", "function",
    "endfunction", "call", "return", "in", "inout", "and", "or", "not", "true",
    "false", "input", "print"
}


@dataclass
class Token:
    value: str
    type: TokenType
    line: int = 1

    def __iter__(self):
        # Compatibility tuple unpack [token_val, token_type]
        yield self.value
        yield self.type.value
