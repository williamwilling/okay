from .field import Field

class IndexEntry:
    def __init__(self, field_name, value, type, multiple=False):
        self.value = value
        self.type = type
        self.multiple = multiple
        self.parents = self._find_parents(field_name)

def create_index(document):
    index = {}
    _index_object(index, document)
    return index

def _index_object(index, document, parent='', indexed_parent=''):
    for key, value in document.items():
        path = f'{parent}{key}'
        indexed_path = f'{indexed_parent}{key}'
        fields = index.get(path, [])
        fields.append(Field(indexed_path, value))
        index[path] = fields

        if isinstance(value, dict):
            _index_object(index, value, f'{path}.', f'{indexed_path}.')
        
        if isinstance(value, list):
            _index_list(index, value, path, indexed_path)

def _index_list(index, items, parent, indexed_parent):
    fields = []
    for i, item in enumerate(items):
        indexed_path = f'{indexed_parent}[{i}]'
        fields.append(Field(indexed_path, item))
    index[f'{parent}[]'] = fields

    if len(items) > 0:
        fields = []
        for i, item in enumerate(items):
            if isinstance(item, dict):
                parent_path = f'{parent}[].'
                indexed_parent_path = f'{indexed_parent}[{i}].'
                _index_object(index, item, parent_path, indexed_parent_path)
            elif isinstance(item, list):
                parent_path = f'{parent}[]'
                indexed_parent_path = f'{indexed_parent}[{i}]'
                _index_list(index, item, parent_path, indexed_parent_path)