import math
from ..message import Message
from okay.type_validators import NumberValidator

class IntValidator:
    def __init__(self, field=None, **kwargs):
        self._validate_number = NumberValidator(**kwargs)

    def __call__(self, field, value, **kwargs):
        if not (isinstance(value, (int, float)) and value == int(value)):
            return Message(
                type='invalid_type',
                field=field,
                expected='int'
            )
        
        return self._validate_number(field, value, **kwargs)