from ..message import Message
from ..schema_error import SchemaError

class CustomValidator:
    def __init__(self, field, **kwargs):
        if not 'validator' in kwargs:
            raise SchemaError(f"No custom validation function specified for field '{field}'.")

        validator = kwargs['validator']
        if not callable(validator):
            raise SchemaError(f"Custom validation function specified for field '{field}' is not callable.")
        
        self._validator = validator
        self._kwargs = kwargs
        del self._kwargs['validator']
    
    def __call__(self, field, value):
        try:
            message = self._validator(field, value, **self._kwargs)
        except Exception as e:
            raise SchemaError(f"Custom validation function `{self._validator.__name__}()` specified for field '{field}' raised exception `{type(e).__name__}`.") from e

        if not (message is None or isinstance(message, Message)):
            raise SchemaError(f"Custom validation function `{self._validator.__name__}()` specified for field '{field}' must return a `Message` object, but it returned a `{type(message).__name__}` object instead.")

        return message