
class ModelView:
    def __init__(self,model_class):
        self.model_class = model_class
        self.title = self.model_class.__class__.__name__

class ClassView(ModelView):
    def __str__(self):
        return self.title

class ObjectView(ModelView):
    def __str__(self):
        return self.title
        


