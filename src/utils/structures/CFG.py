from utils.visitor_pattern import Visitee
from typing import List
from graphviz import Digraph
from utils.structures.AST import AssignStmt, Expr, Stmt

class Block(Visitee):
    def __init__(self, id, name = None,
                
                next = None,

                true = None,
                false = None,

                jump = None,
                link = None,  
                end = None,
                
                stmts : List[AssignStmt] or None  = None,
                cond: Expr or None = None):

        self.id = id
        self.name = name if name is not None else "normal"
        
        self.next = next
        self.true = true
        self.false = false
        self.jump = jump
        self.link = link
        self.end = end   # The final block of the function, exclusive to funcdecl block

        self.stmts = stmts if stmts is not None else []
        self.cond = cond if cond is not None else None
    
    def __repr__(self):
        print_succs = ""
        print_children = ""
        if self.cond is None:
            print_succs = f"next: {self.next.name}_{self.next.id}" if self.next is not None else f"next: None"
            print_children = "stmts: [\n\t" + "\n\t".join((str(stmt)) for stmt in self.stmts) + "\n]" if len(self.stmts) > 0 else "[]"
        else:
            print_succs = f"true: {self.true.name}_{self.true.id}, false: {self.false.name}_{self.false.id}"
            print_children = f"cond: {self.cond})"
        
        return f"Block(id: {self.id}, name: {self.name}, {print_succs}, {print_children}"
    
    def get_successors(self):
        succs = list()
        if self.next is not None: succs.append(self.next)
        if self.true is not None: succs.append(self.true)
        if self.false is not None: succs.append(self.false)
        if self.link is not None: succs.append(self.link)
        return succs
    
    def get_children(self):
        if self.cond is not None:
            return [self.cond]
        return self.stmts
    
    def get_first_child(self):
        children = self.get_children()
        if len(children) > 0: return children[0]
        return None

class CFG(Visitee):
    def __init__(self):
        self.blocks : List[Block] = []
        self.avail_id = 0

    def __repr__(self):
        return ",\n".join(str(block) for block in self.blocks)

    def visualize(self):
        dot = Digraph(comment='Control Flow Graph')
        
        for block in self.blocks:
            # Construct the label in multiple steps for better readability
            block_label = f"{block.name}_{block.id}"
            if isinstance(block, StmtBlock):
                block_label += "\n" + "\n".join(str(stmt) for stmt in block.stmts)
                # Add edges for next, true, and false connections
                if block.next:
                    dot.edge(str(block.id), str(block.next.id), label="next")
            else:
                block_label += "\n" + str(block.cond)
                if block.true:
                    dot.edge(str(block.id), str(block.true.id), label="true")
                if block.false:
                    dot.edge(str(block.id), str(block.false.id), label="false")
            
            # Add the node with the constructed label
            dot.node(str(block.id), block_label, shape='rect', labeljust='l', labelloc='t')            

        return dot

    def get_block_precessors(self, block : Block):
        pres = []
        for _block in self.get_blocks():
            if _block.get_successors() == block:
                pres.append(_block)
        return pres

    def get_block_by_id(self, _id):
        return [block for block in self.blocks if block.id == _id][0]

    def get_block_by_name(self, name):
        return [block for block in self.blocks if block.name == name][0]

    def get_symbols(self):
        syms = set()
        for block in self.blocks:
            if block.cond is None:
                for stmt in block.stmts:
                    syms.add(stmt.lhs.name)
        return list(syms)

    def get_stmts(self):
        res = list()
        for block in self.blocks:
            for stmt in block.get_children():
                res.append(stmt)
        return res

    def get_avail_block_id(self):
        self.avail_id += 1
        return self.avail_id - 1

    def find_func_block(self, name):
        for block in self.obj.blocks:
            if block.name == f"0_{name}":
                return block
        return None

    def get_successors(self, stmt : AssignStmt or Expr):
        res = []
        stmt_block = self.get_block_by_id(stmt.id[0])
        
        if stmt_block.cond is None:
            if stmt.id[1] < len(stmt_block.stmts) - 1:
                res.append(stmt_block.stmts[stmt.id[1] + 1])
            else:
                succ_blocks = stmt_block.get_successors()
                for succ_block in succ_blocks:
                    res.append(succ_block.get_first_child())
        else:
            succ_blocks = stmt_block.get_successors()
            for succ_block in succ_blocks:
                res.append(succ_block.get_first_child())
        return res

    def append_block(self, block : Block):
        self.blocks.append(block)

        return self