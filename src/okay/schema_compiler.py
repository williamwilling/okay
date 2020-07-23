from . import type_validators
from .schema_error import SchemaError
from collections import defaultdict

class Schema:
    def __init__(self):
        self.fields = defaultdict(FieldDefinition)
        self.ignore_extra_fields = False

class FieldDefinition:
    def __init__(self):
        self.strictness = 'unknown'
        self.nullable = None
        self.is_implicit = True
        self.type = None
        self.type_validators = []

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
    fields = _active_schema.fields

    is_implicit = False
    strictness = 'required' if is_required else 'optional' 

    if type == 'list':
        fields[field_name + '[]'].strictness = strictness
    
    nullable = False
    if type and type.endswith('?'):
        type = type[:-1]
        nullable = True
    
    while True:
        field = fields[field_name]
        field.type = type

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
        
        if not is_implicit and not field.is_implicit and field.nullable != nullable:
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
        elif field.is_implicit:
            field.nullable = nullable
            field.is_implicit = is_implicit

        type_validator = None
        if type and type != 'any':
            type_validator_builder = getattr(type_validators, type.capitalize() + 'Validator', None)
            if type_validator_builder:
                type_validator = type_validator_builder(field_name, **kwargs)
            else:
                try:
                    type_validator = getattr(type_validators, 'validate_' + type)
                except AttributeError:
                    raise SchemaError(f"Type `{type}` specified for field `{field_name}` is invalid.")
        
        if type in [ 'object', 'list' ] and not is_implicit:
            field.type_validators = [ type_validator for type_validator in field.type_validators if not type_validator.is_implicit ]
        if type not in [ 'object', 'list' ] or len([ type_validator for type_validator in field.type_validators if not type_validator.is_implicit ]) == 0:
            field.strictness = strictness if field.strictness == 'unknown' else field.strictness
            if type_validator:
                type_validator.is_implicit = is_implicit
                field.type_validators.append(type_validator)

        if field_name == '.':
            break
        elif field_name.endswith('[]'):
            field_name = field_name[:-2]
            type = 'list'
            nullable = False
            kwargs = {}
            is_implicit = True
        elif '.' in field_name:
            field_name = field_name.rsplit('.', 1)[0]
            strictness = 'unknown'
            type = 'object'
            nullable = False
            kwargs = {}
            is_implicit = True
        else:
            field_name = '.'
            strictness = 'required'
            type = 'object'
            nullable = False
            kwargs = {}
            is_implicit = True