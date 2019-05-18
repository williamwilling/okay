import type_validators
from message import Message

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
    
    def required(self, field, type=None, **kwargs):
        values = self._get_values(field)
        for value in values:
            if isinstance(value, Message):
                if value.type != 'missing_field' or value.field.count('.') == field.count('.'):
                    self.messages.append(value)
            else:
                self._validate(field, value, type, **kwargs)
    
    def optional(self, field, type=None, **kwargs):
        values = self._get_values(field)
        for value in values:
            if isinstance(value, Message):
                if value.type != 'missing_field':
                    self.messages.append(value)
            else:
                self._validate(field, value, type, **kwargs)

    def ignore_extra_fields(self):
        for field in self._document.keys():
            self._validated_fields.add(field)
    
    def _get_values(self, field):
        if field is None:
            return [ self._document ]
        
        if field.endswith('[]'):
            field = field[:-2]
        
        self._validated_fields.add(field)

        parent_path, child_name = self._split_field_name(field)
        parents = self._get_values(parent_path)

        values = []
        for parent in parents:
            if isinstance(parent, Message):
                values.append(parent)
                continue
            elif not isinstance(parent, (dict, list)):
                values.append(Message(
                    type='invalid_type',
                    field=parent_path,
                    expected='object'
                ))
                continue
            
            if isinstance(parent, list):
                results = []
                for i, element in enumerate(parent):
                    if not isinstance(element, dict):
                        values.append(Message(
                            type='invalid_type',
                            field=parent_path.replace('[]', f'[{i}]'),
                            expected='object'
                        ))
                        continue

                    if not child_name in element:
                        values.append(Message(
                            type='missing_field',
                            field=field.replace('[]', f'[{i}]')
                        ))
                        continue

                    results.append(element[child_name])

                values.append(results)
            else:
                if not child_name in parent:
                    values.append(Message(
                        type='missing_field',
                        field=field
                    ))
                    continue

                values.append(parent[child_name])
        
        return values
    
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
    
    def _validate(self, field, value, type, **kwargs):
        if type is None:
            return
        
        validator_name = f'validate_{type}'
        type_validator = getattr(type_validators, validator_name)
        
        if isinstance(value, list):
            for i, element in enumerate(value):
                field_name = field.replace('[]', f'[{i}]')
                message = type_validator(field_name, element, **kwargs)
                if not message is None:
                    self.messages.append(message)
        else:
            message = type_validator(field, value, **kwargs)
            if not message is None:
                self.messages.append(message)


class MissingParentError(Exception):
    pass

class InvalidParentError(Exception):
    pass

class MissingFieldError(Exception):
    pass