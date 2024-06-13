'''
  The interfaces to call elemental refactors.

  1) ASTRefactorer:
      VarDeclUnwrapper: unwrap VarDecl(x, typ, init) to [VarDecl(x, typ), Assign(x, init)]
      ScopeJustifier: Rename similar-name symbol with respect to the actual scope. Example: 
        {                         {
          x = 0;                    x_0 = 0;
          {                         {
            x = 1;       ---->        x_1 = 1;
          }                         }
        }                         }
      ForToWhile: Turn all ForStmt to WhileStmt
      BinExprUnwrapper: Unwrap complex binary expressions to single ones. Example:
      a = b + c + d      ---->    tmp_0 = b + c
                                  tmp_1 = tmp_0 + d
                                  a = tmp_1
  
  2) CFGRefactorer:
      EmptyBlockRemover
      LocalOptimizer
      GlobalOptimizer
'''

from optimization.ast_refactor.BinExprUnwrapper import BinExprUnwrapper
from optimization.ast_refactor.ScopeJustifier import ScopeJustifier
from optimization.ast_refactor.VarDeclUnwrapper import VarDeclUnwrapper
from optimization.ast_refactor.ForToWhile import ForToWhile
from optimization.ast_refactor.InforAssigner import InforAssigner

from optimization.cfg_refactor.EmptyBlockRemover import EmptyBlockRemover

class ASTRefactorer:
    def __init__(self, ast):
        self.ast = ast

    def refactor(self):
        ast = VarDeclUnwrapper(self.ast).unwrap()
        ast = ScopeJustifier(ast).justify()
        ast = ForToWhile(ast).refactor()
        ast = BinExprUnwrapper(ast).unwrap()
        ast = InforAssigner(ast).assign()
        return ast

class CFGRefactorer(CFGVisitor):
  def __init__(self, cfg : CFG):
    self.cfg = cfg

  def refactor(self):
    cfg = EmptyBlockRemover(self.cfg).remove()

    return cfg