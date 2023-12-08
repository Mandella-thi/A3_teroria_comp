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
    parser.add_option("-f", "--file")
    options, args = parser.parse_args(args)
    if options.file:
        with open(options.file) as instream:
            code = instream.read()
        label = options.file
  
    ast_codigo = ast.parse(code) #analisa com o pacote ast
    ast_transformado = transformar_ast(ast_codigo)
    expressoes_matematicas = extrair_expressoes_matematicas(code) #ACRESCENTADO
    results = {}
    try:
        for expr in expressoes_matematicas:
            result = eval(expr)
            
            results[expr] = result
            
    except SyntaxError:
        print("erro de sintaxe na expressão:", expr)
    except Exception as e:
        print("Erro semântico na expressão:", expr)
        print("Detalhes: ", str(e))

    ast_transformado['Expressoes_Matematicas'] = results #ACRESCENTADO
    renderer = GraphRenderer() #desenha o grafico de ast com o pacote graphviz
    renderer.render(ast_transformado, label=label)
    #ACRESCENTADO
def extrair_expressoes_matematicas(code):
    expr_matematicas = re.split(r';\s*', code)
    expressoes_validas = []
    for expr in expr_matematicas:
        # Verifica se a expressão é uma expressão matemática válida
        if re.match(r'\b\d+(\s*[\+\-\*\/]\s*\d+|\s*\(\s*\d+\s*[\+\-\*\/]\s*\d+\s*\))+\b', expr):
                try:
                    ast.parse(expr)
                    expressoes_validas.append(expr)
                except SyntaxError:
                    print("erro de sintaxe na expressão:", expr)
                except Exception as e:
                    print("Erro semântico na expressão:", expr)
                    print("Detalhes: ", str(e))
        
    return expressoes_validas

def transformar_ast(codigo_ast):#transforma recursivamente o codigo ast
    if isinstance(codigo_ast, ast.AST):
        node = {para_camelcase(k): transformar_ast(getattr(codigo_ast, k)) for k in codigo_ast._fields}
        node['tipo_node'] = para_camelcase(codigo_ast.__class__.__name__)
        return node
    elif isinstance(codigo_ast, list):
        return [transformar_ast(el) for el in codigo_ast]
    else:
        return codigo_ast


def para_camelcase(string):
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower()


class GraphRenderer:
    #clase que desenha a analise de ast, configuração de cores

    attrsgrafos = {
        'labelloc': 't',
        'fontcolor': 'white',
        'bgcolor': '#333333',
        'margin': '0',
    }

    attrsnos = {
        'color': 'white',
        'fontcolor': 'white',
        'style': 'filled',
        'fillcolor': '#006699',
    }

    attrbordas = {
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
        self._graph.node(node_id, label=node.get("tipo_node", "[dict]"))
        for key, value in node.items():
            if key == "tipo_node":
                continue
            child_node_id = self._render_node(value)
            self._graph.edge(node_id, child_node_id, label=self._escape_dot_label(key))


    def _render_list(self, node, node_id):
        self._graph.node(node_id, label="[list]")
        for idx, value in enumerate(node):
            child_node_id = self._render_node(value)
            self._graph.edge(node_id, child_node_id, label=self._escape_dot_label(str(idx)))

    
    def render(self, data, *, label=None):
        # cria o grafo
        graphattrs = self.attrsgrafos.copy()
        if label is not None:
            graphattrs['label'] = self._escape_dot_label(label)
        graph = gv.Digraph(graph_attr = graphattrs, node_attr = self.attrsnos, edge_attr = self.attrbordas)

        # desenha todos os nós e bordas recursivamente
        self._graph = graph
        self._rendered_nodes = set()
        self._render_node(data)
        self._graph = None
        self._rendered_nodes = None
        try:
            # mostra o grafo, abre o pdf automaticamente
            graph.format = "pdf"
            graph.view()
            subprocess.Popen(['xdg-open', "test.pdf"])
        except Exception as e:
                        e
    
    
if __name__ == '__main__':
    main(sys.argv)
