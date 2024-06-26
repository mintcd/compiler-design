class Data:
    def __init__(self, obj, ctx):
        self.obj = obj
        self.ctx = ctx

class Visitee:
    def accept(self, visitor, data : Data):
        method_name = 'visit{}'.format(self.__class__.__name__)
        visit_function = getattr(visitor, method_name)
        return visit_function(self, data)

class Visitor:
    def visit(self, visitee, data : Data) ->  Data:
        return visitee.accept(self, data)