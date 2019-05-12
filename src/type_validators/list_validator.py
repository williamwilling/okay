from message import Message

def validate_list(field, value, **kwargs):
    if not isinstance(value, list):
        return Message(
            type='invalid_type',
            field=field,
            expected='list'
        )
    
    min = kwargs.get('min')
    if min and len(value) < min:
        return Message(
            type='too_few_elements',
            field=field,
            expected=min
        )
    
    max = kwargs.get('max')
    if max and len(value) > max:
        return Message(
            type='too_many_elements',
            field=field,
            expected=max
        )