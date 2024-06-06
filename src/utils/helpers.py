from utils.structures.AST import IntegerType, FloatType, StringType, BooleanType

def type_inference(typ1, typ2):
  if typ1 is None:
     return typ2
  if typ2 is None:
     return typ1

  if isinstance(typ1, FloatType) or isinstance(typ2, FloatType):
    return FloatType()
  return typ1