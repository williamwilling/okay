from ..message import Message

def validate_bool(field, value):
    if not isinstance(value, bool):
        return Message(
            type='invalid_type',
            field=field,
            expected='boolean'
        )