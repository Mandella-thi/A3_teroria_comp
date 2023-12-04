#!/usr/bin/python3
import ast
import graphviz as gv
import subprocess
import numbers
import re
from uuid import uuid4 as uuid
import optparse
import sys

def main(args):#escolhe qual o tipo de entrada que o programa vai usar e usa as analises, programa principal
    parser = optparse.OptionParser(usage="astvisualizer.py [options] [string]")
    parser.add_option("-f", "--file", action="store",
                      help="Read a code snippet from the specified file")
    parser.add_option("-l", "--label", action="store",
                      help="The label for the visualization")

    options, args = parser.parse_args(args)
    if options.file:
        with open(options.file) as instream:
            code = instream.read()
        label = options.file
    elif len(args) == 2:
        code = args[1]
        label = "<code read from command line parameter>"
    else:
        print("Expecting Python code on stdin...")
        code = sys.stdin.read()
        label = "<code read from stdin>"
    if options.label:
        label = options.label

    code_ast = ast.parse(code) #analisa com o pacote ast
    transformed_ast = transform_ast(code_ast)
    math_expressions = extract_math_expressions(code) #ACRESCENTADO
    results = {}
    for expr in math_expressions:
        result = eval(expr)
        results[expr] = result
    
    transformed_ast['Math_Expressions'] = results #ACRESCENTADO
    renderer = GraphRenderer() #desenha o grafico de ast com o pacote graphviz
    renderer.render(transformed_ast, label=label)
    #ACRESCENTADO
def extract_math_expressions(code):
    math_expressions = re.split(r';\s*', code)
    valid_expressions = []
    for expr in math_expressions:
        # Verifica se a expressão é uma expressão matemática válida
        if re.match(r'\b\d+\s*[\+\-\*\/]\s*\d+\b', expr):
            valid_expressions.append(expr)
    return valid_expressions

def transform_ast(code_ast):#transforma recursivamente o codigo ast
    if isinstance(code_ast, ast.AST):
        node = {to_camelcase(k): transform_ast(getattr(code_ast, k)) for k in code_ast._fields}
        node['node_type'] = to_camelcase(code_ast.__class__.__name__)
        return node
    elif isinstance(code_ast, list):
        return [transform_ast(el) for el in code_ast]
    else:
        return code_ast


def to_camelcase(string):
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower()


class GraphRenderer:
    """
    this class is capable of rendering data structures consisting of
    dicts and lists as a graph using graphviz
    
    """
    #clase que desenha a analise de ast, configuração de cores

    graphattrs = {
        'labelloc': 't',
        'fontcolor': 'white',
        'bgcolor': '#333333',
        'margin': '0',
    }

    nodeattrs = {
        'color': 'white',
        'fontcolor': 'white',
        'style': 'filled',
        'fillcolor': '#006699',
    }

    edgeattrs = {
        'color': 'white',
        'fontcolor': 'white',
    }

    _graph = None
    _rendered_nodes = None


    @staticmethod
    def _escape_dot_label(str):
        return str.replace("\\", "\\\\").replace("|", "\\|").replace("<", "\\<").replace(">", "\\>")


    def _render_node(self, node):
        if isinstance(node, (str, numbers.Number)) or node is None:
            node_id = uuid()
        else:
            node_id = id(node)
        node_id = str(node_id)

        if node_id not in self._rendered_nodes:
            self._rendered_nodes.add(node_id)
            if isinstance(node, dict):
                self._render_dict(node, node_id)
            elif isinstance(node, list):
                self._render_list(node, node_id)
            else:
                self._graph.node(node_id, label=self._escape_dot_label(str(node)))

        return node_id


    def _render_dict(self, node, node_id):
        self._graph.node(node_id, label=node.get("node_type", "[dict]"))
        for key, value in node.items():
            if key == "node_type":
                continue
            child_node_id = self._render_node(value)
            self._graph.edge(node_id, child_node_id, label=self._escape_dot_label(key))


    def _render_list(self, node, node_id):
        self._graph.node(node_id, label="[list]")
        for idx, value in enumerate(node):
            child_node_id = self._render_node(value)
            self._graph.edge(node_id, child_node_id, label=self._escape_dot_label(str(idx)))


    def render(self, data, *, label=None):
        # create the graph
        graphattrs = self.graphattrs.copy()
        if label is not None:
            graphattrs['label'] = self._escape_dot_label(label)
        graph = gv.Digraph(graph_attr = graphattrs, node_attr = self.nodeattrs, edge_attr = self.edgeattrs)

        # recursively draw all the nodes and edges
        self._graph = graph
        self._rendered_nodes = set()
        self._render_node(data)
        self._graph = None
        self._rendered_nodes = None

        # mostra o grapho, abre o pdf automaticamente
        graph.format = "pdf"
        graph.view()
        subprocess.Popen(['xdg-open', "test.pdf"])
    
if __name__ == '__main__':
    main(sys.argv)
