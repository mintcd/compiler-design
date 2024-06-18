from utils.APIs import generate_liveness
from utils.structures.RIG import RIG
from utils.structures.SymbolTable import SymbolTable

class RegisterAllocator:
    def __init__(self, cfg, st, num_reg: int, log_file = None):
        self.num_reg = num_reg
        self.st = st
        self.log_file = log_file
        
        self.cfg = generate_liveness(cfg, st, log_file)

        self.rig = RIG(self.cfg, self.st, self.log_file).build()

    def __str__(self):
        nodes_str = ", ".join(f"({node}, {self.nodes[node]['reg']})" for node in self.nodes)
        return f"Nodes: {nodes_str}"

    def allocate(self) -> SymbolTable:
        self.heuristic_optimize()
        if self.log_file is not None:
            with open(self.log_file, 'a') as file:
                file.write("Allocated symbols\n")
                file.write(f"{str(self.st)}\n\n")
                file.write("--------------------------------------------------------\n\n")

        return self.st

    def heuristic_optimize(self):
        stack = []
    
        for i in range(len(self.rig.nodes)): 
            pop_node = self.rig.pop_node()

            if pop_node.degree <= self.num_reg:
                stack.append(pop_node)
            else: 
                pop_node.symbol.register = "spill"

        while len(stack) > 0:
            used_regs = list()
            added_node = stack.pop()
            self.rig.add_node(added_node)
            self._node_allocate(added_node)

    def _node_allocate(self, node):
        excluded = set()
        for neigh in self.rig.get_neighbors(node):
            if neigh.symbol.register is not None:
                excluded.add(neigh.symbol.register)

        node.symbol.register = list(set(range(self.num_reg))-excluded)[0]




