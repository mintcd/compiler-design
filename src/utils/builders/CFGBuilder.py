from utils.structures.AST import *
from utils.visitors import ASTVisitor
from utils.structures.CFG import *


class CFGContext:
    def __init__(self,  active_block: Block or None = None, 
                        loop_block: Block or None = None, 
                        endloop_block: Block or None = None,
                        func_block : Block or None = None,
                ):
        self.active_block = active_block
        self.loop_block = loop_block
        self.endloop_block = endloop_block
        self.func_block = func_block

class CFGData:
    def __init__(self, cfg : CFG, ctx : CFGContext):
        self.obj = cfg
        self.ctx = ctx

class CFGBuilder(ASTVisitor):
    def __init__(self, ast):
        self.ast = ast
 
    def build(self):
        # Create data
        data = CFGData(CFG(), CFGContext())

        # Visit
        cfg = self.visit(self.ast, data).obj

        # Remove all VarDecl since ST has been build
        for block in cfg.blocks:
            if isinstance(block, Block):
                block.stmts = [stmt for stmt in block.stmts if not isinstance(stmt, VarDecl)]    

        # Assign a unique ID to each statement
        for block in cfg.blocks:
            if isinstance(block, Block):
                for i in range(len(block.stmts)):
                    block.stmts[i].id = (block.id, i)
            else:
                block.cond.id = (block.id, 0)

        return cfg
    
    def visitProgram(self, ast : Program, data : CFGData):
        cfg = data.obj
        ctx = data.ctx

        # Create global block and set active
        global_block = Block(cfg.get_avail_block_id(), "0")
        cfg.blocks.append(global_block)
        ctx.active_block = global_block

        for decl in ast.decls:
            data = self.visit(decl, data)

        # Next block of the global block is the main
        ctx.active_block.next = cfg.get_block_by_name("0_main")

        return data
    
    def visitFuncDecl(self, ast : FuncDecl, data : CFGData):
        cfg = data.obj
        ctx = data.ctx

        global_block = ctx.active_block

        # Create funcblock and set it active
        func_block = Block(cfg.get_avail_block_id(), f"0_{ast.name}")
        ctx.active_block = func_block
        cfg.blocks.append(func_block)

        # Visit function body and point func_block.end to the last active block
        data = self.visit(ast.body, data)
        func_block.end = ctx.active_block

        # Retent ctx
        ctx.active_block = global_block
        ctx.func_block = None

        return data
    
    def visitVarDecl(self, ast : VarDecl, data : CFGData):
        # Add this statement to active_block
        data.ctx.active_block.stmts.append(ast)
        return data

    def visitStmtBlock(self, ast : Block, data : CFGData):
        for stmt in ast.stmts:
            data = self.visit(stmt, data)

        return data

    def visitAssignStmt(self, ast : AssignStmt, data : CFGData):
        # Take care of FuncCall, else add the statement to active_block
        if isinstance(ast.rhs, FuncCall):
            data = self.visit(ast.rhs)
        data.ctx.active_block.stmts.append(ast)
        return data

    def visitIfStmt(self, ast : IfStmt, data : CFGData):
        cfg = data.obj
        ctx = data.ctx

        # Add condition block
        cond_block = Block(cfg.get_avail_block_id(), "cond", ast.cond)
        cfg.blocks.append(cond_block)
        ctx.active_block.next = cond_block

        last_true_active_block = None
        last_false_active_block = None

        # Add true block and visit it
        true_block = Block(cfg.get_avail_block_id(), "true_branch")
        cfg.blocks.append(true_block)
        cond_block.true = true_block
        ctx.active_block = true_block
        data = self.visit(ast.tstmt, data)
        last_true_active_block = ctx.active_block

        # Add false block if there is and visit it
        if ast.fstmt is not None:
            false_block = Block(cfg.get_avail_block_id(), "false_branch")
            cfg.blocks.append(false_block)
            cond_block.false = false_block
            ctx.active_block = false_block
            data = self.visit(ast.fstmt, data)
            last_false_active_block = ctx.active_block

        # Create endif_block
        end_block = Block(cfg.get_avail_block_id(), "endif")
        cfg.blocks.append(end_block)

        last_true_active_block.next = end_block
        if last_false_active_block is not None: 
            last_false_active_block.next = end_block
        else: 
            cond_block.false = end_block

        ctx.active_block = end_block

        return data

    def visitWhileStmt(self, ast : WhileStmt, data : CFGData):
        cfg = data.obj
        ctx = data.ctx

        # Create cond, loop and endloop
        cond_block = Block(cfg.get_avail_block_id(), "cond", ast.cond)
        loop_block = Block(cfg.get_avail_block_id(), "loop")
        endloop_block = Block(cfg.get_avail_block_id(), "endloop")

        cfg.blocks.append(cond_block)
        cfg.blocks.append(loop_block)
        cfg.blocks.append(endloop_block)
       
        ctx.active_block.next = cond_block
        cond_block.true = loop_block
        cond_block.false = endloop_block

        # Set the context
        ctx.active_block = loop_block
        ctx.loop_block = loop_block
        ctx.endloop_block = endloop_block
        
        # Visit the statement
        data = self.visit(ast.stmt, data)
        ctx.active_block.next = cond_block

        # Retend ctx
        ctx.loop_block = None
        ctx.endloop_block = None

        return data

    def visitDoWhileStmt(self, ast: DoWhileStmt, data: CFGData):
        cfg = data.obj
        ctx = data.ctx

        # Create loop, cond and endloop
        loop_block = Block(cfg.get_avail_block_id(), "loop")
        cond_block = Block(cfg.get_avail_block_id(), "cond", ast.cond)
        endloop_block = Block(cfg.get_avail_block_id(), "endloop")

        cfg.blocks.append(loop_block)
        cfg.blocks.append(cond_block)
        cfg.blocks.append(endloop_block)
       
        ctx.active_block.next = loop_block
        cond_block.true = loop_block
        cond_block.false = endloop_block

        # Set the context
        ctx.active_block = loop_block
        ctx.loop_block = loop_block
        ctx.endloop_block = endloop_block
        
        # Visit the statement
        data = self.visit(ast.stmt, data)
        ctx.active_block.next = cond_block

        # Retend ctx
        ctx.loop_block = None
        ctx.endloop_block = None

        return data        
    
    def visitForStmt(self, ast: ForStmt, data: CFGData):
        cfg = data.obj
        ctx = data.ctx

        # Add init to active block
        ctx.active_block.stmts.append(ast.init)

        # Add upd to ast.stmt
        ast.stmt.stmts.append(ast.upd)

        return self.visit(WhileStmt(ast.cond, ast.stmt))


    def visitCallStmt(self, ast : FuncCall, data : CFGData):
        cfg = data.obj
        ctx = data.ctx

        ctx.active_block.jump = cfg.find_func_block(ast.name)

        link_block = Block(cfg.get_avail_block_id(), f"{ast.name}_link")
        cfg.append_block(link_block)
        ctx.active_block.jump = link_block

        return data
        

    def visitFuncCall(self, ast : FuncCall, data : CFGData):
        cfg = data.obj
        ctx = data.ctx

        ctx.active_block.jump = cfg.find_func_block(ast.name)

        link_block = Block(cfg.get_avail_block_id(), f"{ast.name}_link")
        cfg.append_block(link_block)
        ctx.active_block.jump = link_block

        return data
        
    def visitReturnStmt(self, ast : ReturnStmt, data : CFGData):
        data.ctx.active_block.next = func_block

        return data

    def visitBreakStmt(self, ast : BreakStmt, data : CFGData):
        cfg = data.obj
        ctx = data.ctx

        ctx.active_block.next = ctx.endloop_block

        return data

    def visitContinueStmt(self, ast : ContinueStmt, data : CFGData):
        cfg = data.obj
        ctx = data.ctx

        ctx.active_block.next = ctx.loop_block   

        return data   