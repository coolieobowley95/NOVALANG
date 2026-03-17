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
    
NOVALANG Lexer - Lexical Analysis Module
Performs tokenization for the NOVALANG language
"""
import ply.lex as lex
import re

# Reserved keywords
reserved = {
    'let': 'LET',
    'display': 'DISPLAY',
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'end': 'END',
    'while': 'WHILE',
    'do': 'DO',
    'for': 'FOR',
    'to': 'TO',
    'func': 'FUNC',
    'lambda': 'LAMBDA',
    'return': 'RETURN',
    'try': 'TRY',
    'catch': 'CATCH',
    'true': 'TRUE',
    'false': 'FALSE',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'in': 'IN',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'class': 'CLASS',
    'extends': 'EXTENDS',
    'new': 'NEW',
    'null': 'NULL',
    'pass': 'PASS',
    'range': 'RANGE',
    'len': 'LEN',
    'type': 'TYPE',
    'enumerate': 'ENUMERATE',
    'int': 'INT',
    'float': 'FLOAT',
    'str': 'STR',
}

# Token list
tokens = [
    'NUMBER', 'STRING', 'IDENTIFIER',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'POWER',
    'EQUALS', 'LPAREN', 'RPAREN', 'COMMA', 'DOT', 'COLON',
    'LBRACK', 'RBRACK', 'LBRACE', 'RBRACE',
    'LT', 'GT', 'LE', 'GE', 'EQ', 'NE',
    'SEMICOLON', 'ARROW', 'PLUSEQ', 'MINUSEQ',
] + list(reserved.values())

# Token definitions - Operators
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_POWER = r'\^'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACK = r'\['
t_RBRACK = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_DOT = r'\.'
t_COLON = r':'
t_SEMICOLON = r';'
t_ARROW = r'->'
t_PLUSEQ = r'\+='
t_MINUSEQ = r'-='

# Comparison operators (must be before EQUALS)
def t_LE(t):
    r'<='
    return t

def t_GE(t):
    r'>='
    return t

def t_EQ(t):
    r'=='
    return t

def t_NE(t):
    r'!='
    return t

def t_LT(t):
    r'<'
    return t

def t_GT(t):
    r'>'
    return t

t_EQUALS = r'='

# Ignore spaces and tabs
t_ignore = ' \t'

# Comments (single-line with --)
def t_COMMENT(t):
    r'--[^\n]*'
    pass  # Ignore comments

# Multi-line comments
def t_MULTICOMMENT(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass  # Ignore comments

# String literals (double quotes with escape sequences)
def t_STRING(t):
    r'"(?:\\.|[^"\\])*"'
    t.value = t.value[1:-1]  # Remove quotes
    # Process escape sequences
    t.value = t.value.replace('\\n', '\n').replace('\\t', '\t').replace('\\\\', '\\').replace('\\"', '"')
    return t

# Number literals (integers and floats)
def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

# Identifiers and reserved words
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'IDENTIFIER')
    return t

# Newline tracking
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()
