from ..message import Message

class ObjectValidator:
    def __init__(self, field=None):
        pass
    
    def __call__(self, field, value):
        if not isinstance(value, dict):
            return Message(
                type='invalid_type',
                field=field,
                expected={
                    'type': 'object'
                }
            )