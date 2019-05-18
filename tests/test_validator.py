import pytest
from validator import Validator

class TestValidator:
    def test_it_accepts_any_document_when_the_schema_is_empty(self):
        document = {}
        validator = Validator(empty_schema)
        is_valid = validator.validate(document)

        assert is_valid
    
    def test_it_raises_when_document_is_not_a_dictionary(self):
        document = ''
        validator = Validator(empty_schema)
        with pytest.raises(TypeError):
            validator.validate(document)
    
    def test_it_reports_a_missing_required_top_level_field(self):
        def schema(validator):
            validator.required('metadata')

        document = {}
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert not is_valid
        assert len(validator.messages) == 1
        message = validator.messages[0]
        assert message.type == 'missing_field'
        assert message.field == 'metadata'
    
    def test_it_accepts_a_required_top_level_field(self):
        def schema(validator):
            validator.required('metadata')
        
        document = { 'metadata': True }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []
    
    def test_it_reports_an_extra_top_level_field(self):
        document = { 'metadata': True }
        validator = Validator(empty_schema)
        is_valid = validator.validate(document)

        assert not is_valid
        assert len(validator.messages) == 1
        message = validator.messages[0]
        assert message.type == 'extra_field'
        assert message.field == 'metadata'
    
    def test_it_accepts_a_missing_optional_top_level_field(self):
        def schema(validator):
            validator.optional('trace')
        
        document = {}
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []

    def test_it_accepts_a_present_optional_top_level_field(self):
        def schema(validator):
            validator.optional('trace')
        
        document = { 'trace': True }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []
    
    def test_it_ignores_an_extra_top_level_field(self):
        def schema(validator):
            validator.ignore_extra_fields()
        
        document = { 'trace': True }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []
    
    def test_it_accepts_a_nested_required_field(self):
        def schema(validator):
            validator.required('accommodation.geo.latitude')
        
        document = {
            'accommodation': {
                'geo': {
                    'latitude': '12.5345'
                }
            }
        }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []

    def test_it_reports_a_missing_required_field(self):
        def schema(validator):
            validator.required('accommodation.name')
        
        document = { 'accommodation': {} }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert not is_valid
        assert len(validator.messages) == 1
        message = validator.messages[0]
        assert message.type == 'missing_field'
        assert message.field == 'accommodation.name'
    
    def test_it_accepts_a_missing_required_field_if_its_parent_is_missing(self):
        def schema(validator):
            validator.required('accommodation.name')
        
        document = {}
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []
    
    def test_it_reports_if_parent_field_is_not_an_object(self):
        def schema(validator):
            validator.required('accommodation.name')
        
        document = { 'accommodation': 'name' }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert not is_valid
        assert len(validator.messages) == 1
        message = validator.messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'accommodation'
        assert message.expected == 'object'
    
    def test_it_skips_nested_field_if_required_parent_is_missing(self):
        def schema(validator):
            validator.required('accommodation')
            validator.required('accommodation.name')

        document = {}
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert not is_valid
        assert len(validator.messages) == 1
        message = validator.messages[0]
        assert message.field == 'accommodation'
    
    def test_it_reports_a_parent_that_is_not_an_object(self):
        def schema(validator):
            validator.required('accommodation.geo.latitude')
        
        document = { 'accommodation': True }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert not is_valid
        assert len(validator.messages) == 1
        message = validator.messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'accommodation'
        assert message.expected == 'object'
    
    def test_it_accepts_a_required_object_with_the_correct_type(self):
        def schema(validator):
            validator.required('accommodation', type='object')
        
        document = { 'accommodation': {} }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []
    
    def test_it_reports_a_required_object_with_the_incorrect_type(self):
        def schema(validator):
            validator.required('accommodation', type='object')
        
        document = { 'accommodation': True }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert not is_valid
        assert len(validator.messages) == 1
        message = validator.messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'accommodation'
        assert message.expected == 'object'
    
    def test_it_accepts_an_optional_object_with_the_correct_type(self):
        def schema(validator):
            validator.optional('trace', type='object')
        
        document = { 'trace': {} }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []
    
    def test_it_reports_an_optional_object_with_the_incorrect_type(self):
        def schema(validator):
            validator.optional('trace', type='object')
        
        document = { 'trace': True }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert not is_valid
        assert len(validator.messages) == 1
        message = validator.messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'trace'
        assert message.expected == 'object'
    
    def test_it_accepts_a_value_with_custom_type(self):
        def schema(validator):
            def custom_validator(field, value):
                pass
            
            validator.required('accommodation', type='custom', validator=custom_validator)
        
        document = { 'accommodation': {} }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []
    
    def test_it_accepts_a_value_with_number_type(self):
        def schema(validator):
            validator.required('stars', type='number', min=0, max=5)
        
        document = { 'stars': 3 }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []
    
    def test_it_accepts_a_value_with_string_type(self):
        def schema(validator):
            validator.required('unit', type='string', options=['sqm', 'sqft'])
        
        document = { 'unit': 'sqft' }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []
    
    def test_it_accepts_a_value_with_bool_type(self):
        def schema(validator):
            validator.required('has_bathroom', type='bool')
        
        document = { 'has_bathroom': False }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []
    
    def test_it_accepts_a_value_with_int_type(self):
        def schema(validator):
            validator.required('stars', type='int', min=0, max=5)
        
        document = { 'stars': 4 }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []
    
    def test_it_accepts_value_with_list_type(self):
        def schema(validator):
            validator.required('rooms', type='list')
        
        document = { 'rooms': [] }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []
    
    def test_it_accepts_list_of_valid_scalars(self):
        def schema(validator):
            validator.required('scores[]', type='number')
        
        document = { 'scores': [ 1, 2, 3 ]}
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []
    
    def test_it_reports_list_of_invalid_scalars(self):
        def schema(validator):
            validator.required('scores[]', type='number')
        
        document = { 'scores': [ 1, 'good', 4, 'excellent' ]}
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert not is_valid
        assert len(validator.messages) == 2
        message = validator.messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'scores[1]'
        assert message.expected == 'number'
    
    def test_it_accepts_valid_objects_in_a_list(self):
        def schema(validator):
            validator.required('accommodation.ratings[].aspect', type='string')
        
        document = {
            'accommodation': {
                'ratings': [{
                    'aspect': 'cleanliness'
                }]
            }
        }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid
        assert validator.messages == []
    
    def test_it_rejects_invalid_objects_in_a_list(self):
        def schema(validator):
            validator.required('accommodation.ratings[].score', type='number', max=5)
        
        document = {
            'accommodation': {
                'ratings': [{
                    'score': 3
                }, {
                    'score': 'excellent'
                }, {
                    'score': 6
                }]
            }
        }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert not is_valid
        assert len(validator.messages) == 2
        message = validator.messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'accommodation.ratings[1].score'
        assert message.expected == 'number'
        message = validator.messages[1]
        assert message.type == 'number_too_large'
        assert message.field == 'accommodation.ratings[2].score'
        assert message.expected == 5
    
    def test_it_rejects_object_with_missing_fields_in_a_list(self):
        def schema(validator):
            validator.required('accommodation.ratings[].score', type='number')
        
        document = {
            'accommodation': {
                'ratings': [{}]
            }
        }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert not is_valid
        assert len(validator.messages) == 1
        message = validator.messages[0]
        assert message.type == 'missing_field'
        assert message.field == 'accommodation.ratings[0].score'
    
    def test_it_rejects_multiple_objects_with_missing_fields_in_a_list(self):
        def schema(validator):
            validator.required('accommodation.ratings[].score', type='number')
        
        document = {
            'accommodation': {
                'ratings': [{}, {}]
            }
        }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert not is_valid
        assert len(validator.messages) == 2
    
    def test_it_rejects_non_objects_in_a_list(self):
        def schema(validator):
            validator.required('ratings[].aspect', type='string')
        
        document = {
            'ratings': [{ 'aspect': 'good' }, -1]
        }
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert not is_valid
        assert len(validator.messages) == 1
        message = validator.messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'ratings[1]'
        assert message.expected == 'object'


def empty_schema(validator):
    pass