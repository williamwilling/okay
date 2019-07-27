from .message import Message

class Field:
    def __init__(self, full_name, value, type):
        self.full_name = full_name
        self.value = value
        self.message = value
        self.type = type

class IndexEntry:
    def __init__(self, fields):
        self.fields = fields

class Index:
    def __init__(self):
        self._cache = {}
    
    def clear(self):
        self._cache.clear()
    
    def look_up(self, document, field_name):
        if field_name in self._cache:
            return self._cache[field_name]
        
        parent_name, child_name = self._split_field_name(field_name)
        if not parent_name:
            index_entry = self._create_top_level_entry(document, field_name, child_name)
        elif child_name == '[]':
            index_entry = self._create_list_entry(document, parent_name)
        else:
            index_entry = self._create_nested_entry(document, parent_name, child_name)
        
        index_entry.name_hierarchy = list(self._get_name_hierarchy(field_name))
        self._cache[field_name] = index_entry
        return index_entry

    def _create_top_level_entry(self, document, field_name, child_name):
        if child_name not in document:
            value = Message(
                type='missing_field',
                field=field_name
            )
            type = 'message'
        else:
            value = document[child_name]
            if isinstance(value, dict):
                type = 'object'
            elif isinstance(value, list):
                type = 'list'
            else:
                type = 'scalar'

        field = Field(field_name, value, type)
        return IndexEntry([ field ])
        
    def _create_list_entry(self, document, parent_name):
        parent = self.look_up(document, parent_name)
        fields = []

        for parent_field in parent.fields:
            full_name = parent_field.full_name + '[]'

            if parent_field.type == 'message':
                if parent_field.message.type == 'missing_field':
                    value = Message(
                        type='missing_field',
                        field=full_name
                    )
                elif parent_field.message.type == 'invalid_type':
                    value = parent_field.message
                else:
                    value = Message(
                        type='missing_parent',
                        field=full_name,
                        expected=parent_field.full_name
                    )
                fields.append(Field(full_name, value, 'message'))
            elif parent_field.type != 'list':
                value = Message(
                    type='invalid_type',
                    field=parent_field.full_name,
                    expected='list'
                )
                fields.append(Field(full_name, value, 'message'))
            else:
                for i, value in enumerate(parent_field.value):
                    full_name = parent_field.full_name + '[' + str(i) + ']'

                    if isinstance(value, dict):
                        type = 'object'
                    elif isinstance(value, list):
                        type = 'list'
                    else:
                        type = 'scalar'

                    fields.append(Field(full_name, value, type))
        
        return IndexEntry(fields)

    def _create_nested_entry(self, document, parent_name, child_name):
        parent = self.look_up(document, parent_name)
        fields = []

        for parent_field in parent.fields:
            full_name = parent_field.full_name + '.' + child_name
            if parent_field.type == 'message':
                if parent_field.message.type == 'invalid_type':
                    value = parent_field.message
                else:
                    value = Message(
                        type='missing_parent',
                        field=full_name,
                        expected=parent_field.full_name
                    )
                type = 'message'
            elif parent_field.type != 'object':
                value = Message(
                    type='invalid_type',
                    field=parent_field.full_name,
                    expected='object'
                )
                type = 'message'
            elif child_name not in parent_field.value:
                value = Message(
                    type='missing_field',
                    field=full_name
                )
                type = 'message'
            else:
                value = parent_field.value[child_name]
                if isinstance(value, dict):
                    type = 'object'
                elif isinstance(value, list):
                    type = 'list'
                else:
                    type = 'scalar'

            field = Field(full_name, value, type)
            fields.append(field)
        
        return IndexEntry(fields)
    
    def _split_field_name(self, field_name):
        if field_name.endswith('[]'):
            return (field_name[:-2], '[]')
        
        if '.' in field_name:
            return field_name.rsplit('.', 1)
        
        return (None, field_name)
    
    def _get_name_hierarchy(self, field_name):
        while True:
            yield field_name

            if field_name.endswith('[]'):
                field_name = field_name[:-2]
            elif '.' in field_name:
                field_name = field_name.rsplit('.', 1)[0]
            else:
                break
