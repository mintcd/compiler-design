from phases.code_generation.LivenessGenerator import LivenessGenerator
from utils.structures.RIG import RIG

class RegisterAllocator:
    def __init__(self, cfg, st, num_reg: int, log_file = None):
        self.num_reg = num_reg
        self.st = st
        
        live = LivenessGenerator(cfg, st, log_file).generate()
        self.rig = RIG(live).build()
        with open(log_file, 'a') as file:
            file.write("Live symbols after each statement:\n")
            file.write("{\n\t")
            file.write(",\n\t".join((str(stmt) + ": " + str(sym)) for stmt, sym in live.items()))
            file.write("\n}\n")
            file.write("----------------------------------------\n\n")

    def __str__(self):
        nodes_str = ", ".join(f"({node}, {self.nodes[node]['reg']})" for node in self.nodes)
        return f"Nodes: {nodes_str}"

    def allocate(self):
        self.heuristic_optimize()
        return {node.name : node.reg for node in self.rig.nodes}

    def heuristic_optimize(self):
        stack = []
        
        for i in range(len(self.rig.nodes)): 
            pop_node = self.rig.pop_node()

            if pop_node.degree <= self.num_reg:
                stack.append(pop_node)
            else: 
                pop_node.reg = "spill"

        while len(stack) > 0:
            used_regs = list()
            added_node = stack.pop()
            self.rig.add_node(added_node)
            self.node_allocate(added_node)

    def node_allocate(self, node):
        excluded = set()
        for neigh in self.rig.get_neighbors(node):
            if neigh.reg is not None:
                excluded.add(neigh.reg)

        node.reg = list(set(range(self.num_reg))-excluded)[0]




