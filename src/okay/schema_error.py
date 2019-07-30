class SchemaError(Exception):
    def __init__(self, message, type=None, field=None):
        super(SchemaError, self).__init__(message)
        self.type = type
        self.field = field
