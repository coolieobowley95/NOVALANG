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
# Member 5:
    Name: Shavon Scale
    ID#: 2008093
    Email: shavonscale@gmail.com

---

# NOVALANG Mini Programming Language

## Live Deployment & Repository

- **Live Demo:** https://novalang-4x9v.onrender.com/
- **GitHub Repository:** https://github.com/coolieobowley95/NOVALANG

> Note: The live demo is hosted on Render's free tier. If the page takes 30–60 seconds to load, the service is waking up from sleep — this is normal.

---

## Overview

NOVALANG is a general-purpose, high-level mini programming language designed and implemented as part of a programming languages project at the University of Technology, Jamaica. The language demonstrates the fundamental phases of language processing including lexical analysis, syntax analysis, semantic analysis, and interpretation.

NOVALANG is implemented using Python 3 and PLY (Python Lex-Yacc). It provides a simple and readable syntax for demonstrating core programming language concepts such as variables, arithmetic expressions, control structures, exception handling, functions, classes, and lambda expressions.

The project includes:
- A deterministic interpreter (lexer.py, parser.py, interpreter.py)
- A web-based IDE (index.html + app.py) deployed on Render
- A CLI REPL for interactive use (main.py)
- LLM integration via OpenAI API (gpt-4o-mini) for simulated execution and comparison

---

## Programming Paradigm

NOVALANG is a **multi-paradigm language**. The main paradigm is **Procedural/Imperative**, with additional support for **Object-Oriented** and **Functional** programming.

**Imperative example:**
```
let A = 10
let B = 20
let C = A + B
display C
```

**Object-oriented example:**
```
class Animal
end
class Dog extends Animal
end
```

**Functional example:**
```
let double = lambda x -> x * 2
display double(5)
```

---

## Language Type

NOVALANG is a:
- **General Purpose Programming Language**
- **High Level Programming Language**

It abstracts hardware details, uses dynamic typing, and focuses on readability and simplicity. Programs run on any system with Python installed.

---

## Language Features

NOVALANG supports the following features:

- Variables and constants
- Arithmetic operations with correct operator precedence (PEMDAS/BODMAS)
- Conditional statements (if/else/end)
- While loops and For loops
- User-defined functions and recursion
- Classes and inheritance
- Lambda expressions and closures
- Exception handling (try/catch/end)
- Output statements (display / print)
- String literals with escape sequences
- Collections: lists, dictionaries, tuples
- Built-in functions: len, type, int, float, str, range, enumerate
- Logical operators: and, or, not
- Comparison operators: ==, !=, <, >, <=, >=
- Compound assignment: +=, -=
- Single-line comments (--)
- Multi-line comments (/* */)
- LLM simulation and comparison via OpenAI API

---

## Required Sample Program

The following is the required sample program from the project specification:

```
-- Sample program
let A = 20
let B = 40
let C = A + B * B

try
    let D = C / 0
catch
    display "Error: Division by zero attempted but not allowed."
end

display "The result is " C
```

**Output:**
```
Error: Division by zero attempted but not allowed.
The result is 1620
```

---

## Syntax Design

Unlike languages such as C or Java that use `{}` to define blocks, NOVALANG uses the keyword `end` to close all blocks.

```
if x > 5
    display "greater"
else
    display "smaller"
end

for i = 1 to 5
    display i
end

func greet(name)
    display "Hello " name
end
```

---

## Complete Token List

NOVALANG defines 64 tokens across three categories:

**Keywords (35):**
```
LET, DISPLAY, PRINT, IF, ELSE, END, WHILE, FOR, TO, FUNC,
LAMBDA, RETURN, TRY, CATCH, TRUE, FALSE, AND, OR, NOT, IN,
BREAK, CONTINUE, CLASS, EXTENDS, NULL, PASS, RANGE, LEN,
TYPE, ENUMERATE, INT, FLOAT, STR, DO, NEW
```

**Operators and Punctuation (26):**
```
PLUS, MINUS, TIMES, DIVIDE, MOD, POWER, EQUALS, PLUSEQ,
MINUSEQ, EQ, NE, LT, GT, LE, GE, LPAREN, RPAREN, LBRACK,
RBRACK, LBRACE, RBRACE, COMMA, DOT, COLON, SEMICOLON, ARROW
```

**Literals (3):**
```
NUMBER, STRING, IDENTIFIER
```

---

## Lexical Rules (Regular Expressions)

| Token | Regular Expression |
|---|---|
| IDENTIFIER | `[a-zA-Z_][a-zA-Z0-9_]*` |
| NUMBER | `\d+(\.\d+)?` |
| STRING | `"(?:\\.\|[^"\\])*"` |
| PLUS | `\+` |
| MINUS | `-` |
| TIMES | `\*` |
| DIVIDE | `/` |
| MOD | `%` |
| POWER | `\^` |
| EQUALS | `=` |
| EQ | `==` |
| NE | `!=` |
| LE | `<=` |
| GE | `>=` |
| LT | `<` |
| GT | `>` |
| Single-line comment | `--[^\n]*` |
| Multi-line comment | `/\*(.|\n)*?\*/` |

---

## Grammar (BNF)

```
<program>       ::= <statements> | ε
<statements>    ::= <statements> <statement> | <statement>
<statement>     ::= <var_decl> | <assignment> | <display_stmt>
                  | <if_stmt> | <while_stmt> | <for_stmt>
                  | <func_def> | <class_def> | <func_call>
                  | <return_stmt> | <try_stmt> | <break_stmt>
                  | <continue_stmt> | <pass_stmt> | ε

<var_decl>      ::= "let" IDENTIFIER "=" <expression>
<assignment>    ::= IDENTIFIER "=" <expression>
                  | IDENTIFIER "+=" <expression>
                  | IDENTIFIER "-=" <expression>

<display_stmt>  ::= "display" <display_args>
<display_args>  ::= <display_args> <expression> | <expression>

<if_stmt>       ::= "if" <expression> <statements> "end"
                  | "if" <expression> <statements> "else" <statements> "end"

<while_stmt>    ::= "while" <expression> <statements> "end"
<for_stmt>      ::= "for" IDENTIFIER "=" <expression> "to" <expression> <statements> "end"

<func_def>      ::= "func" IDENTIFIER "(" <param_list> ")" <statements> "end"
<class_def>     ::= "class" IDENTIFIER <statements> "end"
                  | "class" IDENTIFIER "extends" IDENTIFIER <statements> "end"

<try_stmt>      ::= "try" <statements> "catch" <statements> "end"

<expression>    ::= <expression> "+" <expression>
                  | <expression> "-" <expression>
                  | <expression> "*" <expression>
                  | <expression> "/" <expression>
                  | <expression> "%" <expression>
                  | <expression> "^" <expression>
                  | "(" <expression> ")"
                  | NUMBER | STRING | IDENTIFIER
                  | "true" | "false" | "null"
```

---

## Scope and Binding

NOVALANG uses **lexical (static) scope** implemented through a chain of `Env` objects.

- `let` always creates a new binding in the **current scope** using `define_var()`
- Bare assignment uses `set_var()` which walks up the scope chain to update an existing variable
- Each function call creates a new child scope: `f_env = Env(env)`
- Lambda expressions capture the enclosing scope at creation time (closures)
- `NovaError` is raised if you try to assign to an undeclared variable

```
let x = 100

func test()
    let x = 999   -- shadows global x, does not modify it
    display x     -- prints 999
end

test()
display x         -- prints 100
```

---

## Interpreter Architecture

NOVALANG follows the standard language processing pipeline:

```
Source Code
     |
     v
Lexical Analyzer (lexer.py)   — tokenizes source using PLY lex
     |
     v
Parser (parser.py)            — builds AST using PLY yacc (LALR(1))
     |
     v
Abstract Syntax Tree
     |
     v
Interpreter (interpreter.py)  — walks AST, performs semantic analysis
     |
     v
Program Output
```

---

## LLM Integration

NOVALANG includes integration with the **OpenAI API (gpt-4o-mini)** via the `/simulate` endpoint in `app.py`.

When you click **Simulate (LLM)** in the web UI:
1. The same source code is sent to the LLM
2. The LLM simulates execution line by line and returns a step-by-step trace
3. The result is compared against the deterministic interpreter output
4. Any differences are flagged as consistency warnings
5. The simulation is logged to `logs/simulations.jsonl`

| Feature | NOVALANG Interpreter | LLM (OpenAI) |
|---|---|---|
| Execution type | Deterministic | Probabilistic |
| Output consistency | Always identical | May vary |
| Syntax enforcement | Strict | Flexible |
| Error detection | Precise | Usually helpful |
| Use case | Ground-truth execution | Explanation and debugging |

---

## Error Handling

NOVALANG implements error handling at three levels:

**Lexical:** `t_error()` reports illegal characters with line number

**Syntax:** `p_error()` reports unexpected tokens with line number

**Runtime:** `NovaError` is raised for undefined variables, division by zero, and undeclared assignment targets

```
try
    let D = C / 0
catch
    display "Error: Division by zero attempted but not allowed."
end
```

---

## Running the Language

**Run a script file:**
```
python main.py test.nl
```

**Interactive REPL mode:**
```
python main.py
```

```
NOVALANG> let x = 10
NOVALANG> display x
10
NOVALANG> exit
```

**Web UI (local):**
```
pip install flask ply gunicorn
python app.py
```
Then open `http://localhost:5000` in your browser.

---

## Technologies Used

| Tool | Purpose |
|---|---|
| Python 3 | Implementation language |
| PLY (Python Lex-Yacc) | Lexer and LALR(1) parser generation |
| Flask | Web server for the IDE |
| Gunicorn | WSGI server for Render deployment |
| OpenAI API | LLM simulation and code assistance |
| Render | Cloud hosting platform |
| GitHub | Version control and repository hosting |

---

## Project Structure

```
NOVALANG/
│
├── lexer.py          — Lexical analyzer (PLY lex)
├── parser.py         — Syntax analyzer and AST builder (PLY yacc)
├── interpreter.py    — Semantic analyzer and tree-walking interpreter
├── app.py            — Flask web server and LLM integration
├── main.py           — CLI entry point and REPL
├── index.html        — Web-based IDE frontend
├── requirements.txt  — Dependencies (flask, ply, gunicorn)
├── render.yaml       — Render cloud deployment configuration
├── Procfile          — Gunicorn start command
├── test.nl           — Required sample program
├── novalang_demo.nl  — Feature demonstration program
└── README.md         — This file
```

---

## GitHub and Cloud Deployment

- **GitHub Repository:** https://github.com/coolieobowley95/NOVALANG
- **Live Demo:** https://novalang-4x9v.onrender.com/

The project is deployed on Render using Gunicorn as the WSGI server. Each request creates a fresh `Env()` scope so variables from one user's session do not persist into another user's session.

To clone the repository:
```
git clone https://github.com/coolieobowley95/NOVALANG.git
```

---

## Educational Purpose

NOVALANG was built to demonstrate all major phases of programming language implementation:

- Lexical analysis and tokenization
- Syntax analysis and parse tree / AST generation
- Semantic analysis and scope management
- Tree-walking interpretation and execution
- Exception handling at all three compiler levels
- LLM integration and comparison with deterministic execution
- Cloud deployment of a working language interpreter