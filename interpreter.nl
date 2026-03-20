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
    
NOVALANG Interpreter - Semantic Analysis & Execution Module
Executes the AST and manages runtime state
"""

class BreakEx(Exception):
    pass


class ContinueEx(Exception):
    pass


class ReturnEx(Exception):
    def __init__(self, val):
        self.val = val


class NovaError(Exception):
    pass


class NovaObject:
    """Runtime object for NOVALANG classes"""
    def __init__(self, classname, attrs=None):
        self.classname = classname
        self.attrs = attrs or {}

    def get(self, name, default=None):
        return self.attrs.get(name, default)

    def set(self, name, value):
        self.attrs[name] = value

    def __repr__(self):
        return f"<{self.classname} {self.attrs}>"


class Env:
    """Environment/scope for variables, functions, and classes"""
    def __init__(self, parent=None):
        self.vars = {}
        self.funcs = {}
        self.classes = {}
        self.parent = parent

    def get_var(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get_var(name)
        raise NovaError(f"Variable '{name}' not defined")

    def set_var(self, name, value):
        """Set variable in current or parent scope"""
        if name in self.vars:
            self.vars[name] = value
        elif self.parent and self.parent.has_var(name):
            self.parent.set_var(name, value)
        else:
            # If not found in parent chain, define in current scope
            self.vars[name] = value

    def has_var(self, name):
        """Check if variable exists in scope chain"""
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.has_var(name)
        return False

    def define_var(self, name, value):
        """Define variable in current scope"""
        self.vars[name] = value

    def define_func(self, name, func):
        self.funcs[name] = func

    def get_func(self, name):
        if name in self.funcs:
            return self.funcs[name]
        if self.parent:
            return self.parent.get_func(name)
        raise NovaError(f"Function '{name}' not defined")

    def define_class(self, name, cls):
        self.classes[name] = cls

    def get_class(self, name):
        if name in self.classes:
            return self.classes[name]
        if self.parent:
            return self.parent.get_class(name)
        raise NovaError(f"Class '{name}' not defined")


# --- AST helpers ---
def is_true(val):
    """Determine truthiness of value"""
    return val is not None and val is not False


# --- Expression evaluator ---
def eval_expr(expr, env):
    """Evaluate an expression AST node"""
    # Literals
    if isinstance(expr, (int, float, str, bool)):
        return expr
    if expr is None:
        return None

    if isinstance(expr, tuple):
        tag = expr[0]

        # Variables
        if tag == 'var':
            return env.get_var(expr[1])

        # Constants
        if tag == 'num':
            return expr[1]
        if tag == 'str':
            return expr[1]
        if tag == 'bool':
            return expr[1]
        if tag == 'null':
            return None

        # Binary operations
        if tag == 'binop':
            op = expr[1]
            left = eval_expr(expr[2], env)
            right = eval_expr(expr[3], env)
            if op == '+':
                return left + right
            if op == '-':
                return left - right
            if op == '*':
                return left * right
            if op == '/':
                if right == 0:
                    raise NovaError('Division by zero')
                return left / right
            if op == '%':
                return left % right
            if op == '^' or op == '**':
                return left ** right

        # Comparison
        if tag == 'cmp':
            op = expr[1]
            left = eval_expr(expr[2], env)
            right = eval_expr(expr[3], env)
            if op == '==':
                return left == right
            if op == '!=':
                return left != right
            if op == '>':
                return left > right
            if op == '<':
                return left < right
            if op == '>=':
                return left >= right
            if op == '<=':
                return left <= right

        # Logical operations
        if tag == 'logic':
            op = expr[1]
            left = eval_expr(expr[2], env)
            right = eval_expr(expr[3], env)
            if op == 'and':
                return left and right
            if op == 'or':
                return left or right

        # Unary operations
        if tag == 'not':
            return not eval_expr(expr[1], env)
        if tag == 'uminus':
            return -eval_expr(expr[1], env)

        # Collections
        if tag == 'list':
            return [eval_expr(e, env) for e in expr[1]]
        if tag == 'tuple':
            return tuple(eval_expr(e, env) for e in expr[1])
        if tag == 'dict':
            d = {}
            for k, v in expr[1].items():
                d[k] = eval_expr(v, env) if isinstance(v, tuple) else v
            return d

        # Indexing
        if tag == 'index':
            container = env.get_var(expr[1])
            idx = eval_expr(expr[2], env)
            return container[int(idx)]

        # Attribute access
        if tag == 'attr':
            obj = env.get_var(expr[1])
            attr_name = expr[2]
            if isinstance(obj, NovaObject):
                return obj.get(attr_name)
            elif isinstance(obj, dict):
                return obj.get(attr_name)
            else:
                return getattr(obj, attr_name, None)

        # Function calls
        if tag == 'call':
            func_name = expr[1]
            args = [eval_expr(a, env) for a in expr[2]]
            func = env.get_func(func_name)
            return func(*args)

        # Built-in function calls
        if tag == 'call_builtin':
            name = expr[1]
            args = [eval_expr(a, env) for a in expr[2]]
            func = env.get_func(name)
            return func(*args)

        # Lambda (FIX: Complete implementation)
        if tag == 'lambda':
            params = expr[1]
            body = expr[2]
            # Capture environment at lambda creation time
            def lambda_fn(*args):
                lambda_env = Env(env)
                for pname, pval in zip(params, args):
                    lambda_env.define_var(pname, pval)
                try:
                    return eval_expr(body, lambda_env)
                except ReturnEx as r:
                    return r.val
            return lambda_fn

        # In operator
        if tag == 'in':
            val = eval_expr(expr[1], env)
            container = eval_expr(expr[2], env)
            return val in container

        # Method call
        if tag == 'method_call':
            obj = env.get_var(expr[1])
            method_name = expr[2]
            args = [eval_expr(a, env) for a in expr[3]]
            if isinstance(obj, NovaObject):
                # Call method on object
                method_fn = obj.attrs.get(method_name)
                if callable(method_fn):
                    return method_fn(*args)
            return None

    raise NovaError(f"Unknown expression type: {expr}")


# --- Statement executor ---
def exec_stmt(stmt, env):
    """Execute a statement AST node"""
    # Block
    if isinstance(stmt, tuple) and stmt and stmt[0] == 'block':
        for s in stmt[1]:
            exec_stmt(s, env)
        return

    # List of statements
    if isinstance(stmt, list):
        for s in stmt:
            if s:
                exec_stmt(s, env)
        return

    if not isinstance(stmt, tuple) or not stmt:
        return

    t = stmt[0]

    # Variable declaration
    if t == 'let':
        env.define_var(stmt[1], eval_expr(stmt[2], env))

    # Assignment
    elif t == 'assign':
        env.set_var(stmt[1], eval_expr(stmt[2], env))

    # Compound assignment
    elif t == 'assign_op':
        name = stmt[1]
        op = stmt[2]
        val = eval_expr(stmt[3], env)
        current = env.get_var(name)
        if op == '+':
            result = current + val
        elif op == '-':
            result = current - val
        env.set_var(name, result)

    # Index assignment (list[i] = val)
    elif t == 'assign_index':
        arr = env.get_var(stmt[1])
        idx = eval_expr(stmt[2], env)
        arr[int(idx)] = eval_expr(stmt[3], env)

    # Attribute assignment (obj.attr = val)
    elif t == 'assign_attr':
        obj = env.get_var(stmt[1])
        attr_name = stmt[2]
        val = eval_expr(stmt[3], env)
        if isinstance(obj, NovaObject):
            obj.set(attr_name, val)
        elif isinstance(obj, dict):
            obj[attr_name] = val
        else:
            setattr(obj, attr_name, val)

    # Display/Print
    elif t == 'display':
        # Handle multiple arguments - concatenate and print
        args = stmt[1] if isinstance(stmt[1], list) else [stmt[1]]
        output = ''.join(str(eval_expr(arg, env)) for arg in args)
        print(output)

    # If statement
    elif t == 'if':
        cond = eval_expr(stmt[1], env)
        if is_true(cond):
            exec_stmt(stmt[2], env)
        elif len(stmt) > 3 and stmt[3]:
            exec_stmt(stmt[3], env)

    # While loop (FIX: Use same env for condition & body)
    elif t == 'while':
        while is_true(eval_expr(stmt[1], env)):
            try:
                exec_stmt(stmt[2], env)
            except BreakEx:
                break
            except ContinueEx:
                continue

    # For loop (FIX: Create loop var in same env)
    elif t == 'for':
        start = int(eval_expr(stmt[2], env))
        end = int(eval_expr(stmt[3], env))
        loop_var = stmt[1]
        loop_body = stmt[4]
        # Define loop variable in current env
        for i in range(start, end + 1):
            env.define_var(loop_var, i)
            try:
                exec_stmt(loop_body, env)
            except BreakEx:
                break
            except ContinueEx:
                continue

    # Break
    elif t == 'break':
        raise BreakEx()

    # Continue
    elif t == 'continue':
        raise ContinueEx()

    # Return
    elif t == 'return':
        val = eval_expr(stmt[1], env) if len(stmt) > 1 and stmt[1] else None
        raise ReturnEx(val)

    # Function definition
    elif t == 'func':
        name = stmt[1]
        params = stmt[2]
        body = stmt[3]

        def f(*args):
            f_env = Env(env)
            for pname, pval in zip(params, args):
                f_env.define_var(pname, pval)
            try:
                exec_stmt(body, f_env)
                return None
            except ReturnEx as r:
                return r.val

        env.define_func(name, f)

    # Class definition
    elif t == 'class':
        name = stmt[1]
        parent_name = stmt[2]
        body = stmt[3]
        env.define_class(name, stmt)

    # Try-Catch
    elif t == 'try':
        try:
            exec_stmt(stmt[1], env)
        except BreakEx:
            raise
        except ContinueEx:
            raise
        except ReturnEx:
            raise
        except Exception as e:
            if len(stmt) > 2 and stmt[2]:
                exec_stmt(stmt[2], env)
            else:
                print(f"Error: {e}")

    # Pass
    elif t == 'pass':
        return

    else:
        # Try to evaluate as expression statement
        try:
            eval_expr(stmt, env)
        except:
            pass


# --- Built-in functions ---
def add_builtins(env):
    """Register built-in functions"""
    env.define_func('len', lambda x: len(x))
    env.define_func('type', lambda x: type(x).__name__)
    env.define_func('int', lambda x: int(x))
    env.define_func('float', lambda x: float(x))
    env.define_func('str', lambda x: str(x))
    env.define_func('range', lambda *args: list(range(*map(int, args))))
    env.define_func('enumerate', lambda x: list(enumerate(x)))
    env.define_func('list', lambda x: list(x))
    env.define_func('tuple', lambda x: tuple(x))
    env.define_func('dict', lambda: {})
    env.define_func('abs', lambda x: abs(x))
    env.define_func('min', lambda *args: min(args))
    env.define_func('max', lambda *args: max(args))
    env.define_func('sum', lambda x: sum(x))
    env.define_func('print', lambda *args: print(*args))
    env.define_func('input', lambda prompt='': input(prompt))


# --- Global environment ---
global_env = Env()
add_builtins(global_env)


def run(ast, env=None):
    """Execute an AST"""
    if env is None:
        env = global_env
    if isinstance(ast, tuple) and ast and ast[0] == 'block':
        exec_stmt(ast, env)
    elif isinstance(ast, list):
        exec_stmt(ast, env)
    else:
        raise NovaError('Invalid AST root')


if __name__ == '__main__':
    import readline
    print('NovaLang Interpreter')
    while True:
        try:
            line = input('NOVALANG> ')
            if not line.strip():
                continue
            from parser import parser
            ast = parser.parse(line)
            if ast:
                run(ast)
        except KeyboardInterrupt:
            print('\n^C')
        except Exception as e:
            print('Error:', e)



