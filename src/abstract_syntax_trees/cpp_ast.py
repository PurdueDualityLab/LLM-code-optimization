from abstract_syntax_trees.abstract_syntax_tree import AbstractSyntaxTree
import subprocess
import re

class CPPAST(AbstractSyntaxTree):
    def __init__(self, language):
        super().__init__(language)

    def create_ast(self, source_code_path) -> str:
        command = f"clang++ -Xclang -ast-dump -fsyntax-only {source_code_path} | grep -A 1000 {source_code_path}"
        ast = subprocess.run(command, shell=True, capture_output=True, text=True)
        ast = ast.stdout
        return self.clean_ast(ast)
    
    def clean_ast(self, ast_text):
        # Remove memory addresses (0x followed by hex digits)
        ast_text = re.sub(r'0x[0-9a-fA-F]+', '', ast_text)
        
        # Remove file path and location info inside <>
        ast_text = re.sub(r'<[^>]+>', '', ast_text)
        
        # Remove line and column markers (e.g., line:4:5, col:19)
        ast_text = re.sub(r'\b(line|col):\d+(:\d+)?', '', ast_text)

        # Remove excessive spaces from cleaned lines while keeping line breaks
        ast_text = '\n'.join(line.strip() for line in ast_text.splitlines())
        
        return ast_text   
    
    def parse_ast(self):
        """
        Implement later based on how we decide to use the AST.
        """
        pass