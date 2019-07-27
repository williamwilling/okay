from collections import namedtuple
from . import type_validators
from .index import Index
from .message import Message
from .schema_error import SchemaError

Field = namedtuple('Field', 'name value')

def validate(schema, document, message_values=None):
    if not isinstance(document, dict):
        raise TypeError('Document must be dictionary.')

    _validator._reset(document, message_values)
    try:
        schema()
    except SchemaError:
        raise
    except Exception as e:
        raise SchemaError(f"Schema raised `{type(e).__name__}`.") from e

    _validator._report_extra_fields(document)    

    message_values = message_values or {}
    for message in _validator.messages:
        message.add(**message_values)
    return _validator.messages


class Validator:
    def __init__(self):
        self._validated_fields = set()
        self._required_fields = set()
        self._optional_fields = set()
        self._index = Index()
        self.messages = []
    
    def _reset(self, document, message_values):
        self._document = document
        self._validated_fields.clear()
        self._required_fields.clear()
        self._optional_fields.clear()
        self._index.clear()
        self._ignore_extra_fields = False
        self.messages.clear()
    
    def required(self, field_name, type=None, **kwargs):
        if field_name.strip('[]') in self._optional_fields:
            raise SchemaError('Required field ' + field_name + ' has already been specified as optional.')
        else:
            self._required_fields.add(field_name.strip('[]'))

        index_entry = self._index.look_up(self._document, field_name)
        
        for name in index_entry.name_hierarchy:
            self._validated_fields.add(name)

        for field in index_entry.fields:
            if field.type == 'message':
                if field.message.type != 'missing_parent':
                    self.messages.append(field.message)

                continue

        self._validate(field_name, index_entry.fields, type, **kwargs)
    
    def optional(self, field_name, type=None, **kwargs):
        if field_name.strip('[]') in self._required_fields:
            raise SchemaError('Optional field ' + field_name + ' has already been specified as required.')
        else:
            self._optional_fields.add(field_name.strip('[]'))

        index_entry = self._index.look_up(self._document, field_name)
        
        for name in index_entry.name_hierarchy:
            self._validated_fields.add(name)

        for field in index_entry.fields:
            if field.type == 'message':
                if field.message.type == 'invalid_type':
                    self.messages.append(field.message)
                
                continue

        self._validate(field_name, index_entry.fields, type, **kwargs)
    
    def ignore_extra_fields(self):
        self._ignore_extra_fields = True
    
    def _validate(self, field_name, fields, type, **kwargs):
        if type is None:
            return
        
        validator_name = f'validate_{type}'
        try:
            type_validator = getattr(type_validators, validator_name)
        except AttributeError:
            raise SchemaError(f"Type `{type}` specified for field `{field_name}` is invalid.")
        
        for field in fields:
            if field.type == 'message':
                continue

            message = type_validator(field.full_name, field.value, **kwargs)
            if message is not None:
                self.messages.append(message)

    def _report_extra_fields(self, object, prefix='', indexed_prefix=''):
        if self._ignore_extra_fields:
            return

        if isinstance(object, dict):
            for key in object.keys():
                field_name = f'{prefix}{key}'
                if field_name not in self._validated_fields:
                    self.messages.append(Message(
                        type='extra_field',
                        field=f'{indexed_prefix}{key}'
                    ))
                else:
                    self._report_extra_fields(object[key], f'{prefix}{key}.', f'{indexed_prefix}{key}.')
        elif isinstance(object, list):
            for i, element in enumerate(object):
                self._report_extra_fields(element, f'{prefix[:-1]}[].', f'{indexed_prefix[:-1]}[{i}].')


_validator = Validator()