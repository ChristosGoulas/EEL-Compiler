from typing import Optional


class EELError(Exception):
    """Base exception class for EEL Compiler errors with rich source context."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        source_line: Optional[str] = None
    ) -> None:
        self.message = message
        self.line = line
        self.column = column
        self.source_line = source_line

        formatted = self._format_error()
        super().__init__(formatted)

    def _format_error(self) -> str:
        parts = []
        if self.line is not None:
            location = f"line {self.line}"
            if self.column is not None:
                location += f", col {self.column}"
            parts.append(f"Error ({location}): {self.message}")
        else:
            parts.append(f"Error: {self.message}")

        if self.source_line is not None:
            trimmed = self.source_line.rstrip()
            parts.append(f"    {trimmed}")
            if self.column is not None and self.column > 0:
                caret_offset = " " * (4 + self.column - 1) + "^"
                parts.append(caret_offset)

        return "\n".join(parts)


class LexerError(EELError):
    """Raised when the tokenizer encounters invalid syntax or out-of-bound constants."""
    pass


class SyntaxError(EELError):
    """Raised when the parser encounters a grammatical violation."""
    pass


class SemanticError(EELError):
    """Raised when static semantic checks fail (e.g. undeclared identifier, scope mismatch)."""
    pass
