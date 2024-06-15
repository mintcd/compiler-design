from copy import deepcopy
from utils.structures.AST import *

def infer_type(typ1, typ2):
  if typ1 is None:
     return typ2
  if typ2 is None:
     return typ1

  if isinstance(typ1, Float) or isinstance(typ2, Float):
    return Float()
  res = deepcopy(typ1)
  res.val = None	
  return res


def is_atomic(ast):
   if isinstance(ast, BinExpr) or isinstance(ast, UnExpr):
      return False
   return True