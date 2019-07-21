import re
from ..message import Message

def validate_string(field, value, **kwargs):
    if not isinstance(value, str):
        return Message(
            type='invalid_type',
            field=field,
            expected='string'
        )
    pattern = kwargs.get('regex')
    options = kwargs.get('options')

    if pattern and options:
        if value in options or re.fullmatch(pattern, value):
            return
        else:
            return Message(
                type='no_match',
                field=field,
                expected={
                    'regex': pattern,
                    'options': options
                }
            )

    if pattern and not re.fullmatch(pattern, value):
            return Message(
            type='no_match',
            field=field,
            expected=pattern
        )
    
    if options and value not in options:
        return Message(
            type='invalid_option',
            field=field,
            expected=options
        )