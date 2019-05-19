import type_validators
from collections import namedtuple
from message import Message

Field = namedtuple('Field', 'name value')

class Validator:
    def __init__(self, schema):
        self._schema = schema
        self._validated_fields = set()
        self.messages = []
    
    def validate(self, document):
        if not isinstance(document, dict):
            raise TypeError('Document must be dictionary.')
        
        self._document = document
        self._schema(self)
        self._report_extra_fields()

        return len(self.messages) == 0
    
    def required(self, field_name, type=None, **kwargs):
        for field in self._iterate_fields(field_name):
            if isinstance(field, Message):
                message = field
                if message.type != 'missing_field' or message.field.count('.') == field_name.count('.'):
                    self.messages.append(message)
            else:
                self._validate(field, type, **kwargs)
    
    def optional(self, field_name, type=None, **kwargs):
        for field in self._iterate_fields(field_name):
            if isinstance(field, Message):
                message = field
                if message.type != 'missing_field':
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

            return
        
        self._validated_fields.add(field_name)

        parent_path, child_name = self._split_field_name(field_name)
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
            
            if isinstance(parent.value, list):
                for i, element in enumerate(parent.value):
                    if not isinstance(element, dict):
                        yield Message(
                            type='invalid_type',
                            field=f'{parent.name}[{i}]',
                            expected='object'
                        )
                        continue

                    if not child_name in element:
                        yield Message(
                            type='missing_field',
                            field=field_name.replace('[]', f'[{i}]')
                        )
                        continue

                    yield Field(field_name.replace('[]', f'[{i}]'), element[child_name])
            else:
                if parent.name is None:
                    name = child_name
                else:
                    name = f'{parent.name}.{child_name}'

                if not child_name in parent.value:
                    yield Message(
                        type='missing_field',
                        field=name
                    )
                    continue
                
                yield Field(name, parent.value[child_name])
    
    def _split_field_name(self, field):
        if not '.' in field:
            return (None, field)

        return field.rsplit('.', 1)
    
    def _report_extra_fields(self):
        for field in self._document.keys():
            if field not in self._validated_fields:
                self.messages.append(Message(
                    type='extra_field',
                    field=field
                ))
    
    def _validate(self, field, type, **kwargs):
        if type is None:
            return
        
        validator_name = f'validate_{type}'
        type_validator = getattr(type_validators, validator_name)
        
        message = type_validator(field.name, field.value, **kwargs)
        if not message is None:
            self.messages.append(message)