import ast
import polars as pl

class SafeASTValidator(ast.NodeVisitor):
    def __init__(self, df_columns: list[str]):
        self.df_columns = set(df_columns)
        # Whitelist of allowed AST nodes
        self.allowed_nodes = {
            ast.Expression,
            ast.Expr,
            ast.Call,
            ast.Attribute,
            ast.Name,
            ast.Constant,
            ast.List,
            ast.Tuple,
            ast.Dict,
            ast.BinOp,
            ast.UnaryOp,
            ast.Compare,
            ast.keyword,
            ast.Slice,
            ast.Subscript,
            ast.Load,
        }
        # Whitelist of allowed global names
        self.allowed_names = {"df", "pl", "True", "False", "None"}

    def visit(self, node):
        # Check node type
        node_type = type(node)
        if node_type not in self.allowed_nodes:
            raise ValueError(f"Blocked unsafe operation or construct: {node_type.__name__}")
        
        # Check name nodes
        if isinstance(node, ast.Name):
            if node.id not in self.allowed_names:
                raise ValueError(f"Blocked access to unauthorized variable or function: '{node.id}'")
                
        # Check attribute nodes
        if isinstance(node, ast.Attribute):
            if node.attr.startswith("__"):
                raise ValueError(f"Blocked access to private/special attribute: '{node.attr}'")

        # Check call nodes for columns
        if isinstance(node, ast.Call):
            self._check_call_columns(node)

        # Continue traversing
        self.generic_visit(node)

    def _check_call_columns(self, node: ast.Call):
        # 1. Check pl.col(...) or col(...) calls
        is_col_call = False
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "pl" and node.func.attr == "col":
                is_col_call = True
        elif isinstance(node.func, ast.Name) and node.func.id == "col":
            is_col_call = True

        if is_col_call and node.args:
            first_arg = node.args[0]
            self._validate_column_arg(first_arg)

        # 2. Check dataframe methods that accept columns directly
        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr
            if method_name in {"select", "group_by", "groupby", "sort", "drop"}:
                # Check positional args
                for arg in node.args:
                    self._validate_column_arg(arg)
                # Check keywords (e.g. by=...)
                for kw in node.keywords:
                    if kw.arg in {"by", "on", "left_on", "right_on"}:
                        self._validate_column_arg(kw.value)

    def _validate_column_arg(self, node: ast.AST):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value not in self.df_columns:
                raise ValueError(f"Column '{node.value}' does not exist in the dataset.")
        elif isinstance(node, (ast.List, ast.Tuple)):
            for elt in node.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    if elt.value not in self.df_columns:
                        raise ValueError(f"Column '{elt.value}' does not exist in the dataset.")

def execute_query(code: str, df: pl.DataFrame, required_columns: list[str] = None) -> dict:
    """
    Safely executes a generated Polars query string on a dataframe.
    """
    # 1. Validate required columns list if provided
    if required_columns:
        for col in required_columns:
            if col not in df.columns:
                return {
                    "success": False,
                    "error": f"Validated query requires column '{col}' which is missing from the dataset."
                }

    # 2. Parse and Validate the code AST
    try:
        # Parse in eval mode (only accepts single expressions, blocking statements and imports)
        parsed_ast = ast.parse(code.strip(), mode="eval")
        
        # Walk and validate AST
        validator = SafeASTValidator(df.columns)
        validator.visit(parsed_ast)
    except SyntaxError as e:
        return {
            "success": False,
            "error": f"Invalid syntax in query: {e.msg} at line {e.lineno}, col {e.offset}"
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Validation failed: {str(e)}"
        }

    # 3. Compile and execute
    try:
        compiled_code = compile(parsed_ast, "<string>", "eval")
        # Strict namespace: block imports, filesystem access, builtins
        namespace = {
            "df": df,
            "pl": pl,
            "__builtins__": {
                "len": len,
                "int": int,
                "float": float,
                "str": str,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "min": min,
                "max": max,
                "sum": sum,
                "abs": abs,
                "round": round,
            }
        }
        
        result = eval(compiled_code, namespace, {})
        
        # Format output
        if isinstance(result, pl.DataFrame):
            serializable_result = result.to_dicts()
        elif isinstance(result, pl.Series):
            serializable_result = result.to_list()
        else:
            if hasattr(result, "to_list"):
                serializable_result = result.to_list()
            elif hasattr(result, "to_dicts"):
                serializable_result = result.to_dicts()
            else:
                serializable_result = result
                
        return {
            "success": True,
            "result": serializable_result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Execution error: {str(e)}"
        }
