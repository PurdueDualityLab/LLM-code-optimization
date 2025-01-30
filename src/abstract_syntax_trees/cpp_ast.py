from abstract_syntax_trees.abstract_syntax_tree import AbstractSyntaxTree
import subprocess
import json

class CPPAST(AbstractSyntaxTree):
    def __init__(self, language):
        super().__init__(language)

    def create_ast(self, source_code_path) -> str:
        command = f"clang++ -Xclang -ast-dump=json -fsyntax-only {source_code_path}"
        ast = subprocess.run(command, shell=True, capture_output=True, text=True)
        ast = ast.stdout
        ast = json.loads(ast)
        self._remove_fields(ast)
        return ast
    
    def _remove_fields(self, node):
        """
        Recursively remove specific fields from a JSON AST node.
        """
        fields_to_remove = ["id", "range", "loc"]
        if isinstance(node, dict):
            for field in fields_to_remove:
                if field in node:
                    del node[field]
            for key, value in node.items():
                self._remove_fields(value)
        elif isinstance(node, list):
            for item in node:
                self._remove_fields(item)    
    
    def parse_ast(self):
        """
        Implement later based on how we decide to use the AST.
        """
        pass