import pygraphviz as pyv
from utils.consts_global import *


class Graph:
    __graph = None

    def __init__(self, directed=True):
        self.__graph = pyv.AGraph(directed=directed, strict=True, rankdir='LR')

    def add_edges(self, edges, edge_type=DEFAULT):
        for from_node, to_nodes in edges.iteritems():
            for to_node in to_nodes:
                if edge_type == NATIVE_EDGE:  # draw sys_app in rectangle
                    self.__graph.add_node(to_node, shape='box')
                self.__graph.add_edge(from_node, to_node, color=edge_type)

    def draw(self, output):
        self.__graph.layout(prog='dot')
        self.__graph.draw(output, format='jpg')
