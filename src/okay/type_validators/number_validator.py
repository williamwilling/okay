from decimal import Decimal
from ..message import Message

class NumberValidator:
    def __init__(self, field=None, min=None, max=None, options=None):
        self._min = min
        self._max = max
        self._options = options

    def __call__(self, field, value):
        if not isinstance(value, (int, float, Decimal)):
            return Message(
                type='invalid_type',
                field=field,
                expected={
                    'type': 'number'
                }
            )
        
        value = Decimal(value)
        expected = {
            'min': self._min,
            'max': self._max,
            'options': self._options
        }

        pass_minimum = value >= self._min if self._min is not None else self._max is not None
        pass_maximum = value <= self._max if self._max is not None else self._min is not None
        pass_options = value in self._options if self._options is not None else False

        if pass_options or (pass_minimum and pass_maximum):
            return
        
        if self._min is not None and not pass_minimum:
            return Message(
                type='number_too_small',
                field=field,
                expected=expected
            )
        
        if self._max is not None and not pass_maximum:
            return Message(
                type='number_too_large',
                field=field,
                expected=expected
            )
        
        if self._options is not None and not pass_options:
            return Message(
                type='invalid_number_option',
                field=field,
                expected=expected
            )