from ..message import Message

class BoolValidator:
    def __init__(self, field=None, **kwargs):
        pass

    def __call__(self, field, value):
        if not isinstance(value, bool):
            return Message(
                type='invalid_type',
                field=field,
                expected='bool'
            )