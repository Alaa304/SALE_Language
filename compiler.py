import re
from typing import List

# -------------------------------
# Token
# -------------------------------
class Token:
    def __init__(self, kind: str, lexeme: str, line: int):
        self.kind = kind
        self.lexeme = lexeme
        self.line = line

    def __repr__(self):
        return f"{self.kind}('{self.lexeme}') [line {self.line}]"


# -------------------------------
# AST Node (Ready for future use)
# -------------------------------
class STNode:
    def __init__(self, kind: str, value=None, children=None, dtype=None, line=None):
        self.kind = kind
        self.value = value
        self.children = children if children else []
        self.dtype = dtype
        self.line = line


# -------------------------------
# Symbol Table
# -------------------------------
class IdentifierInfo:
    def __init__(self, name, dtype, line):
        self.name = name
        self.dtype = dtype
        self.line = line

    def __repr__(self):
        return f"{self.name} : {self.dtype} (line {self.line})"


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def declare(self, name, dtype, line):
        cur = self.scopes[-1]
        if name in cur:
            return f"Redeclaration of '{name}'"
        cur[name] = IdentifierInfo(name, dtype, line)
        return None

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def print_table(self):
        print("\n===== SYMBOL TABLE =====")
        for i, scope in enumerate(self.scopes):
            print(f"Scope {i}:")
            if not scope:
                print("  (empty)")
            for k in scope.values():
                print(" ", k)
        print("========================\n")


# -------------------------------
# Scanner
# -------------------------------
token_specification = [

    ('PROGRAM_START', r'esal\(\)'),

    ('ELSE', r'@@\?'),
    ('RETURN', r'\$\$@'),
    ('FUNC_DEF', r'@@'),

    ('VAR_INT', r'##'),
    ('OUTPUT', r'@\$'),
    ('IF', r'@\?'),

    ('NUMBER', r'\d+(\.\d+)?'),
    ('STRING', r'"[^"]*"'),

    ('ASSIGN', r'='),
    ('ARITH_OP', r'[+\-*/]'),

    ('IDENTIFIER', r'[A-Za-z_]\w*'),

    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),

    ('SEMICOLON', r';'),

    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('MISMATCH', r'.')
]

regex = "|".join(f"(?P<{n}>{p})" for n, p in token_specification)
scanner = re.compile(regex)


def scan_esal(code):
    tokens = []
    line = 1

    for m in scanner.finditer(code):
        kind = m.lastgroup
        lex = m.group()

        if kind == 'NEWLINE':
            line += 1
            continue

        if kind == 'SKIP':
            continue

        if kind == 'MISMATCH':
            continue

        tokens.append((kind, lex, Token(kind, lex, line)))

    tokens.append(('EOF', '', Token('EOF', '', line)))
    return tokens


# -------------------------------
# Parser
# -------------------------------
class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

        self.symtab = SymbolTable()

        self.errors = []
        self.warnings = []

    def current(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.current()
        self.pos += 1
        return tok

    def match(self, kind):
        tok = self.current()

        if tok[0] == kind:
            return self.advance()

        raise SyntaxError(f"Expected {kind} at line {tok[2].line}")

    # -------------------------

    def parse_program(self):

        self.match('PROGRAM_START')
        self.match('LBRACE')

        while self.current()[0] != 'RBRACE':
            self.parse_statement()

        self.match('RBRACE')

        if self.current()[0] != 'EOF':
            self.errors.append("Unexpected tokens after program end")

    # -------------------------

    def parse_statement(self):

        tok = self.current()

        if tok[0] == 'VAR_INT':
            self.parse_declaration()

        elif tok[0] == 'IDENTIFIER':
            self.parse_assignment()

        elif tok[0] == 'OUTPUT':
            self.parse_output()

        else:
            self.advance()

    # -------------------------

    def parse_declaration(self):

        self.advance()

        name_tok = self.match('IDENTIFIER')
        name = name_tok[1]

        self.symtab.declare(name, 'int', name_tok[2].line)

        if self.current()[0] == 'ASSIGN':
            self.advance()
            self.parse_expr()

        self.match('SEMICOLON')

    # -------------------------

    def parse_assignment(self):

        name_tok = self.match('IDENTIFIER')
        name = name_tok[1]

        self.match('ASSIGN')

        expr_type = self.parse_expr()

        info = self.symtab.lookup(name)

        if info and expr_type and info.dtype != expr_type:
            self.errors.append(
                f"Type Error at line {name_tok[2].line}: cannot assign {expr_type} to {info.dtype}"
            )

        self.match('SEMICOLON')

        if info is None:
            self.warnings.append(
                f"Undeclared variable '{name}' at line {name_tok[2].line}"
            )

    # -------------------------

    def parse_output(self):

        self.advance()
        self.parse_expr()
        self.match('SEMICOLON')

    # -------------------------

    def parse_expr(self):

        tok = self.current()

        if tok[0] == 'NUMBER':
            self.advance()
            dtype = 'int'

        elif tok[0] == 'STRING':
            self.advance()
            dtype = 'string'

        elif tok[0] == 'IDENTIFIER':
            info = self.symtab.lookup(tok[1])
            self.advance()

            dtype = info.dtype if info else None

        else:
            raise SyntaxError(f"Invalid expression at line {tok[2].line}")

        while self.current()[0] == 'ARITH_OP':

            self.advance()

            right = self.current()

            if right[0] not in ('NUMBER', 'STRING', 'IDENTIFIER'):
                raise SyntaxError(f"Expected operand at line {right[2].line}")

            self.advance()

        return dtype


# -------------------------------
# API FOR UI
# -------------------------------
def run_compiler(code):

    tokens = scan_esal(code)
    parser = Parser(tokens)

    result = {
        "errors": [],
        "warnings": [],
        "symbol_table": ""
    }

    try:
        parser.parse_program()
    except SyntaxError as e:
        result["errors"].append(str(e))
        return result

    result["errors"] = parser.errors
    result["warnings"] = parser.warnings

    import io
    import sys

    buffer = io.StringIO()
    sys.stdout = buffer
    parser.symtab.print_table()
    sys.stdout = sys.__stdout__

    result["symbol_table"] = buffer.getvalue()

    return result
