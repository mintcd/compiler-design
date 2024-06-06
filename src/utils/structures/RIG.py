from typing import Tuple, List

class Node:
  def __init__(self, name, degree = 0, avail = True, reg = None):
    self.name = name
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
  def __init__(self, live : dict):
    self.live = live
    self.num_node = 0
    self.nodes : List[Node] = []
    self.edges : List[Edge] = []
  
  def __str__(self):
    return (f"Nodes: [{', '.join(str(node) for node in self.nodes)}]\n"
            f"Edges: [{', '.join(str(edge) for edge in self.edges)}]\n")

  def build(self):
    for stmt_id in list(self.live.keys()):
      for i in range(len(self.live[stmt_id])):
        self.nodes.append(Node(self.live[stmt_id][i]))

    for stmt_id in list(self.live.keys()):
      for i in range(0, len(self.live[stmt_id])):
        for j in range(i+1, len(self.live[stmt_id])):
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
      if node.name == edge.nodes[0].name:
        neighs.append(edge.nodes[1])
      if node.name == edge.nodes[1].name:
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
