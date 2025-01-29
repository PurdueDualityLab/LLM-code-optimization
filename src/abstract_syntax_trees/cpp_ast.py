from abstract_syntax_tree import AbstractSyntaxTree
import ast
import subprocess


class CPPAST(AbstractSyntaxTree):
    def __init__(self, language):
        super().__init__(language)

    def create_ast(self, source_code_path) -> str:
        command = f"clang++ -Xclang -ast-dump=json -fsyntax-only {source_code_path}"
        ast = subprocess.run(command, shell=True, capture_output=True, text=True)
        return ast.stdout
        
    def parse_ast(self):
        """
        Implement later based on how we decide to use the AST.
        """
        pass