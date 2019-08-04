import re
from ..message import Message

class StringValidator:
    def __init__(self, field=None, regex=None, options=None, case_sensitive=True):
        self._pattern = regex
        if self._pattern:
            self._regex = re.compile(self._pattern)
        
        self._options = options
        self._case_sensitive = case_sensitive
        if self._options:
            if not self._case_sensitive:
                self._options = [ option.lower() for option in self._options ]
    
    def __call__(self, field, value, **kwargs):
        if not isinstance(value, str):
            return Message(
                type='invalid_type',
                field=field,
                expected='string'
            )

        if self._options:
            if self._case_sensitive:
                in_options = value in self._options
            else:
                in_options = value.lower() in self._options

        if self._pattern and self._options:
            if in_options or self._regex.fullmatch(value):
                return
            else:
                return Message(
                    type='no_match',
                    field=field,
                    expected={
                        'regex': self._pattern,
                        'options': self._options
                    }
                )

        if self._pattern and not self._regex.fullmatch(value):
            return Message(
                type='no_match',
                field=field,
                expected=self._pattern
            )
        
        if self._options and not in_options:
            return Message(
                type='invalid_option',
                field=field,
                expected=self._options
            )