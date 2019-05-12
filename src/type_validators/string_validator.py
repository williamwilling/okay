import re
from message import Message

def validate_string(field, value, **kwargs):
    if not isinstance(value, str):
        return Message(
            type='invalid_type',
            field=field,
            expected='string'
        )
    
    pattern = kwargs.get('regex')
    if pattern and re.fullmatch(pattern, value) is None:
        return Message(
            type='no_match',
            field=field,
            expected=pattern
        )
    
    options = kwargs.get('options')
    if options and value not in options:
        return Message(
            type='invalid_option',
            field=field,
            expected=options
        )