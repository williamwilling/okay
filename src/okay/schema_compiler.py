from . import type_validators
from .schema_error import SchemaError
from collections import defaultdict

class Schema:
    def __init__(self):
        self.fields = defaultdict(Field)
        self.ignore_extra_fields = False

class Field:
    def __init__(self):
        self.strictness = 'unknown'
        self.validators = []
        self.nullable = False

    def has_explicit_type(self):
        for validator in self.validators:
            if not validator.is_implicit:
                return True
        
        return False
    
    def is_nullable_object(self):
        for validator in self.validators:
            if validator.type == 'object' and validator.nullable:
                return True
        
        return False


class Validator:
    def __init__(self, type, nullable, is_implicit, validation_function):
        self.type = type
        self.nullable = nullable
        self.is_implicit = is_implicit
        self.run = validation_function

_active_schema = None

def compile(schema):
    global _active_schema
    _active_schema = Schema()

    schema()
    return _active_schema

def required(field_name, type=None, **kwargs):
    _process(field_name, type, is_required=True, **kwargs)

def optional(field_name, type=None, **kwargs):
    if field_name == '.':
        raise SchemaError(
            'Root cannot be optional.',
            type='optional_not_allowed',
            field='.'
        )
    
    _process(field_name, type, is_required=False, **kwargs)

def ignore_extra_fields():
    _active_schema.ignore_extra_fields = True

def _process(field_name, type, is_required, **kwargs):
    if type is not None:
        nullable = type.endswith('?')
        is_implicit = False
        type = type.rstrip('?')
    else:
        type = 'any'
        nullable = False
        is_implicit = True

    strictness = 'required' if is_required else 'optional'
    if type == 'list':
        _active_schema.fields[field_name + '[]'].strictness = strictness
    
    while field_name:
        field = _active_schema.fields[field_name]
        _raise_on_schema_errors(field, field_name, strictness, nullable, is_implicit)
        
        if not is_implicit and type in ['object', 'list']:
            _remove_implicit_validators(field, type)
        if not (type in ['object', 'list'] and is_implicit and _validator_exists(field.validators, type)):
            validation_function = _get_validation_function(type, field_name, kwargs)
            validator = Validator(type, nullable, is_implicit, validation_function)
            field.validators.append(validator)

        field.nullable = field.nullable or nullable
        field.strictness = strictness if field.strictness == 'unknown' else field.strictness

        field_name, type, strictness = _get_parent_field(field_name, strictness)
        nullable = False
        kwargs = {}
        is_implicit = True

def _raise_on_schema_errors(field, field_name, strictness, nullable, is_implicit):
    if field.strictness == 'required' and strictness == 'optional':
        raise SchemaError(
            "Field '" + field_name + "' marked as optional, but it's already required.",
            type='already_required',
            field=field_name.strip('[]')
        )
    elif field.strictness == 'optional' and strictness == 'required':
        raise SchemaError(
            "Field '" + field_name + "' marked as required, but it's already optional.",
            type='already_optional',
            field=field_name.strip('[]')
        )
    
    if not is_implicit and field.has_explicit_type() and field.nullable != nullable:
        if nullable:
            raise SchemaError(
                "Field '" + field_name + "' marked as nullable, but it's already non-nullable.",
                type='already_non_nullable',
                field=field_name.strip('[]')
            )
        else:
            raise SchemaError(
                "Field '" + field_name + "' marked as non-nullable, but it's already nullable.",
                type='already_nullable',
                field=field_name.strip('[]')
            )

def _get_validation_function(type, field_name, kwargs):
    type_validator_builder = getattr(type_validators, type.capitalize() + 'Validator', None)
    if type_validator_builder:
        return type_validator_builder(field_name, **kwargs)
    else:
        raise SchemaError(f"Type `{type}` specified for field `{field_name}` is invalid.")

def _remove_implicit_validators(field, type):
    field.validators = [ validator for validator in field.validators if validator.type != type or not validator.is_implicit ]

def _validator_exists(validators, type):
    for validator in validators:
        if validator.type == type:
            return True
    
    return False

def _get_parent_field(field_name, strictness):
    if field_name == '.':
        return None, None, None
    elif field_name.endswith('[]'):
        return field_name[:-2], 'list', strictness
    elif '.' in field_name:
        return field_name.rsplit('.', 1)[0], 'object', 'unknown'
    else:
        return '.', 'object', 'required'