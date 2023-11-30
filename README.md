# EEL-Compiler

EEL (Early Experimental Language) is a small programming language. It supports functions and procedures, parameter passing by reference and value, recursive calls, and other structures. It also allows nesting in the declaration of functions and procedures. However, it does not support basic programming tools such as the "for" structure or data types like real numbers and strings.

# The alphabet of EEL 

* Unordered sub-list. lowercase and uppercase letters of the Latin alphabet ("A" to "Z" and "a" to "z"),
* numerical digits ("0" to "9"),
* symbols of arithmetic operations ("+", "-", "*", "/"),
* relational operators "<", ">", "=", "<=", ">=", "<>",
* assignment symbol ":=",
* delimiters (";", ",", ":"),
* grouping symbols ("(", ")", "[", "]"),
* and comment delimiters ("*", "*", \).
The symbols "[" and "]" are used in logical expressions, similar to "(" and ")" in arithmetic expressions.

Certain words are reserved:

program, endprogram
declare, enddeclare
if, then, else, endif
while, endwhile
repeat, endrepeat, exit
switch, case, endswitch
forcase, when, endforcase
procedure, endprocedure, function, endfunction, call, return, in, inout
and, or, not, true, false
input, print
These words cannot be used as variables. Constants in the language are integer constants consisting of an optional sign and a sequence of numeric digits. The constants true and false are also supported.

Identifiers in the language are strings consisting of letters and digits, starting with a letter. The compiler only considers the first thirty letters. White characters (tab, space, return) are ignored and can be used freely, as long as they are not within reserved words, identifiers, constants, or comments. The same applies to comments, which must be within the symbols "/" and "/" or after "//" until the end of the line.

The only supported data type in EEL is integer numbers, ranging from -32767 to 32767. Declaration is done using the declare command, followed by the names of identifiers without any other declaration since they are known to be integer variables. Variables are separated by commas, and the end of the variable declaration is marked by the enddeclare command.

The operator precedence from highest to lowest is:

1. Unary logical "not", <br />
2. Multiplicative "*", "/", <br />
3. Unary additive "+", "-", <br />
4. Binary additive "+", "-", <br />
5. Relational "=", "<", ">", "<>", "<=", ">=", <br />
6. Logical "and", <br />
7. Logical "or", <br />

EEL supports two parameter passing methods:

* Pass by value, declared with the keyword "in." Changes to its value do not reflect back to the calling program.
* Pass by reference, declared with the keyword "inout." Any change in its value is transferred back to the calling program.

In a function or procedure call, actual parameters are written after the keywords "in" and "inout," depending on whether they are passed by value or reference, respectively.
