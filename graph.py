from typing import Optional

from pygraphviz import AGraph

from little_duck import LittleDuckAnalyzer, LittleDuckLexer, LittleDuckParser
from little_duck.nodes import (
    ASTNode,
    DeclareVariableNode,
    ExpressionNode,
    FunctionDeclarationNode,
    PrimitiveValueNode,
    ProgramNode,
    ReadVariableNode,
    ScopeNode,
    StatementNode,
)


def graph_ast(
        node: ASTNode,
        graph: Optional[AGraph] = None,
        parent_id: Optional[str] = None,
        parent_label: Optional[str] = None):
    if graph is None:
        graph = AGraph(strict=True, directed=True)

    node_id = str(id(node))

    # Create a label for the node
    label = f'{node.__class__.__name__}'
    details = ''
    for field, value in node.__dict__.items():
        if isinstance(value, str):
            if len(value) > 0:
                details += f'\n{field}: {value}'
            else:
                details += f'\n{field}: ""'
    if details:
        label += '\n' + details

    if isinstance(node, (ProgramNode, ScopeNode)):
        color = '#a7aec4' # Blue
    elif isinstance(node, (DeclareVariableNode, FunctionDeclarationNode)):
        color = '#a7c3c4' # Cyan
    elif isinstance(node, StatementNode):
        color = '#b4c4a7' # Green
    elif isinstance(node, ReadVariableNode):
        color = '#e5c5a4' # Orange
    elif isinstance(node, PrimitiveValueNode):
        color = '#f1efa3' # Yellow
    elif isinstance(node, ExpressionNode):
        color = '#c67b78' # Red
    else:
        color = '#bea7c4' # Purple

    # Add the node with the label and style
    graph.add_node(node_id, label=label, color='#0000001A', fontname='Graphik', fontcolor='#000000A8', shape='box', style='filled', fillcolor=color)

    # If there's a parent, add an edge from parent to this node
    if parent_id is not None:
        graph.add_edge(parent_id, node_id, fontname='Graphik', label=parent_label, color='#333333', fontcolor='#333333')

    # Recursively handle fields that are also ASTNodes or lists of ASTNodes
    for field, value in node.__dict__.items():
        if isinstance(value, ASTNode):
            graph_ast(value, graph, node_id, field)
        elif isinstance(value, list) and value and isinstance(value[0], ASTNode):
            for item in value:
                graph_ast(item, graph, node_id, field[:-1])

    return graph

def draw_graph(node: ProgramNode, name: str):
    # Generate graph from AST
    graph = graph_ast(node)
    # Layout using dot engine, better for hierarchical structures like ASTs
    graph.layout(prog='dot')
    # graph.draw(name + '.png')  # Save as PNG
    graph.draw(name + '.pdf')  # Save as PDF for high-quality output

#
# Graph the AST
#
if __name__ == "__main__":
    # Build the lexer
    lexer = LittleDuckLexer()
    parser = LittleDuckParser()
    analyzer = LittleDuckAnalyzer()

    file_contents = ""
    with open('code.ld', 'r') as file:
        file_contents = file.read()

    # Generate the graphs
    tree = parser.parse(file_contents, lexer=lexer)
    draw_graph(tree, name="ast_parsed")

    analyzer.analyze(tree) # Tree will get updated during analysis
    draw_graph(tree, name="ast_analyzed")
