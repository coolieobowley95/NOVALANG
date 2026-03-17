<<<<<<< HEAD
# Group Members: 
# Member 1:
    Name: Tashana Henry 
    ID: 1804274
    Email: Henrytashana09@gmail.com
# Member 2:
    Name: Orine Stephenson, 
    ID: 2005009
    Email: orinestephenson4@gmail.com
# Member 3:
    Name: Coolieo Bowley 
    ID: 2003923 
    Email: coolieobowley95@gmail.com
# Member 4:
    Name: Jonathan Masters
    ID#: 2100098
    Email: jonathanmasters2018@gmail.com

# NOVALANG Mini Programming Language

## Overview

NOVALANG is a mini programming language designed and implemented as part of a programming languages project. The language demonstrates the fundamental phases of language processing including lexical analysis, syntax analysis, semantic analysis, and interpretation.

NOVALANG is implemented using Python and PLY (Python Lex-Yacc). It provides a simple and readable syntax for demonstrating core programming language concepts such as variables, arithmetic expressions, control structures, and exception handling.

---

## Programming Paradigm

NOVALANG primarily follows the **Imperative Programming Paradigm**.

In the imperative paradigm, programs are written as sequences of instructions that change the program state step-by-step.

Example:

```
let A = 10
let B = 20
let C = A + B
display C
```

The program executes each statement in order and modifies variables during execution.

---

## Language Type

NOVALANG is a:

- **General Purpose Programming Language**
- **High Level Programming Language**

It abstracts hardware details and focuses on readability and simplicity.

---

## Language Features

NOVALANG supports the following features:

- Variables
- Arithmetic operations
- Operator precedence
- Conditional statements
- Loops
- Exception handling
- Output statements
- String literals

---

## Example Program

```
let A = 20
let B = 40
let C = A + B * B

try
    let D = C / 0
catch
    display "Error: Division by zero attempted but not allowed."
end

display "The result is"
display C
```

Output:

```
Error: Division by zero attempted but not allowed.
The result is
1620
```

---

## Syntax Design

Unlike languages such as C or Java that use `{}` to define blocks, NOVALANG uses keyword-based blocks.

Example:

```
if x > 5
    display "greater"
end
```

This design improves readability and reduces syntax complexity.

---

## Tokens in NOVALANG

The language lexer identifies the following tokens:

```
LET
DISPLAY
IF
WHILE
TRY
CATCH
END
IDENTIFIER
NUMBER
STRING
PLUS
MINUS
TIMES
DIVIDE
EQUALS
LPAREN
RPAREN
```

---

## Lexical Rules (Regular Expressions)

Identifier

```
[a-zA-Z_][a-zA-Z0-9_]*
```

Number

```
\d+(\.\d+)?
```

String

```
"(?:\\.|[^"\\])*"
```

Arithmetic Operators

```
+   -   *   /
```

---

## Grammar Overview (EBNF)

```
program ::= statement*

statement ::= let_statement
            | display_statement
            | try_statement

let_statement ::= "let" IDENTIFIER "=" expression

display_statement ::= "display" expression

try_statement ::= "try" statement* "catch" statement* "end"

expression ::= term (("+" | "-") term)*

term ::= factor (("*" | "/") factor)*

factor ::= NUMBER
         | IDENTIFIER
         | "(" expression ")"
```

---

## Interpreter Architecture

NOVALANG follows the standard language processing pipeline:

```
Source Code
     |
     v
Lexical Analyzer (lexer.py)
     |
     v
Parser (parser.py)
     |
     v
Abstract Syntax Tree
     |
     v
Interpreter (interpreter.py)
     |
     v
Program Execution
```

---

## Error Handling

NOVALANG includes exception handling using `try` and `catch`.

Example:

```
try
    let X = 5 / 0
catch
    display "division error"
end
```

This prevents the program from crashing and allows safe execution.

---

## Running the Language

Run a NOVALANG program using:

```
python main.py test.nl
```

Example:

```
python main.py test.nl
```

---

## Interactive Mode

You can also run the interpreter interactively:

```
python main.py
```

Example:

```
NOVALANG> let x = 10
NOVALANG> display x
```

Output:

```
10
```

---

## Technologies Used

NOVALANG was implemented using:

- Python
- PLY (Python Lex-Yacc)

These tools were used to implement lexical analysis and parsing functionality.

---

## Project Structure

```
NOVALANG/
│
├── lexer.py
├── parser.py
├── interpreter.py
├── main.py
├── test.nl
└── README.md
```

---

## Educational Purpose

The goal of this project is to demonstrate how programming languages are implemented, including:

- lexical analysis
- syntax parsing
- semantic evaluation
- interpreter execution

NOVALANG provides a simplified environment for studying programming language design and implementation.

---
=======
# NOVALANG
NOVALANG is a mini programming language designed for educational purposes to demonstrate compiler and interpreter concepts, including lexical analysis, syntax parsing, semantic analysis, and execution. It supports both explicit and implicit variable declaration, arithmetic operations, operator precedence, exception handling, and basic I/O.
>>>>>>> 9084398de947016940539bb48f0fd56b13440780
