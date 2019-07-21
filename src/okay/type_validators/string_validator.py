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
    case_sensitive = kwargs.get('case_sensitive', True)

    if case_sensitive:
        in_options = options and value in options
    else:
        in_options = options and value.lower() in [ option.lower() for option in options ]

    if pattern and options:
        if in_options or re.fullmatch(pattern, value):
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
    
    if options and not in_options:
        return Message(
            type='invalid_option',
            field=field,
            expected=options
        )