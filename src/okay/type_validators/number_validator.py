from decimal import Decimal
from ..message import Message

class NumberValidator:
    def __init__(self, field=None, min=None, max=None):
        self._min = min
        self._max = max

    def __call__(self, field, value):
        if not isinstance(value, (int, float, Decimal)):
            return Message(
                type='invalid_type',
                field=field,
                expected='number'
            )
        
        value = Decimal(value)
        
        if self._min and value < self._min:
            return Message(
                type='number_too_small',
                field=field,
                expected=self._min
            )
        
        if self._max and value > self._max:
            return Message(
                type='number_too_large',
                field=field,
                expected=self._max
            )