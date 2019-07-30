class Message:
    def __init__(self, type, **kwargs):
        self.type = type
        self.add(**kwargs)
        
    def add(self, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value
    
    def __repr__(self):
        return self.type + ': ' + self.field