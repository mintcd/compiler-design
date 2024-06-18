from typing import Tuple, List
from utils.structures.CFG import CFG
from utils.structures.SymbolTable import SymbolTable
from utils.structures.AST import Void

class Node:
  def __init__(self, symbol, degree = 0, avail = True, reg = None):
    self.symbol = symbol 
    self.degree = degree
    self.avail = True
    self.reg = reg
  
  def __str__(self):
    return f"({self.name}, {self.degree}, {self.avail}, {self.reg})"

  def __repr__(self):
    return f"({self.name}, {self.reg})"

class Edge:
  def __init__(self, nodes : Tuple[Node, Node], avail = True):
    self.nodes = nodes
  
  def __str__(self):
    return f"({self.nodes[0].name}, {self.nodes[1].name})"

class RIG:
  def __init__(self, cfg : CFG, st : SymbolTable, log_file = None):
    self.cfg = cfg
    self.st = st
    self.log_file = log_file

    self.nodes : List[Node] = []
    self.edges : List[Edge] = []

    self.num_node = 0
  
  def __str__(self):
    return (f"Nodes: [{', '.join(str(node) for node in self.nodes)}]\n"
            f"Edges: [{', '.join(str(edge) for edge in self.edges)}]\n")

  def build(self):

    live = {
      stmt.id : stmt.live_symbols
      for stmt in self.cfg.get_stmts()
    }

    for stmt_id in list(live.keys()):
      for i in range(len(live[stmt_id])):
        self.nodes.append(Node(live[stmt_id][i]))

    for stmt_id in list(live.keys()):
      for i in range(0, len(live[stmt_id])):
        for j in range(i+1, len(live[stmt_id])):
          self.edges.append(Edge((self.nodes[i], self.nodes[j])))

    for node in self.nodes:
      for edge in self.edges:
        if node in edge.nodes:
          node.degree += 1

    self.nodes = sorted(self.nodes, key=lambda x: x.degree)
    self.num_node = len(self.nodes)

    return self

  def get_neighbors(self, node):
    neighs = list()
    for edge in self.edges:
      if node == edge.nodes[0]:
        neighs.append(edge.nodes[1])
      if node == edge.nodes[1]:
        neighs.append(edge.nodes[0])

    return neighs

  def add_node(self, node):
    node.avail = True
    for edge in self.edges:
      if node in edge.nodes:
        edge.avail = True 

  def pop_node(self):
    self.num_node -= 1
    self.nodes[self.num_node].avail = False

    for edge in self.edges:
      if edge.nodes[0] == self.nodes[self.num_node]:
        edge.nodes[1].degree -= 1
        edge.avail = False
      if edge.nodes[1] == self.nodes[self.num_node]:
        edge.nodes[0].degree -= 1
        edge.avail = False

    return self.nodes[self.num_node]
