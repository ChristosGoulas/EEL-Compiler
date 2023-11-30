from typing import List, Optional
from .errors import LexerError
from .tokens import KEYWORDS, Token, TokenType


class Lexer:
    """Character-state machine tokenizer for the EEL programming language."""

    def __init__(self, source_code: str) -> None:
        self.source_code: str = source_code
        self.position: int = 0
        self.line: int = 1
        self.state: int = 0

    def get_next_token(self) -> Token:
        token_val: str = ""
        token_type_str: str = ""

        if self.position >= len(self.source_code):
            return Token("eof", TokenType.EOF, self.line)

        while self.position < len(self.source_code):
            ch = self.source_code[self.position]

            if ch == '+' and self.state == 0:
                self.position += 1
                return Token('+', TokenType.PLUS, self.line)

            elif (ch == '\t' or ch.isspace()) and self.state == 0:
                if ch == '\n':
                    self.line += 1
                self.position += 1

            elif ch == '-' and self.state == 0:
                self.position += 1
                return Token('-', TokenType.MINUS, self.line)

            elif ch == '*' and self.state == 0:
                self.position += 1
                return Token('*', TokenType.MUL, self.line)

            elif ch == '/' and self.state == 0:
                self.state = 6
                self.position += 1
                if self.position < len(self.source_code) and self.source_code[self.position] == '/':
                    self.position += 1
                    # consume single line comment
                    while self.position < len(self.source_code) and self.source_code[self.position] != '\n':
                        self.position += 1
                    self.state = 0
                elif self.position < len(self.source_code) and self.source_code[self.position] == '*':
                    self.state = 7
                    self.position += 1
                else:
                    self.state = 0
                    return Token('/', TokenType.DIV, self.line)

            elif self.state == 6:
                if ch == '\n':
                    self.line += 1
                    self.state = 0
                self.position += 1

            elif self.state == 7:
                if ch == '*' and self.position + 1 < len(self.source_code) and self.source_code[self.position + 1] == '/':
                    self.position += 2
                    self.state = 0
                else:
                    if ch == '\n':
                        self.line += 1
                    self.position += 1
                    if self.position >= len(self.source_code):
                        print(f"ERROR: comments did not close in line: {self.line}")
                        break

            elif ch == '=' and self.state == 0:
                self.position += 1
                return Token('=', TokenType.EQUAL, self.line)

            elif ch == '(' and self.state == 0:
                self.position += 1
                return Token('(', TokenType.OPEN_PAREN, self.line)

            elif ch == ')' and self.state == 0:
                self.position += 1
                return Token(')', TokenType.CLOSE_PAREN, self.line)

            elif ch == '[' and self.state == 0:
                self.position += 1
                return Token('', TokenType.OPEN_BRACKET, self.line)

            elif ch == ']' and self.state == 0:
                self.position += 1
                return Token(']', TokenType.CLOSE_BRACKET, self.line)

            elif ch == ',' and self.state == 0:
                self.position += 1
                return Token(',', TokenType.COMMA, self.line)

            elif ch == ';' and self.state == 0:
                self.position += 1
                return Token(';', TokenType.SEMICOLON, self.line)

            elif ch == '<' and self.state == 0:
                self.position += 1
                self.state = 3
                if self.position < len(self.source_code) and self.source_code[self.position] == '>':
                    self.position += 1
                    self.state = 0
                    return Token('<>', TokenType.NOTEQUAL, self.line)
                elif self.position < len(self.source_code) and self.source_code[self.position] == '=':
                    self.position += 1
                    self.state = 0
                    return Token('<=', TokenType.LESSEQUAL, self.line)
                else:
                    self.state = 0
                    return Token('<', TokenType.LESS, self.line)

            elif ch == '>' and self.state == 0:
                self.position += 1
                self.state = 4
                if self.position < len(self.source_code) and self.source_code[self.position] == '=':
                    self.position += 1
                    self.state = 0
                    return Token('>=', TokenType.GREATEREQUAL, self.line)
                else:
                    self.state = 0
                    return Token('>', TokenType.GREATER, self.line)

            elif ch == ':' and self.state == 0:
                self.position += 1
                self.state = 5
                if self.position < len(self.source_code) and self.source_code[self.position] == '=':
                    self.position += 1
                    self.state = 0
                    return Token(':=', TokenType.ASSIGN, self.line)
                else:
                    self.state = 0
                    return Token(':', TokenType.COLON, self.line)

            elif ch.isalpha() and self.state == 0:
                self.state = 1
                token_val = ch
                self.position += 1

            elif (ch.isalpha() or ch.isdigit()) and self.state == 1:
                token_val += ch
                self.position += 1

            elif (not (ch.isalpha() or ch.isdigit())) and self.state == 1:
                self.state = 0
                if token_val in KEYWORDS:
                    token_type_str = token_val + 'tk'
                else:
                    token_type_str = 'idtk'
                return Token(token_val, TokenType(token_type_str), self.line)

            elif ch.isdigit() and self.state == 0:
                self.state = 2
                token_val = ch
                self.position += 1

            elif ch.isdigit() and self.state == 2:
                token_val += ch
                self.position += 1

            elif ch.isalpha() and self.state == 2:
                raise LexerError("Invalid number", line=self.line, source_line=self._get_source_line(self.line))

            elif not (ch.isdigit() and self.state == 2):
                if int(token_val) > 32767 or int(token_val) < -32767:
                    raise LexerError("Number out of bounds", line=self.line, source_line=self._get_source_line(self.line))
                self.state = 0
                return Token(token_val, TokenType.CONST, self.line)

            else:
                raise LexerError("Character does not belong to language", line=self.line, source_line=self._get_source_line(self.line))

        # Handle trailing token if stream ends while in identifier state
        if self.state == 1:
            self.state = 0
            token_type_str = (token_val + 'tk') if token_val in KEYWORDS else 'idtk'
            return Token(token_val, TokenType(token_type_str), self.line)
        elif self.state == 2:
            self.state = 0
            if int(token_val) > 32767 or int(token_val) < -32767:
                raise LexerError("Number out of bounds", line=self.line, source_line=self._get_source_line(self.line))
            return Token(token_val, TokenType.CONST, self.line)

        return Token("eof", TokenType.EOF, self.line)

    def _get_source_line(self, target_line: int) -> Optional[str]:
        lines = self.source_code.splitlines()
        if 1 <= target_line <= len(lines):
            return lines[target_line - 1]
        return None
