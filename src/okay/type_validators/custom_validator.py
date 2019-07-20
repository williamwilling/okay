from ..message import Message
from ..schema_error import SchemaError

def validate_custom(field, value, validator):
    if not callable(validator):
        raise SchemaError(f"Custom validation function specified for field '{field}' is not callable.")

    try:
        message = validator(field, value)
    except Exception as e:
        raise SchemaError(f"Custom validation function `{validator.__name__}()` specified for field '{field}' raised exception `{type(e).__name__}`.") from e

    if not (message is None or isinstance(message, Message)):
        raise SchemaError(f"Custom validation function `{validator.__name__}()` specified for field '{field}' must return a `Message` object, but it returned a `{type(message).__name__}` object instead.")

    return message