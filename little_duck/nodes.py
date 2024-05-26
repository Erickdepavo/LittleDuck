from dataclasses import dataclass
from typing import Any, List, Optional

from .quadruples import QuadrupleOperation


#
# Base Nodes
#
@dataclass
class ASTNode:
    pass

@dataclass
class TypeNode(ASTNode):
    identifier: str

@dataclass
class StatementNode(ASTNode):
    pass

@dataclass
class ExpressionNode(ASTNode):
    type: Optional[TypeNode]

@dataclass
class PrimitiveValueNode(ASTNode):
    primitive_type: str
    value: Any

@dataclass
class ScopeNode(ASTNode):
    identifier: str
    statements: List[StatementNode]

#
# Primitive Types
#
@dataclass
class StringPrimitiveValueNode(PrimitiveValueNode):
    value: str
    def __init__(self, value: str):
        super().__init__(primitive_type='string', value=value)
        self.value = value

@dataclass
class IntegerPrimitiveValueNode(PrimitiveValueNode):
    value: int
    def __init__(self, value: int):
        super().__init__(primitive_type='int', value=value)
        self.value = value

@dataclass
class FloatPrimitiveValueNode(PrimitiveValueNode):
    value: float
    def __init__(self, value: float):
        super().__init__(primitive_type='float', value=value)
        self.value = value

@dataclass
class BoolPrimitiveValueNode(PrimitiveValueNode):
    value: bool
    def __init__(self, value: bool):
        super().__init__(primitive_type='bool', value=value)
        self.value = value

#
# Expressions
#
@dataclass
class BinaryOperationNode(ExpressionNode):
    operator: QuadrupleOperation
    left_side: ExpressionNode
    right_side: ExpressionNode

@dataclass
class UnaryOperationNode(ExpressionNode):
    operator: QuadrupleOperation
    expression: ExpressionNode

@dataclass
class ReadVariableNode(ExpressionNode):
    identifier: str

@dataclass
class ValueNode(ExpressionNode):
    value: PrimitiveValueNode

# @dataclass
# class NonVoidFunctionCallNode(ExpressionNode):
#     identifier: str
#     arguments: List[ExpressionNode]

#
# Statements & Scopes
#
@dataclass
class DeclareVariableNode(StatementNode):
    identifier: str
    type: TypeNode

@dataclass
class AssignmentNode(StatementNode):
    identifier: str
    value: ExpressionNode

@dataclass
class FunctionScopeNode(ScopeNode):
    arguments: List[DeclareVariableNode]

@dataclass
class FunctionDeclarationNode(StatementNode):
    identifier: str
    type: Optional[TypeNode]
    parameters: List[DeclareVariableNode]
    body: FunctionScopeNode

@dataclass
class VoidFunctionCallNode(StatementNode):
    identifier: str
    arguments: List[ExpressionNode]

@dataclass
class PrintNode(StatementNode):
    arguments: List[ExpressionNode]

@dataclass
class IfConditionNode(StatementNode):
    condition: ExpressionNode
    body: ScopeNode
    else_body: Optional[ScopeNode]

@dataclass
class WhileCycleNode(StatementNode):
    condition: ExpressionNode
    body: ScopeNode

#
# Program Node
#
@dataclass
class ProgramNode(ASTNode):
    identifier: str
    global_vars: List[DeclareVariableNode]
    global_funcs: List[FunctionDeclarationNode]
    body: ScopeNode
