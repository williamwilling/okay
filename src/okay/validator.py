
from . import type_validators
from .field import Field
from .indexer import create_index
from .message import Message
from .schema_error import SchemaError

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

    return _validator.messages


class Validator:
    def __init__(self):
        self._validated_fields = set()
        self._required_fields = set()
        self._optional_fields = set()
        self.messages = []
    
    def _reset(self, document, message_values):
        self._document = document
        self._index = create_index(document)
        self._validated_fields.clear()
        self._required_fields.clear()
        self._optional_fields.clear()
        self._message_values = message_values or {}
        self.messages.clear()
    
    def required(self, field_name, type=None, **kwargs):
        if field_name.strip('[]') in self._optional_fields:
            raise SchemaError(f"Required field `{field_name}` has already been specified as optional.")
        self._required_fields.add(field_name.strip('[]'))
        self._mark_field(field_name)

        if field_name not in self._index:
            if field_name.endswith('[]') and field_name.rstrip('[]') in self._index:
                self.messages.append(Message(
                    type='invalid_type',
                    field=self._index[field_name.rstrip('[]')][0].name,
                    expected='list',
                    **self._message_values
                ))
                return

            fragments = self._fragment(field_name)
            for fragment in reversed(fragments[1:]):
                if not fragment in self._index:
                    return

                if self._index[fragment][0].type != 'object':
                    self.messages.append(Message(
                        type='invalid_type',
                        field=fragment,
                        expected='object',
                        **self._message_values
                    ))
                    return

            if len(fragments) == 1:
                self.messages.append(Message(
                    type='missing_field',
                    field=field_name,
                    **self._message_values
                ))
                return
            else:
                field_tail = field_name.rsplit('.', -1)[-1]

                for parent_field in self._index[fragments[1]]:
                    self.messages.append(Message(
                        type='missing_field',
                        field=f'{parent_field.name}.{field_tail}'
                    ))
                return
        
        self._validate(field_name, self._index[field_name], type, **kwargs)

    def optional(self, field_name, type=None, **kwargs):
        if field_name.strip('[]') in self._required_fields:
            raise SchemaError(f"Optional field `{field_name}` has already been specified as required.")
        self._optional_fields.add(field_name.strip('[]'))
        self._mark_field(field_name)

        parent = self._parent(field_name)
        if parent:
            if parent not in self._index:
                return
            
            parent_fields = self._index[parent]
            for field in parent_fields:
                if field.type != 'object':
                    self.messages.append(Message(
                        type='invalid_type',
                        field=field.name,
                        expected='object',
                        **self._message_values
                    ))

        if field_name not in self._index:
            return

        self._validate(field_name, self._index[field_name], type, **kwargs)

    def ignore_extra_fields(self):
        for field_name in self._document.keys():
            self._validated_fields.add(field_name)
    
    def _mark_field(self, field_name):
        if '.' in field_name or field_name.endswith('[]'):
            self._mark_field(self._parent(field_name))

        self._validated_fields.add(field_name)
        # if field_name.endswith('[]'):
        #     self._validated_fields.add(field_name[:-2])
        # if field_name in self._index and self._index[field_name][0].type == 'list':
        #     self._validated_fields.add(f'{field_name}[]')
    
    def _parent(self, field_name):
        if field_name.endswith('[]'):
            return field_name[:-2]
        
        if '.' in field_name:            
            return field_name.rsplit('.', 1)[0]
        
    def _fragment(self, field_name):
        fragments = [ field_name ]
        while '.' in field_name:
            field_name = field_name.rsplit('.', 1)[0]
            fragments.append(field_name)

        return fragments
    
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
    
    # def _validate(self, field, type, **kwargs):
    #     if type is None:
    #         return
        
    #     validator_name = f'validate_{type}'
    #     try:
    #         type_validator = getattr(type_validators, validator_name)
    #     except AttributeError:
    #         raise SchemaError(f"Type `{type}` specified for field `{field}` is invalid.")
        
    #     if field.value.multiple:
    #         for i, element in enumerate(field.value.value):
    #             field_name = f"{field.name.strip('[]')}[{i}]"
    #             message = type_validator(field_name, element, **kwargs)
    #             if not message is None:
    #                 message.add(**self._message_values)
    #                 self.messages.append(message)
    #     else:
    #         message = type_validator(field.name, field.value.value, **kwargs)
    #         if not message is None:
    #             message.add(**self._message_values)
    #             self.messages.append(message)

    def _validate(self, field_name, fields, type, **kwargs):
        if type is None:
            return
        
        validator_name = f'validate_{type}'
        try:
            type_validator = getattr(type_validators, validator_name)
        except AttributeError:
            raise SchemaError(f"Type `{type}` specified for field `{field_name}` is invalid.")

        for field in fields:
            message = type_validator(field.name, field.value, **kwargs)
            if not message is None:
                message.add(**self._message_values)
                self.messages.append(message)

    # def _report_extra_fields(self, object, prefix='', indexed_prefix=''):
    #     if isinstance(object, dict):
    #         for key in object.keys():
    #             field_name = f'{prefix}{key}'
    #             if field_name not in self._validated_fields:
    #                 self.messages.append(Message(
    #                     type='extra_field',
    #                     field=f'{indexed_prefix}{key}',
    #                     **self._message_values
    #                 ))
    #             else:
    #                 self._report_extra_fields(object[key], f'{prefix}{key}.', f'{indexed_prefix}{key}.')
    #     elif isinstance(object, list):
    #         for i, element in enumerate(object):
    #             self._report_extra_fields(element, f'{prefix[:-1]}[].', f'{indexed_prefix[:-1]}[{i}].')

    def _report_extra_fields(self, document):
        for key, fields in self._index.items():
            if key not in self._validated_fields:
                if not (key.endswith('[]') and self._index[key[:-2]][0].type == 'list'):
                    for field in fields:
                        self.messages.append(Message(
                            type='extra_field',
                            field=field.name,
                            **self._message_values
                        ))



def _split_field_name(field):
    if not '.' in field:
        return (None, field)

    return field.rsplit('.', 1)

def _is_parent_missing(message, field_name):
    return message.type == 'missing_field' and message.field.count('.') < field_name.count('.')


_validator = Validator()