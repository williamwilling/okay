class Index:
    def __init__(self):
        self.fields = {}
        self.extra_fields = []

class IndexEntry:
    def __init__(self, path, value, parent_type):
        self.path = path
        self.value = value
        self.parent_type = parent_type

def create_index(document, schema_fields):
    index = Index()
    _create_object_entry(index, document, schema_fields, parent_name=None, parent_path=None, parent_type=None)

    return index

def _create_object_entry(index, document, schema_fields, parent_name, parent_path, parent_type):
    for key, value in document.items():
        field_name = parent_name + '.' + key if parent_name else key
        path = parent_path + '.' + key if parent_path else key
        if field_name not in schema_fields:
            index.extra_fields.append(path)
            continue

        index.fields[field_name] = index.fields.get(field_name, [])

        index.fields[field_name].append(IndexEntry(path, value, parent_type))

        if isinstance(value, dict):
            _create_object_entry(index, value, schema_fields, field_name, path, 'object')
        elif isinstance(value, list):
            _create_list_entry(index, value, schema_fields, field_name, path, 'object')

def _create_list_entry(index, document, schema_fields, parent_name, parent_path, parent_type):
    field_name = parent_name + '[]'
    if field_name not in schema_fields:
        return

    index.fields[field_name] = index.fields.get(field_name, [])

    for i, value in enumerate(document):
        path = parent_path + '[' + str(i) + ']'
        index.fields[field_name].append(IndexEntry(path, value, 'list'))

        if isinstance(value, dict):
            _create_object_entry(index, value, schema_fields, field_name, path, 'object')
        elif isinstance(value, list):
            _create_list_entry(index, value, schema_fields, field_name, path, 'list')