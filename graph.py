from pygraphviz import AGraph
from typing import Optional
from little_duck import LittleDuckLexer, LittleDuckParser
from little_duck.nodes import ASTNode, DeclareVariableNode, ExpressionNode, FunctionDeclarationNode, PrimitiveValueNode, ProgramNode, ReadVariableNode, ScopeNode, StatementNode

def graph_ast(
        node: ASTNode,
        graph: Optional[AGraph] = None,
        parent: Optional[str] = None,
        parent_label: Optional[str] = None):
    if graph is None:
        graph = AGraph(strict=True, directed=True)

    node_id = str(id(node))
    # Create a simplified label for the node
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

    color = '#bea7c4'
    if isinstance(node, StatementNode):
        color = '#b4c4a7'
    elif isinstance(node, ReadVariableNode):
        color = '#e5c5a4'
    elif isinstance(node, PrimitiveValueNode):
        color = '#f1efa3'
    elif isinstance(node, ExpressionNode):
        color = '#c67b78'
    elif isinstance(node, (ProgramNode ,ScopeNode, DeclareVariableNode, FunctionDeclarationNode)):
        color = '#a7aec4'

    # Add the node with the label and style
    graph.add_node(node_id, label=label, color='#0000001A', fontname='Graphik', fontcolor='#000000A8', shape='box', style='filled', fillcolor=color)

    # If there's a parent, add an edge from parent to this node
    if parent is not None:
        graph.add_edge(parent, node_id, fontname='Graphik', label=parent_label)

    # Recursively handle fields that are also ASTNodes or lists of ASTNodes
    for field, value in node.__dict__.items():
        if isinstance(value, ASTNode):
            graph_ast(value, graph, node_id, field)
        elif isinstance(value, list) and value and isinstance(value[0], ASTNode):
            for item in value:
                graph_ast(item, graph, node_id, field[:-1])

    return graph

def draw_graph(graph):
    # Layout using dot engine, better for hierarchical structures like ASTs
    graph.layout(prog='dot')
    # graph.draw('ast_graph.png')  # Save as PNG
    graph.draw('ast_graph.pdf')  # Save as PDF for high-quality output

#
# Graph the AST
#
if __name__ == "__main__":
    # Build the lexer
    lexer = LittleDuckLexer()
    parser = LittleDuckParser()

    file_contents = ""
    with open('code.ld', 'r') as file:
        file_contents = file.read()

    tree = parser.parse(file_contents, lexer=lexer)
    print(tree)

    # Generate the graph
    draw_graph(graph_ast(tree))
