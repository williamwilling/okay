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
    
    def required(self, field, type=None):
        try:
            value = self._get_value(field)
        except MissingParentError:
            return
        except InvalidParentError as error:
            self.messages.append(Message(
                type='invalid_type',
                field=str(error),
                expected='object'
            ))
            return
        except MissingFieldError:
            self.messages.append(Message(
                type='missing_field',
                field=field
            ))
            return
        
        self._validate(field, value, type)
    
    def optional(self, field, type=None):
        try:
            value = self._get_value(field)
        except (MissingParentError, MissingFieldError):
            return
        except InvalidParentError as error:
            self.messages.append(Message(
                type='invalid_type',
                field=str(error),
                expected='object'
            ))
            return
        
        self._validate(field, value, type)

    def ignore_extra_fields(self):
        for field in self._document.keys():
            self._validated_fields.add(field)
    
    def _get_value(self, field):
        if field is None:
            return self._document
        
        self._validated_fields.add(field)

        parent_path, child_name = self._split_field_name(field)
        try:
            parent = self._get_value(parent_path)
        except MissingFieldError as error:
            raise MissingParentError(str(error))

        if not isinstance(parent, dict):
            raise InvalidParentError(parent_path)
        elif not child_name in parent:
            raise MissingFieldError(field)

        return parent[child_name]
    
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
    
    def _validate(self, field, value, type):
        if type is None:
            return
        
        validator_name = f'validate_{type}'
        type_validator = getattr(type_validators, validator_name)

        message = type_validator(field, value)
        if not message is None:
            self.messages += [ message ]


class MissingParentError(Exception):
    pass

class InvalidParentError(Exception):
    pass

class MissingFieldError(Exception):
    pass