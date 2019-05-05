class Message:
    def __init__(self, type, field, expected=None):
        self.type = type
        self.field = field
        self.expected = expected

class Validator:
    def __init__(self, schema):
        self._schema = schema
        self._specified_fields = set()
        self.messages = []
    
    def validate(self, document):
        if not isinstance(document, dict):
            raise TypeError('Document must be dictionary.')
        
        self._document = document
        self._schema(self)
        self._report_extra_fields()

        return len(self.messages) == 0
    
    def required(self, field, document=None, prefix=''):
        document = document or self._document

        if '.' in field:
            head, tail = field.split('.', 1)
            self._specified_fields.add(head)

            if head in document:
                if isinstance(document[head], dict):
                    prefix = f'{prefix}{head}.'
                    return self.required(tail, document[head], prefix)
                else:
                    self.messages.append(Message(
                        type='incorrect_type',
                        field=f'{prefix}{head}',
                        expected='object'
                    ))
            else:
                return

        self._specified_fields.add(field)

        if field not in document:
            self.messages.append(Message(
                type='missing_field',
                field=f'{prefix}{field}'
            ))
    
    def optional(self, field):
        self._specified_fields.add(field)
    
    def ignore_extra_fields(self):
        for field in self._document.keys():
            self._specified_fields.add(field)
    
    def _report_extra_fields(self):
        for field in self._document.keys():
            if field not in self._specified_fields:
                self.messages.append(Message(
                    type='extra_field',
                    field=field
                ))