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

NOVALANG Parser - Syntax Analysis Module
Builds Abstract Syntax Tree (AST) for the NOVALANG language
"""
import ply.yacc as yacc
from lexer import tokens

# Operator precedence (PEMDAS/BODMAS order)
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'EQ', 'NE', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'POWER'),
    ('right', 'UMINUS'),  # Unary minus
)

# Program root rule
def p_program(p):
    '''program : statements
               | empty'''
    p[0] = ('block', p[1] if p[1] else [])

# Statements
def p_statements(p):
    '''statements : statements statement
                  | statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]] if p[2] else p[1]
    else:
        p[0] = [p[1]] if p[1] else []

# Statement types
def p_statement(p):
    '''statement : var_decl
                 | assignment
                 | display
                 | if_stmt
                 | while_stmt
                 | for_stmt
                 | func_def
                 | class_def
                 | func_call
                 | return_stmt
                 | try_stmt
                 | break_stmt
                 | continue_stmt
                 | pass_stmt
                 | expression SEMICOLON
                 | empty'''
    p[0] = p[1]

def p_empty(p):
    'empty :'
    pass

# Variable declaration
def p_var_decl(p):
    'var_decl : LET IDENTIFIER EQUALS expression'
    p[0] = ('let', p[2], p[4])

# Assignment
def p_assignment(p):
    '''assignment : IDENTIFIER EQUALS expression
                  | IDENTIFIER LBRACK expression RBRACK EQUALS expression
                  | IDENTIFIER DOT IDENTIFIER EQUALS expression
                  | IDENTIFIER PLUSEQ expression
                  | IDENTIFIER MINUSEQ expression'''
    if len(p) == 4:
        p[0] = ('assign', p[1], p[3])
    elif len(p) == 7:
        p[0] = ('assign_index', p[1], p[3], p[6])
    elif len(p) == 6:
        if p[2] == '.':
            p[0] = ('assign_attr', p[1], p[3], p[5])
        else:  # += or -=
            op = '+' if p[2] == '+=' else '-'
            p[0] = ('assign_op', p[1], op, p[3])

# Display/Print statement (space-separated arguments, no commas needed)
def p_display(p):
    '''display : DISPLAY display_args
               | PRINT display_args'''
    p[0] = ('display', p[2])

# Display arguments (space-separated, not comma-separated)
def p_display_args(p):
    '''display_args : display_args expression
                    | expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

# If statement
def p_if_stmt(p):
    '''if_stmt : IF expression statements END
               | IF expression statements ELSE statements END'''
    if len(p) == 5:
        p[0] = ('if', p[2], p[3], [])
    else:
        p[0] = ('if', p[2], p[3], p[5])

# While loop
def p_while_stmt(p):
    'while_stmt : WHILE expression statements END'
    p[0] = ('while', p[2], p[3])

# For loop (inclusive)
def p_for_stmt(p):
    'for_stmt : FOR IDENTIFIER EQUALS expression TO expression statements END'
    p[0] = ('for', p[2], p[4], p[6], p[7])

# Function definition with parameters
def p_func_def(p):
    '''func_def : FUNC IDENTIFIER LPAREN RPAREN statements END
                | FUNC IDENTIFIER LPAREN param_list RPAREN statements END'''
    if len(p) == 7:
        p[0] = ('func', p[2], [], p[5])
    else:
        p[0] = ('func', p[2], p[4], p[6])

# Parameter list
def p_param_list(p):
    '''param_list : param_list COMMA IDENTIFIER
                  | IDENTIFIER'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# Class definition
def p_class_def(p):
    '''class_def : CLASS IDENTIFIER statements END
                 | CLASS IDENTIFIER EXTENDS IDENTIFIER statements END'''
    if len(p) == 5:
        p[0] = ('class', p[2], None, p[3])
    else:
        p[0] = ('class', p[2], p[4], p[5])

# Function call with arguments
def p_func_call(p):
    '''func_call : IDENTIFIER LPAREN RPAREN
                 | IDENTIFIER LPAREN args RPAREN'''
    if len(p) == 4:
        p[0] = ('call', p[1], [])
    else:
        p[0] = ('call', p[1], p[3])

# Argument list
def p_args(p):
    '''args : args COMMA expression
            | expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# Return statement
def p_return_stmt(p):
    '''return_stmt : RETURN expression
                   | RETURN'''
    if len(p) == 2:
        p[0] = ('return', ('bool', 'null'))
    else:
        p[0] = ('return', p[2])

# Try-Catch statement
def p_try_stmt(p):
    '''try_stmt : TRY statements CATCH statements END
                | TRY statements CATCH statement END
                | TRY statement CATCH statements END
                | TRY statement CATCH statement'''
    # p[2] is the try-body (either a `statements` list or a single `statement`),
    # p[4] is the catch-body. Normalize both into AST nodes as-is.
    p[0] = ('try', p[2], p[4])

# Break statement
def p_break_stmt(p):
    'break_stmt : BREAK'
    p[0] = ('break',)

# Continue statement
def p_continue_stmt(p):
    'continue_stmt : CONTINUE'
    p[0] = ('continue',)

# Pass statement
def p_pass_stmt(p):
    'pass_stmt : PASS'
    p[0] = ('pass',)

# ============= EXPRESSIONS =============

# Binary operations
def p_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MOD expression
                  | expression POWER expression'''
    p[0] = ('binop', p[2], p[1], p[3])

# Unary minus
def p_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = ('uminus', p[2])

# Comparison operators
def p_cmp(p):
    '''expression : expression LT expression
                  | expression GT expression
                  | expression LE expression
                  | expression GE expression
                  | expression EQ expression
                  | expression NE expression'''
    p[0] = ('cmp', p[2], p[1], p[3])

# Logical operators
def p_logic(p):
    '''expression : expression AND expression
                  | expression OR expression'''
    p[0] = ('logic', p[2], p[1], p[3])

# Negation
def p_not(p):
    'expression : NOT expression'
    p[0] = ('not', p[2])

# Parenthesized expression
def p_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

# In operator
def p_in_expr(p):
    'expression : expression IN expression'
    p[0] = ('in', p[1], p[3])

# Array/List indexing
def p_index(p):
    'expression : IDENTIFIER LBRACK expression RBRACK'
    p[0] = ('index', p[1], p[3])

# Attribute access
def p_attr(p):
    'expression : IDENTIFIER DOT IDENTIFIER'
    p[0] = ('attr', p[1], p[3])

# Method call
def p_method_call(p):
    '''expression : IDENTIFIER DOT IDENTIFIER LPAREN RPAREN
                  | IDENTIFIER DOT IDENTIFIER LPAREN args RPAREN'''
    if len(p) == 6:
        p[0] = ('method_call', p[1], p[3], [])
    else:
        p[0] = ('method_call', p[1], p[3], p[5])

# List literal
def p_list(p):
    '''expression : LBRACK RBRACK
                  | LBRACK list_items RBRACK'''
    if len(p) == 3:
        p[0] = ('list', [])
    else:
        p[0] = ('list', p[2])

# List items
def p_list_items(p):
    '''list_items : list_items COMMA expression
                  | expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# Dictionary/Map literal
def p_dict(p):
    '''expression : LBRACE RBRACE
                  | LBRACE dict_items RBRACE'''
    if len(p) == 3:
        p[0] = ('dict', {})
    else:
        p[0] = ('dict', p[2])

# Dictionary items
def p_dict_items(p):
    '''dict_items : dict_items COMMA IDENTIFIER COLON expression
                  | IDENTIFIER COLON expression'''
    if len(p) == 4:
        p[0] = {p[1]: p[3]}
    else:
        p[0] = p[1]
        p[0][p[3]] = p[5]

# Tuple literal
def p_tuple(p):
    'expression : LPAREN tuple_items RPAREN'
    p[0] = ('tuple', p[2])

# Tuple items (at least 2 items or trailing comma)
def p_tuple_items(p):
    '''tuple_items : tuple_items COMMA expression
                   | expression COMMA expression
                   | expression COMMA'''
    if len(p) == 3 and isinstance(p[1], list):
        p[0] = p[1] + [p[3]]
    elif len(p) == 3:
        p[0] = [p[1], p[3]]
    else:
        p[0] = [p[1]]

# Lambda expression
def p_lambda(p):
    'expression : LAMBDA param_list ARROW expression'
    p[0] = ('lambda', p[2], p[4])

# Built-in function calls
def p_builtin_len(p):
    'expression : LEN LPAREN expression RPAREN'
    p[0] = ('call_builtin', 'len', [p[3]])

def p_builtin_type(p):
    'expression : TYPE LPAREN expression RPAREN'
    p[0] = ('call_builtin', 'type', [p[3]])

def p_builtin_int(p):
    'expression : INT LPAREN expression RPAREN'
    p[0] = ('call_builtin', 'int', [p[3]])

def p_builtin_float(p):
    'expression : FLOAT LPAREN expression RPAREN'
    p[0] = ('call_builtin', 'float', [p[3]])

def p_builtin_str(p):
    'expression : STR LPAREN expression RPAREN'
    p[0] = ('call_builtin', 'str', [p[3]])

def p_builtin_range(p):
    '''expression : RANGE LPAREN expression RPAREN
                  | RANGE LPAREN expression COMMA expression RPAREN
                  | RANGE LPAREN expression COMMA expression COMMA expression RPAREN'''
    if len(p) == 5:
        p[0] = ('call_builtin', 'range', [p[3]])
    elif len(p) == 7:
        p[0] = ('call_builtin', 'range', [p[3], p[5]])
    else:
        p[0] = ('call_builtin', 'range', [p[3], p[5], p[7]])

def p_builtin_enumerate(p):
    'expression : ENUMERATE LPAREN expression RPAREN'
    p[0] = ('call_builtin', 'enumerate', [p[3]])

# Literals
def p_number(p):
    'expression : NUMBER'
    p[0] = ('num', p[1])

def p_string(p):
    'expression : STRING'
    p[0] = ('str', p[1])

def p_true(p):
    'expression : TRUE'
    p[0] = ('bool', True)

def p_false(p):
    'expression : FALSE'
    p[0] = ('bool', False)

def p_null(p):
    'expression : NULL'
    p[0] = ('null',)

def p_identifier(p):
    'expression : IDENTIFIER'
    p[0] = ('var', p[1])

# Error handling
def p_error(p):
    if p:
        print(f"Syntax Error at '{p.value}' (line {p.lineno})")
    else:
        print("Syntax Error: Unexpected end of input")

# Build parser
parser = yacc.yacc(debug=False, write_tables=False)
