from .schema_error import SchemaError

class Schema:
    def __init__(self):
        self.fields = {}

class FieldDefinition:
    def __init__(self, strictness):
        self.strictness = strictness

_active_schema = None

def compile(schema):
    global _active_schema
    _active_schema = Schema()

    schema()
    return _active_schema

def required(field_name, type=None, **kwargs):
    _process(field_name, type, is_required=True, **kwargs)

def optional(field_name, type=None, **kwargs):
    _process(field_name, type, is_required=False, **kwargs)

def _process(field_name, type, is_required, **kwargs):
    fields = _active_schema.fields

    strictness = 'required' if is_required else 'optional' 
    if type == 'list':
        field_name += '[]'   

    while True:
        if field_name in fields:
            if fields[field_name].strictness == 'required' and strictness == 'optional':
                raise SchemaError(
                    "Field '" + field_name + "' marked as optional, but it's already required.",
                    type='already_required',
                    field=field_name.strip('[]')
                )
            elif fields[field_name].strictness == 'optional' and strictness == 'required':
                raise SchemaError(
                    "Field '" + field_name + "' marked as required, but it's already optional.",
                    type='already_optional',
                    field=field_name.strip('[]')
                )
        else:
            fields[field_name] = FieldDefinition(strictness)

        if field_name.endswith('[]'):
            field_name = field_name[:-2]
        elif '.' in field_name:
            field_name = field_name.rsplit('.', 1)[0]
            strictness = 'unknown'
        else:
            break