from okay.index import create_index

class TestIndex:
    def test_it_creates_no_entries_for_an_empty_document(self):
        document = {}
        schema_fields = []

        index = create_index(document, schema_fields)

        assert index.fields == {}
    
    def test_it_creates_an_entry_for_a_top_level_field(self):
        document = {
            'metadata': {}
        }
        schema_fields = [ 'metadata' ]

        index = create_index(document, schema_fields)

        assert 'metadata' in index.fields
    
    def test_it_doesnt_create_an_entry_for_a_top_level_field_not_in_the_schema(self):
        document = {
            'metadata': {}
        }
        schema_fields = []

        index = create_index(document, schema_fields)

        assert 'metadata' not in index.fields
    
    def test_it_creates_entries_for_a_nested_field(self):
        document = {
            'accommodation': {
                'geo': {
                    'longitude': 0
                }
            }
        }
        schema_fields = [
            'accommodation',
            'accommodation.geo',
            'accommodation.geo.longitude'
        ]

        index = create_index(document, schema_fields)

        assert 'accommodation' in index.fields
        assert 'accommodation.geo' in index.fields
        assert 'accommodation.geo.longitude' in index.fields
    
    def test_it_doesnt_create_an_entry_for_a_nested_field_not_in_the_schema(self):
        document = {
            'accommodation': {
                'geo': {
                    'latitude': 0
                }
            }
        }
        schema_fields = [ 'accommodation' ]

        index = create_index(document, schema_fields)

        assert 'accommodation.geo' not in index.fields
        assert 'accommodation.geo.latitude' not in index.fields
    
    def test_it_doesnt_create_an_entry_for_a_nested_field_when_parent_is_not_in_the_schema(self):
        document = {
            'accommodation': {
                'geo': {
                    'latitude': 0
                }
            }
        }
        schema_fields = [
            'accommodation.geo',
            'accommodation.geo.latitude'
        ]

        index = create_index(document, schema_fields)

        assert 'accommodation.geo' not in index.fields
        assert 'accommodation.geo.latitude' not in index.fields

    
    def test_it_creates_entries_for_a_list_of_scalars(self):
        document = {
            'accommodation': {
                'payment_methods': [ 'visa', 'mastercard', 'cash' ]
            }
        }
        schema_fields = [
            'accommodation',
            'accommodation.payment_methods',
            'accommodation.payment_methods[]'
        ]

        index = create_index(document, schema_fields)

        assert 'accommodation.payment_methods' in index.fields
        assert 'accommodation.payment_methods[]' in index.fields
    
    def test_it_creates_entries_for_a_list_of_nested_objects(self):
        document = {
            'ratings': [{
                'aspect': 'general',
                'score': 4.3
            }, {
                'aspect': 'staff',
                'score': 3.9
            }]
        }
        schema_fields = [
            'ratings',
            'ratings[]',
            'ratings[].aspect',
            'ratings[].score'
        ]

        index = create_index(document, schema_fields)

        assert 'ratings[].aspect' in index.fields
        assert 'ratings[].score' in index.fields
    
    def test_it_doesnt_create_an_entry_for_nested_objects_in_a_list_thats_not_in_the_schema(self):
        document = {
            'ratings': [{
                'aspect': 'general',
                'score': 4.3
            }, {
                'aspect': 'staff',
                'score': 3.9
            }]
        }
        schema_fields = [
            'ratings',
            'ratings[].aspect',
            'ratings[].score'
        ]

        index = create_index(document, schema_fields)

        assert 'ratings[].aspect' not in index.fields
        assert 'ratings[].score' not in index.fields
        
    
    def test_it_creates_entries_for_list_of_lists(self):
        document = {
            'matrix': [
                [ 1, 2, 3 ],
                [ 9, 8, 7 ]
            ]
        }
        schema_fields = [
            'matrix',
            'matrix[]',
            'matrix[][]'
        ]

        index = create_index(document, schema_fields)

        assert 'matrix[][]' in index.fields
    
    def test_it_doesnt_create_an_entry_for_a_list_in_a_list_thats_not_in_the_schema(self):
        document = {
            'matrix': [
                [ 1, 2, 3 ],
                [ 9, 8, 7 ]
            ]
        }
        schema_fields = [
            'matrix',
            'matrix[][]'
        ]

        index = create_index(document, schema_fields)

        assert 'matrix[][]' not in index.fields
    
    def test_it_adds_an_entry_for_a_top_level_field(self):
        document = {
            'name': 'Heartbreak Hotel'
        }
        schema_fields = [ 'name' ]

        index = create_index(document, schema_fields)

        assert len(index.fields['name']) == 1
        assert index.fields['name'][0].path == 'name'
        assert index.fields['name'][0].value == 'Heartbreak Hotel'
        assert index.fields['name'][0].parent_type == None
    
    def test_it_adds_entries_for_nested_fields(self):
        document = {
            'accommodation': {
                'name': 'Heartbreak Hotel'
            }
        }
        schema_fields = [
            'accommodation',
            'accommodation.name'
        ]

        index = create_index(document, schema_fields)

        assert len(index.fields['accommodation']) == 1
        assert index.fields['accommodation'][0].path == 'accommodation'
        assert index.fields['accommodation'][0].value == { 'name': 'Heartbreak Hotel' }
        assert index.fields['accommodation'][0].parent_type == None
        assert len(index.fields['accommodation.name']) == 1
        assert index.fields['accommodation.name'][0].path == 'accommodation.name'
        assert index.fields['accommodation.name'][0].value == 'Heartbreak Hotel'
        assert index.fields['accommodation.name'][0].parent_type == 'object'
    
    def test_it_adds_entries_for_a_list_of_scalars(self):
        document = {
            'accommodation': {
                'payment_methods': [ 'visa', 'mastercard', 'cash' ]
            }
        }
        schema_fields = [
            'accommodation',
            'accommodation.payment_methods',
            'accommodation.payment_methods[]'
        ]

        index = create_index(document, schema_fields)

        assert len(index.fields['accommodation.payment_methods']) == 1
        assert index.fields['accommodation.payment_methods'][0].path == 'accommodation.payment_methods'
        assert index.fields['accommodation.payment_methods'][0].value == [ 'visa', 'mastercard', 'cash' ]
        assert index.fields['accommodation.payment_methods'][0].parent_type == 'object'
        assert len(index.fields['accommodation.payment_methods[]']) == 3
        assert index.fields['accommodation.payment_methods[]'][0].path == 'accommodation.payment_methods[0]'
        assert index.fields['accommodation.payment_methods[]'][0].value == 'visa'
        assert index.fields['accommodation.payment_methods[]'][0].parent_type == 'list'
        assert index.fields['accommodation.payment_methods[]'][1].path == 'accommodation.payment_methods[1]'
        assert index.fields['accommodation.payment_methods[]'][1].value == 'mastercard'
        assert index.fields['accommodation.payment_methods[]'][1].parent_type == 'list'
        assert index.fields['accommodation.payment_methods[]'][2].path == 'accommodation.payment_methods[2]'
        assert index.fields['accommodation.payment_methods[]'][2].value == 'cash'
        assert index.fields['accommodation.payment_methods[]'][2].parent_type == 'list'
    
    def test_it_adds_entries_for_a_list_of_objects(self):
        document = {
            'accommodation': {
                'ratings': [{
                    'score': 4.2
                }, {
                    'aspect': 'staff',
                    'score': 3.9
                }]
            }
        }
        schema_fields = [
            'accommodation',
            'accommodation.ratings',
            'accommodation.ratings[]',
            'accommodation.ratings[].score',
            'accommodation.ratings[].aspect'
        ]

        index = create_index(document, schema_fields)

        assert len(index.fields['accommodation.ratings[]']) == 2
        assert index.fields['accommodation.ratings[]'][0].path == 'accommodation.ratings[0]'
        assert index.fields['accommodation.ratings[]'][0].value == { 'score': 4.2 }
        assert index.fields['accommodation.ratings[]'][0].parent_type == 'list'
        assert index.fields['accommodation.ratings[]'][1].path == 'accommodation.ratings[1]'
        assert index.fields['accommodation.ratings[]'][1].value == { 'aspect': 'staff', 'score': 3.9 }
        assert index.fields['accommodation.ratings[]'][1].parent_type == 'list'
        assert len(index.fields['accommodation.ratings[].score']) == 2
        assert index.fields['accommodation.ratings[].score'][0].path == 'accommodation.ratings[0].score'
        assert index.fields['accommodation.ratings[].score'][0].value == 4.2
        assert index.fields['accommodation.ratings[].score'][0].parent_type == 'object'
        assert index.fields['accommodation.ratings[].score'][1].path == 'accommodation.ratings[1].score'
        assert index.fields['accommodation.ratings[].score'][1].value == 3.9
        assert index.fields['accommodation.ratings[].score'][1].parent_type == 'object'
        assert len(index.fields['accommodation.ratings[].aspect']) == 1
        assert index.fields['accommodation.ratings[].aspect'][0].path == 'accommodation.ratings[1].aspect'
        assert index.fields['accommodation.ratings[].aspect'][0].value == 'staff'
        assert index.fields['accommodation.ratings[].aspect'][0].parent_type == 'object'
    
    def test_it_adds_entries_for_a_nested_list(self):
        document = {
            'matrix': [
                [ 1, 2, 3 ],
                [ 4, 5 ]
            ]
        }
        schema_fields = [
            'matrix',
            'matrix[]',
            'matrix[][]'
        ]

        index = create_index(document, schema_fields)

        assert len(index.fields['matrix[]']) == 2
        assert index.fields['matrix[]'][0].path == 'matrix[0]'
        assert index.fields['matrix[]'][0].value == [ 1, 2, 3 ]
        assert index.fields['matrix[]'][0].parent_type == 'list'
        assert index.fields['matrix[]'][1].path == 'matrix[1]'
        assert index.fields['matrix[]'][1].value == [ 4, 5 ]
        assert index.fields['matrix[]'][1].parent_type == 'list'
        assert len(index.fields['matrix[][]']) == 5
        assert index.fields['matrix[][]'][0].path == 'matrix[0][0]'
        assert index.fields['matrix[][]'][0].value == 1
        assert index.fields['matrix[][]'][0].parent_type == 'list'
        assert index.fields['matrix[][]'][1].path == 'matrix[0][1]'
        assert index.fields['matrix[][]'][1].value == 2
        assert index.fields['matrix[][]'][1].parent_type == 'list'
        assert index.fields['matrix[][]'][2].path == 'matrix[0][2]'
        assert index.fields['matrix[][]'][2].value == 3
        assert index.fields['matrix[][]'][2].parent_type == 'list'
        assert index.fields['matrix[][]'][3].path == 'matrix[1][0]'
        assert index.fields['matrix[][]'][3].value == 4
        assert index.fields['matrix[][]'][3].parent_type == 'list'
        assert index.fields['matrix[][]'][4].path == 'matrix[1][1]'
        assert index.fields['matrix[][]'][4].value == 5
        assert index.fields['matrix[][]'][4].parent_type == 'list'
    
    def test_it_stores_extra_top_level_field(self):
        document = {
            'accommodation': {}
        }
        schema_fields = []

        index = create_index(document, schema_fields)

        assert index.extra_fields == [ 'accommodation' ]
    
    def test_it_stores_extra_nested_fields(self):
        document = {
            'accommodation': {
                'name': 'Hearbreak Hotel'
            }
        }
        schema_fields = [ 'accommodation' ]

        index = create_index(document, schema_fields)

        assert index.extra_fields == [ 'accommodation.name' ]