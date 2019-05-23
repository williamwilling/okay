class Message:
    def __init__(self, type, field=None, document_number=None, expected=None, extra=None):
        self.type = type
        self.field = field
        self.expected = expected
        self.document_number = document_number
        self.extra = extra
        