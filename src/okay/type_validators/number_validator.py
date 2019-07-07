from decimal import Decimal
from ..message import Message

def validate_number(field, value, **kwargs):
    if not isinstance(value, (int, float, Decimal)):
        return Message(
            type='invalid_type',
            field=field,
            expected='number'
        )
    
    value = Decimal(value)
    
    min = kwargs.get('min')
    if min and value < min:
        return Message(
            type='number_too_small',
            field=field,
            expected=min
        )
    
    max = kwargs.get('max')
    if max and value > max:
        return Message(
            type='number_too_large',
            field=field,
            expected=max
        )