from ..message import Message

class ListValidator:
    def __init__(self, field=None, min=None, max=None):
        self._min = min
        self._max = max

    def __call__(self, field, value):
        if not isinstance(value, list):
            return Message(
                type='invalid_type',
                field=field,
                expected='list'
            )
        
        if self._min and len(value) < self._min:
            return Message(
                type='too_few_elements',
                field=field,
                expected=self._min
            )
        
        if self._max and len(value) > self._max:
            return Message(
                type='too_many_elements',
                field=field,
                expected=self._max
            )