import re
from ..message import Message

class StringValidator:
    def __init__(self, field=None, regex=None, options=None, case_sensitive=True, min=None, max=None):
        self._pattern = regex
        self._regex = re.compile(self._pattern) if self._pattern is not None else None
        
        self._options = options
        self._case_sensitive = case_sensitive
        if self._options:
            if not self._case_sensitive:
                self._options = [ option.lower() for option in self._options ]
        
        self._min = min
        self._max = max
    
    def __call__(self, field, value, **kwargs):
        if not isinstance(value, str):
            return Message(
                type='invalid_type',
                field=field,
                expected='string'
            )
        
        expected = {
            'case_sensitive': self._case_sensitive if self._options is not None else None,
            'max': self._max,
            'min': self._min,
            'options': self._options,
            'regex': self._pattern
        }
        
        pass_regex = self._regex.fullmatch(value) if self._regex is not None else False
        pass_minimum = len(value) >= self._min if self._min is not None else False
        pass_maximum = len(value) <= self._max if self._max is not None else False
        pass_options = (value in self._options) or (not self._case_sensitive and value.lower() in self._options) if self._options is not None else False

        if pass_regex or pass_options or (pass_minimum and pass_maximum):
            return

        if self._regex is not None and not pass_regex:
            return Message(
                type='no_match',
                field=field,
                expected=expected
            )

        if self._min is not None and not pass_minimum:
            return Message(
                type='string_too_short',
                field=field,
                expected=expected
            )
        
        if self._max is not None and not pass_maximum:
            return Message(
                type='string_too_long',
                field=field,
                expected=expected
            )
        
        if self._options is not None and not pass_options:
            return Message(
                type='invalid_string_option',
                field=field,
                expected=expected
            )
        
        # If we reach this point, the validator didn't receive any parameters, so we only need to
        # validate the type, and we already did that at the beginning of this function. In other
        # words, everything is fine.
        return