import os
import ast
import json

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "DATA")
OUT_FILE = os.path.join(DATA_DIR, "code_knowledge.json")

def extract(target_path: str):
    """
    Extract AST-level code knowledge from a file or directory
    """

    data = {
        "functions": {},
        "classes": {},
        "calls": {},
        "syntax_errors": [],
        "logical_bugs": []
    }

    class CodeAnalyzer(ast.NodeVisitor):
        def __init__(self, file, code):
            self.file = file
            self.lines = code.splitlines()
            self.current_function = None

        def visit_FunctionDef(self, node):
            code_block = "\n".join(
                self.lines[node.lineno - 1 : node.end_lineno]
            )

            data["functions"][node.name] = {
                "name": node.name,
                "file": self.file,
                "start": node.lineno,
                "end": node.end_lineno,
                "code": code_block,
                "called_by": []
            }

            self.current_function = node.name
            self.generic_visit(node)
            self.current_function = None

        def visit_ClassDef(self, node):
            code_block = "\n".join(
                self.lines[node.lineno - 1 : node.end_lineno]
            )

            data["classes"][node.name] = {
                "name": node.name,
                "file": self.file,
                "start": node.lineno,
                "end": node.end_lineno,
                "code": code_block
            }

            self.generic_visit(node)

        def visit_Call(self, node):
            if self.current_function:
                if isinstance(node.func, ast.Name):
                    data["calls"].setdefault(
                        self.current_function, []
                    ).append(node.func.id)

                elif isinstance(node.func, ast.Attribute):
                    data["calls"].setdefault(
                        self.current_function, []
                    ).append(node.func.attr)

            self.generic_visit(node)

    class LogicalBugAnalyzer(ast.NodeVisitor):
        def __init__(self, file):
            self.file = file
            self.defined = set()
            self.used = set()
            self.bugs = []

        def visit_FunctionDef(self, node):
            for arg in node.args.args:
                self.defined.add(arg.arg)
            self.generic_visit(node)

        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.defined.add(target.id)
            self.generic_visit(node)

        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Load):
                self.used.add(node.id)
            self.generic_visit(node)

        def visit_Try(self, node):
            for handler in node.handlers:
                if handler.body and isinstance(handler.body[0], ast.Pass):
                    self.bugs.append({
                        "type": "EmptyExceptBlock",
                        "file": self.file,
                        "line": handler.lineno
                    })
            self.generic_visit(node)

        def finalize(self):
            for var in self.defined - self.used:
                self.bugs.append({
                    "type": "UnusedVariable",
                    "name": var,
                    "file": self.file
                })

    # Collect Python files
    python_files = []

    if os.path.isfile(target_path):
        python_files.append(target_path)
    else:
        for root, _, files in os.walk(target_path):
            for f in files:
                if f.endswith(".py"):
                    python_files.append(os.path.join(root, f))

    # ------------------------------------
    # Parse files
    # ------------------------------------
    for file in python_files:
        try:
            code = open(file, encoding="utf8").read()

            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                data["syntax_errors"].append({
                    "type": "SyntaxError",
                    "file": file,
                    "line": e.lineno,
                    "message": e.msg
                })
                continue

            CodeAnalyzer(file, code).visit(tree)

            bug = LogicalBugAnalyzer(file)
            bug.visit(tree)
            bug.finalize()
            data["logical_bugs"].extend(bug.bugs)

        except Exception:
            pass

    # Reverse call graph
    for caller, callees in data["calls"].items():
        for callee in callees:
            if callee in data["functions"]:
                data["functions"][callee]["called_by"].append(caller)

    os.makedirs(DATA_DIR, exist_ok=True)
    json.dump(data, open(OUT_FILE, "w", encoding="utf8"), indent=2)
