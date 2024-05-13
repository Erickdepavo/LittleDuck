from .nodes import ASTNode


class LittleDuckError(Exception):
    """Little Duck Code Analysis Exception"""
    def __init__(self, message: str, node: ASTNode) -> None:
        super().__init__(message, node)
        self.message = message
        self.node = node

class SemanticError(LittleDuckError):
    """Little Duck Semantic Analysis Exception"""
    pass