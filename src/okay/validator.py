from . import type_validators
from .index import create_index
from .message import Message
from .schema_compiler import compile, required, optional
from .schema_error import SchemaError

def validate(schema, document, message_values=None):
    if not isinstance(document, dict):
        raise TypeError('Document must be dictionary.')

    _validator._reset(document, message_values)
    _validator._preprocessing = True
    try:
        compiled_schema = compile(schema)
    except Exception as e:
        raise SchemaError(f"Schema raised `{type(e).__name__}`.") from e
        
    _validator._index = create_index(document, compiled_schema.fields.keys())

    _validator._preprocessing = False
    try:
        schema()
    except SchemaError:
        raise
    except Exception as e:
        raise SchemaError(f"Schema raised `{type(e).__name__}`.") from e

    _validator._report_missing_fields(compiled_schema)
    _validator._report_extra_fields()  

    message_values = message_values or {}
    for message in _validator.messages:
        message.add(**message_values)
    return _validator.messages


class Validator:
    def __init__(self):
        self.messages = []
    
    def _reset(self, document, message_values):
        self._document = document
        self._ignore_extra_fields = False
        self.messages.clear()
    
    def required(self, field_name, type=None, **kwargs):
        if self._preprocessing:
            required(field_name, type, **kwargs)    # schema_compiler.required
            return
        
        if field_name in self._index.fields:
            self._validate(field_name, self._index.fields[field_name], type, **kwargs)
    
    def optional(self, field_name, type=None, **kwargs):
        if self._preprocessing:
            optional(field_name, type, **kwargs)    # schema_compiler.optional
            return
        
        if field_name in self._index.fields:
            self._validate(field_name, self._index.fields[field_name], type, **kwargs)

    def ignore_extra_fields(self):
        self._ignore_extra_fields = True
    
    def _report_extra_fields(self):
        if self._ignore_extra_fields:
            return

        for extra_field in self._index.extra_fields:
            self.messages.append(Message(
                type='extra_field',
                field=extra_field
            ))
    
    def _report_missing_fields(self, compiled_schema):
        for field_name, field in compiled_schema.fields.items():
            if '.' not in field_name:
                base_field_name = field_name.strip('[]')
                if field.strictness == 'required' and base_field_name not in self._document:
                    self.messages.append(Message(
                        type='missing_field',
                        field=field_name
                    ))
                
                if field_name.endswith('[]') and base_field_name in self._document and not isinstance(self._document[base_field_name], list):
                    self.messages.append(Message(
                        type='invalid_type',
                        field=base_field_name,
                        expected='list'
                    ))
            else:
                parent_name, child_name = field_name.rsplit('.', 1)
                parent = self._index.fields.get(parent_name, [])
                for parent_field in parent:
                    if not isinstance(parent_field.value, dict):
                        self.messages.append(Message(
                            type='invalid_type',
                            field=parent_field.path,
                            expected='object'
                        ))
                    elif field.strictness == 'required' and child_name.strip('[]') not in parent_field.value:
                        self.messages.append(Message(
                            type='missing_field',
                            field=parent_field.path + '.' + child_name
                        ))
                    
                    base_child_name = child_name.strip('[]')
                    if child_name.endswith('[]') and base_child_name in parent_field.value and not isinstance(parent_field.value[base_child_name], list):
                        self.messages.append(Message(
                            type='invalid_type',
                            field=parent_field.path + '.' + base_child_name,
                            expected='list'
                        ))
    
    def _validate(self, field_name, fields, type, **kwargs):
        if type is None:
            return
        
        validator_name = f'validate_{type}'
        try:
            type_validator = getattr(type_validators, validator_name)
        except AttributeError:
            raise SchemaError(f"Type `{type}` specified for field `{field_name}` is invalid.")
        
        for field in fields:
            message = type_validator(field.path, field.value, **kwargs)
            if not message is None:
                self.messages.append(message)
    
    def _get_parent_name(self, field_name):
        if '.' in field_name:
            return field_name.strip('[]').rsplit('.', 1)
        elif field_name.endswith('[]'):
            return (field_name.strip('[]'), None)
            
        return (None, None)

_validator = Validator()