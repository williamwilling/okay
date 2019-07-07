import math
from ..message import Message
from okay.type_validators import validate_number

def validate_int(field, value, **kwargs):
    if not (isinstance(value, (int, float)) and value == int(value)):
        return Message(
            type='invalid_type',
            field=field,
            expected='int'
        )
    
    return validate_number(field, value, **kwargs)