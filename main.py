"""
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
    
NOVALANG - Mini Programming Language
Main entry point with REPL and script execution

A dynamically-typed language supporting:
- Variables, constants, and expressions with correct operator precedence
- Collections (lists, dictionaries, tuples, sets)
- Control flow (if/else, while, for loops)
- Functions and lambdas
- Classes and inheritance
- Exception handling (try/catch)
- Built-in functions and methods
- Comments and multi-line statements
"""

import sys
import os
import traceback
from parser import parser
from interpreter import run, global_env, NovaError

# Program metadata
LANGUAGE_NAME = "NOVALANG"
VERSION = "1.0.0"
DESCRIPTION = "A mini programming language supporting OOP, dynamic typing, and functional programming"

def print_banner():
    """Print welcome banner"""
    print(f"\n{'='*70}")
    print(f"{LANGUAGE_NAME} v{VERSION}")
    print(f"{DESCRIPTION}")
    print(f"{'='*70}")
    print("Type 'help' for commands, 'exit' or 'quit' to quit\n")

def print_help():
    """Print help information"""
    print(f"""
{LANGUAGE_NAME} Commands:
  help         - Show this help message
  clear        - Clear the environment
  vars         - List all variables
  exit/quit    - Exit {LANGUAGE_NAME}

{LANGUAGE_NAME} Language Features:
  - Variables: let x = 10
  - Arithmetic: +, -, *, /, %, ^ (power)
  - Comparisons: <, >, <=, >=, ==, !=
  - Logic: and, or, not
  - Collections: [list]
  - Control: if/else, while, for, try/catch
  - Functions: func name() ... end
  - Classes: class Name ... end
  - Display: display "Hello World"
  - Comments: -- single line and /* single line */
""")

def clear_environment():
    """Clear all variables and functions"""
    global_env.vars.clear()
    global_env.funcs.clear()
    global_env.classes.clear()
    print("Environment cleared.")

def list_variables():
    """List all defined variables"""
    if not global_env.vars:
        print("No variables defined.")
    else:
        print("Variables:")
        for name, value in global_env.vars.items():
            print(f"  {name} = {value}")

def execute_code(code, filename="<stdin>"):
    """Execute NovaLang code"""
    try:
        # Remove empty lines and comments
        lines = code.strip().split('\n')
        filtered_lines = []
        for line in lines:
            # Remove comments
            if '--' in line:
                line = line[:line.index('--')]
            line = line.rstrip()
            if line:
                filtered_lines.append(line)

        if not filtered_lines:
            return

        code = '\n'.join(filtered_lines)

        # Parse the code
        ast = parser.parse(code)

        if ast is None:
            print("Syntax error: Failed to parse code")
            return

        # Execute the AST
        run(ast, global_env)

    except NovaError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        # Uncomment for debugging:
        # traceback.print_exc()

def repl():
    """Interactive REPL (Read-Eval-Print Loop)"""
    print_banner()

    prompt = f"{LANGUAGE_NAME}> "
    buffer = ""  # For multi-line input

    while True:
        try:
            # Get input
            if buffer:
                line = input("... ")  # Continuation prompt
            else:
                line = input(prompt)

            # Handle special commands
            if not buffer:
                if line.strip().lower() in ['exit', 'quit']:
                    print(f"Goodbye!")
                    break
                elif line.strip().lower() == 'help':
                    print_help()
                    continue
                elif line.strip().lower() == 'clear':
                    clear_environment()
                    continue
                elif line.strip().lower() == 'vars':
                    list_variables()
                    continue

            # Accumulate multi-line input
            buffer += line + '\n'

            # Check if statement is complete (very simple heuristic)
            # Count parentheses, brackets, and check for 'end' keyword
            open_count = buffer.count('(') + buffer.count('[') + buffer.count('{')
            close_count = buffer.count(')') + buffer.count(']') + buffer.count('}')

            # If line starts IF, WHILE, FOR, FUNC, CLASS, TRY - wait for END
            keywords = ['if ', 'while ', 'for ', 'func ', 'class ', 'try ']
            needs_end = any(buffer.strip().lower().startswith(kw) for kw in keywords)
            has_end = buffer.strip().lower().endswith('end')

            if open_count == close_count and (not needs_end or has_end) and buffer.strip():
                # Execute the complete statement
                execute_code(buffer)
                buffer = ""

        except KeyboardInterrupt:
            print("\n^C - Interrupted")
            buffer = ""
        except EOFError:
            print()
            break
        except Exception as e:
            print(f"Error: {e}")
            buffer = ""

def run_file(filename):
    """Execute a NovaLang script from a file"""
    try:
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found")
            return

        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()

        print(f"Running {filename}...")
        print("-" * 70)
        execute_code(code, filename=filename)
        print("-" * 70)

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error reading file: {e}")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Execute script file(s)
        for filename in sys.argv[1:]:
            run_file(filename)
    else:
        # Start interactive REPL
        try:
            repl()
        except KeyboardInterrupt:
            print("\n\nKeyboard interrupt. Exiting...")
            sys.exit(0)

if __name__ == "__main__":
    main()

