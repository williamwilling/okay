class Message:
    def __init__(self, type, field):
        self.type = type
        self.field = field

class Validator:
    def __init__(self, schema):
        self._schema = schema
        self.messages = []
    
    def validate(self, document):
        if not isinstance(document, dict):
            raise TypeError('Document must be dictionary.')
        
        self._document = document
        self._schema(self)

        return len(self.messages) == 0
    
    def required(self, field):
        if not field in self._document:
            self.messages.append(Message(
                type='missing_field',
                field=field
            ))