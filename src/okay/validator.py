from . import type_validators
from .index import create_index
from .message import Message
from .schema_compiler import compile, required, optional, ignore_extra_fields
from .schema_error import SchemaError

def validate(schema, document, message_values=None):
    _validator._reset(schema, document)
    _validator._validate()
    _validator._report_missing_fields()
    _validator._report_extra_fields()

    if message_values:
        for message in _validator.messages:
            message.add(**message_values)
    return _validator.messages


class Validator:
    def __init__(self):
        self.messages = []
        self._type_validators = {}
        self._compiled_schemas = {}
    
    def _reset(self, schema, document):
        if schema not in self._compiled_schemas:
            try:
                self._preprocessing = True
                self._compiled_schemas[schema] = compile(schema)
                self._preprocessing = False
            except Exception as e:
                raise SchemaError(f"Schema raised `{type(e).__name__}`.") from e
        
        self._schema = self._compiled_schemas[schema]
        self._index = create_index(document, self._schema.fields.keys())
        self._document = document
        self._ignore_extra_fields = False
        self.messages.clear()
    
    def _validate(self):
        for field_name, fields in self._index.fields.items():
            for field in fields:
                for rule in self._schema.fields[field_name].rules:
                    if field.value is None:
                        if not rule.nullable:
                            message = Message(
                                type='null_value',
                                field=field.path,
                                expected={
                                    'type': rule.type
                                }
                            )

                            self.messages.append(message)
                    else:
                        message = rule.validate(field.path, field.value)
                        if not message is None:
                            self.messages.append(message)
    
    def _report_extra_fields(self):
        if self._schema.ignore_extra_fields:
            return

        for extra_field in self._index.extra_fields:
            self.messages.append(Message(
                type='extra_field',
                field=extra_field
            ))
    
    def _report_missing_fields(self):
        for field_name, field in self._schema.fields.items():
            if '.' not in field_name:
                parent_name = '.'
                child_name = field_name
            else:
                parent_name, child_name = field_name.rsplit('.', 1)

            parent = self._index.fields.get(parent_name, [])
            for parent_field in parent:
                if parent_field.value is None and self._schema.fields[parent_field.path].is_nullable_object():
                    continue

                if parent_field.value is None and field.strictness == 'required':
                    self.messages.append(Message(
                        type='missing_field',
                        field=parent_field.path + '.' + child_name if parent_field.path != '.' else child_name
                    ))

                if isinstance(parent_field.value, dict) and field.strictness == 'required' and child_name.strip('[]') not in parent_field.value:
                    self.messages.append(Message(
                        type='missing_field',
                        field=parent_field.path + '.' + child_name if parent_field.path != '.' else child_name
                    ))

_validator = Validator()