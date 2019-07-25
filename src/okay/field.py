class Field:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.type = self._typeof(value)
    
    def _typeof(self, value):
        if isinstance(value, dict):
            return 'object'
        elif isinstance(value, list):
            return 'list'
        
        return 'scalar'