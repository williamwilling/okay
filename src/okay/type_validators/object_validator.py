from ..message import Message

def validate_object(field, value):
    if not isinstance(value, dict):
        return Message(
            type='invalid_type',
            field=field,
            expected='object'
        )