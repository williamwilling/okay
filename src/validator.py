import type_validators
from collections import namedtuple
from message import Message

Field = namedtuple('Field', 'name value')

def validate(schema, document, message_values=None):
    if not isinstance(document, dict):
        raise TypeError('Document must be dictionary.')

    _validator._reset(document, message_values)
    schema(_validator)
    _validator._report_extra_fields(document)    

    return _validator.messages


class Validator:
    def __init__(self):
        self._validated_fields = set()
        self.messages = []
    
    def _reset(self, document, message_values):
        self._document = document
        self._validated_fields.clear()
        self._message_values = message_values or {}
        self.messages.clear()
    
    def required(self, field_name, type=None, **kwargs):
        for field in self._iterate_fields(field_name):
            if isinstance(field, Message):
                message = field
                if not _is_parent_missing(message, field_name):
                    message.add(**self._message_values)
                    self.messages.append(message)
            else:
                self._validate(field, type, **kwargs)
    
    def optional(self, field_name, type=None, **kwargs):
        for field in self._iterate_fields(field_name):
            if isinstance(field, Message):
                message = field
                if message.type != 'missing_field':
                    message.add(**self._message_values)
                    self.messages.append(message)
            else:
                self._validate(field, type, **kwargs)

    def ignore_extra_fields(self):
        for field_name in self._document.keys():
            self._validated_fields.add(field_name)
    
    def _iterate_fields(self, field_name):
        if field_name is None:
            yield Field(None, self._document)
            return
        
        if field_name.endswith('[]'):
            yield from self._iterate_list(field_name)
            return
        
        self._validated_fields.add(field_name)

        parent_path, child_name = _split_field_name(field_name)
        for parent in self._iterate_fields(parent_path):
            if isinstance(parent, Message):
                yield parent
                continue
            elif not isinstance(parent.value, (dict, list)):
                yield Message(
                    type='invalid_type',
                    field=parent.name,
                    expected='object'
                )
                continue

            name = f'{parent.name}.{child_name}' if parent.name is not None else child_name
            if not child_name in parent.value:
                yield Message(
                    type='missing_field',
                    field=name
                )
                continue
            
            yield Field(name, parent.value[child_name])
    
    def _iterate_list(self, field_name):
        field = next(self._iterate_fields(field_name[:-2]))
        if not isinstance(field.value, list):
            yield Message(
                type='invalid_type',
                field=field.name,
                expected='list'
            )
        else:
            for i, element in enumerate(field.value):
                yield Field(f'{field.name}[{i}]', element)
    
    def _validate(self, field, type, **kwargs):
        if type is None:
            return
        
        validator_name = f'validate_{type}'
        type_validator = getattr(type_validators, validator_name)
        
        message = type_validator(field.name, field.value, **kwargs)
        if not message is None:
            message.add(**self._message_values)
            self.messages.append(message)

    def _report_extra_fields(self, object, prefix='', indexed_prefix=''):
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


def _split_field_name(field):
    if not '.' in field:
        return (None, field)

    return field.rsplit('.', 1)

def _is_parent_missing(message, field_name):
    return message.type == 'missing_field' and message.field.count('.') < field_name.count('.')


_validator = Validator()