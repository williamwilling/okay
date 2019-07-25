from okay import create_index

class TestIndexer:
    def test_it_leaves_empty_document_unchanged(self):
        document = {}
        index = create_index(document)

        assert index == {}
    
    def test_it_extracts_root_level_paths(self):
        document = {
            'accommodation': {}
        }
        index = create_index(document)

        assert 'accommodation' in index
    
    def test_it_extracts_nested_paths(self):
        document = {
            'accommodation': {
                'geo': {
                    'latitude': 0
                }
            }
        }
        index = create_index(document)

        assert 'accommodation.geo.latitude' in index
    
    def test_it_extracts_paths_from_list_of_scalars(self):
        document = {
            'accommodation': {
                'payment_methods': []
            }
        }
        index = create_index(document)

        assert 'accommodation.payment_methods' in index
        assert 'accommodation.payment_methods[]' in index
    
    def test_it_extracts_paths_from_a_list_of_empty_objects(self):
        document = {
            'accommodation': {
                'ratings': [{}]
            }
        }
        index = create_index(document)

        assert 'accommodation.ratings[]' in index
    
    def test_it_extracts_path_from_list_of_similar_objects(self):
        document = {
            'accommodation': {
                'ratings': [{
                    'score': 0,
                    'out_of': 0
                }, {
                    'score': 1,
                    'out_of': 1
                }]
            }
        }
        index = create_index(document)

        assert 'accommodation.ratings[].score' in index
        assert 'accommodation.ratings[].out_of' in index
    
    def test_it_extracts_paths_from_list_of_dissimilar_objects(self):
        document = {
            'accommodation': {
                'ratings': [{
                    'score': 0
                }, {
                    'aspect': ''
                }]
            }
        }
        index = create_index(document)

        assert 'accommodation.ratings[].score' in index
        assert 'accommodation.ratings[].aspect' in index
    
    def test_it_stores_the_value_of_root_level_items(self):
        document = {
            'metadata': {
                'accommodation_id': 1    
            }
        }
        index = create_index(document)

        fields = index['metadata']
        assert len(fields) == 1
        assert fields[0].name == 'metadata'
        assert fields[0].value == { 'accommodation_id': 1 }
    
    def test_it_stores_the_value_of_nested_items(self):
        document = {
            'metadata': {
                'accommodation_id': 1    
            }
        }
        index = create_index(document)

        fields = index['metadata.accommodation_id']
        assert len(fields) == 1
        assert fields[0].name == 'metadata.accommodation_id'
        assert fields[0].value == 1
    
    def test_it_stores_the_value_of_lists(self):
        document = {
            'accommodation': {
                'payment_methods': [ 'visa', 'mastercard', 'cash' ]
            }
        }
        index = create_index(document)

        fields = index['accommodation.payment_methods']
        assert len(fields) == 1
        assert fields[0].name == 'accommodation.payment_methods'
        assert fields[0].value == [ 'visa', 'mastercard', 'cash' ]
    
    def test_it_stores_the_values_of_a_list_of_scalars(self):
        document = {
            'accommodation': {
                'payment_methods': [ 'visa', 'mastercard', 'cash' ]
            }
        }
        index = create_index(document)

        fields = index['accommodation.payment_methods[]']
        assert len(fields) == 3
        assert fields[0].name == 'accommodation.payment_methods[0]'
        assert fields[0].value == 'visa'
        assert fields[1].name == 'accommodation.payment_methods[1]'
        assert fields[1].value == 'mastercard'
        assert fields[2].name == 'accommodation.payment_methods[2]'
        assert fields[2].value == 'cash'
    
    def test_it_stores_the_values_of_a_list_of_empty_objects(self):
        document = {
            'accommodation': {
                'ratings': [ {}, {} ]
            }
        }
        index = create_index(document)

        fields = index['accommodation.ratings[]']
        assert len(fields) == 2
        assert fields[0].name == 'accommodation.ratings[0]'
        assert fields[0].value == {}
        assert fields[1].name == 'accommodation.ratings[1]'
        assert fields[1].value == {}
    
    def test_it_stores_the_values_of_a_list_of_similar_objects(self):
        document = {
            'accommodation': {
                'ratings': [{
                    'score': 3.7,
                }, {
                    'score': 4.1
                }]
            }
        }
        index = create_index(document)

        fields = index['accommodation.ratings[].score']
        assert fields[0].name == 'accommodation.ratings[0].score'
        assert fields[0].value == 3.7
        assert fields[1].name == 'accommodation.ratings[1].score'
        assert fields[1].value == 4.1
    
    def test_it_stores_the_values_of_a_list_of_dissimilar_objects(self):
        document = {
            'accommodation': {
                'ratings': [{
                    'aspect': 'general'
                }, {
                    'score': 3.2
                }]
            }
        }
        index = create_index(document)

        fields = index['accommodation.ratings[].aspect']
        assert len(fields) == 1
        assert fields[0].name == 'accommodation.ratings[0].aspect'
        assert fields[0].value == 'general'

        fields = index['accommodation.ratings[].score']
        assert len(fields) == 1
        assert fields[0].name == 'accommodation.ratings[1].score'
        assert fields[0].value == 3.2
    
    def test_it_stores_the_values_of_nested_objects_inside_lists(self):
        document = {
            'accommodation': {
                'ratings': [{
                    'score': {
                        'value': 3.7,
                        'out_of': 5
                    }
                }, {
                    'score': {
                        'value': 4.1,
                        'out_of': 5
                    }
                }]
            }
        }
        index = create_index(document)

        fields = index['accommodation.ratings[].score.value']
        assert len(fields) == 2
        assert fields[0].name == 'accommodation.ratings[0].score.value'
        assert fields[0].value == 3.7
        assert fields[1].name == 'accommodation.ratings[1].score.value'
        assert fields[1].value == 4.1
        
        fields = index['accommodation.ratings[].score.out_of']
        assert len(fields) == 2
        assert fields[0].name == 'accommodation.ratings[0].score.out_of'
        assert fields[0].value == 5
        assert fields[1].name == 'accommodation.ratings[1].score.out_of'
        assert fields[1].value == 5
    
    def test_it_stores_the_values_of_nested_lists(self):
        document = {
            'accommodation': {
                'units': [{
                    'ratings': [{
                        'aspect': 'general',
                        'score': 3.7,
                    }, {
                        'aspect': 'cleanliness',
                        'score': 4.1
                    }]
                }, {
                    'ratings': [{
                        'aspect': 'general',
                        'score': 4.4
                    }, {
                        'aspect': 'staff',
                        'score': 4.0,
                        'out_of': 5
                    }]
                }]
            }
        }
        index = create_index(document)

        fields = index['accommodation.units[].ratings[].aspect']
        assert len(fields) == 4
        assert fields[0].name == 'accommodation.units[0].ratings[0].aspect'
        assert fields[0].value == 'general'
        assert fields[1].name == 'accommodation.units[0].ratings[1].aspect'
        assert fields[1].value == 'cleanliness'
        assert fields[2].name == 'accommodation.units[1].ratings[0].aspect'
        assert fields[2].value == 'general'
        assert fields[3].name == 'accommodation.units[1].ratings[1].aspect'
        assert fields[3].value == 'staff'

        fields = index['accommodation.units[].ratings[].score']
        assert len(fields) == 4
        assert fields[0].name == 'accommodation.units[0].ratings[0].score'
        assert fields[0].value == 3.7
        assert fields[1].name == 'accommodation.units[0].ratings[1].score'
        assert fields[1].value == 4.1
        assert fields[2].name == 'accommodation.units[1].ratings[0].score'
        assert fields[2].value == 4.4
        assert fields[3].name == 'accommodation.units[1].ratings[1].score'
        assert fields[3].value == 4.0

        fields = index['accommodation.units[].ratings[].out_of']
        assert len(fields) == 1
        assert fields[0].name == 'accommodation.units[1].ratings[1].out_of'
        assert fields[0].value == 5
    
    def test_it_types_objects(self):
        document = {
            'metadata': {}
        }
        index = create_index(document)

        assert index['metadata'][0].type == 'object'
    
    def test_it_types_lists(self):
        document = {
            'accommodation': {
                'payment_methods': []
            }
        }
        index = create_index(document)

        assert index['accommodation.payment_methods'][0].type == 'list'
    
    def test_it_types_scalars(self):
        document = {
            'metadata': {
                'accommodation_id': 1
            }
        }
        index = create_index(document)

        assert index['metadata.accommodation_id'][0].type == 'scalar'
    
    def test_it_types_list_elements(self):
        document = {
            'accommodation': {
                'ratings': [ {} ]
            }
        }
        index = create_index(document)

        assert index['accommodation.ratings[]'][0].type == 'object'
    
    def test_it_stores_the_values_of_a_heterogeneous_list(self):
        document = {
            'amalgam': [ {}, 0, [] ]
        }
        index = create_index(document)

        fields = index['amalgam[]']
        assert len(fields) == 3
        assert fields[0].name == 'amalgam[0]'
        assert fields[0].value == {}
        assert fields[1].name == 'amalgam[1]'
        assert fields[1].value == 0
        assert fields[2].name == 'amalgam[2]'
        assert fields[2].value == []
    
    def test_it_stores_the_values_of_an_object_in_a_heterogeneous_list(self):
        document = {
            'amalgam': [ { 'metal': 'mercury' }, 0, { 'metal': 'tin' } ]
        }
        index = create_index(document)

        fields = index['amalgam[].metal']
        assert len(fields) == 2
        assert fields[0].name == 'amalgam[0].metal'
        assert fields[0].value == 'mercury'
        assert fields[1].name == 'amalgam[2].metal'
        assert fields[1].value == 'tin'
    
    def test_it_extracts_path_from_nested_list(self):
        document = {
            'matrix': [[],[],[]]
        }
        index = create_index(document)

        assert 'matrix[][]' in index