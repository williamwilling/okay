class Message:
    def __init__(self, type, field, expected=None):
        self.type = type
        self.field = field
        self.expected = expected