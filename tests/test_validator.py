import pytest
from okay import validate, SchemaError, Message
from okay.schema import *

class TestValidator:
    def test_it_accepts_any_document_when_the_schema_is_empty(self):
        document = {}
        messages = validate(empty_schema, document)

        assert messages == []
    
    def test_it_reports_a_missing_required_top_level_field(self):
        def schema():
            required('metadata')

        document = {}
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'missing_field'
        assert message.field == 'metadata'
    
    def test_it_accepts_a_required_top_level_field(self):
        def schema():
            required('metadata')
        
        document = { 'metadata': True }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_reports_an_extra_top_level_field(self):
        document = { 'metadata': True }
        messages = validate(empty_schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'extra_field'
        assert message.field == 'metadata'
    
    def test_it_accepts_a_missing_optional_top_level_field(self):
        def schema():
            optional('trace')
        
        document = {}
        messages = validate(schema, document)

        assert messages == []

    def test_it_accepts_a_present_optional_top_level_field(self):
        def schema():
            optional('trace')
        
        document = { 'trace': True }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_ignores_an_extra_top_level_field(self):
        def schema():
            ignore_extra_fields()
        
        document = { 'trace': True }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_accepts_a_nested_required_field(self):
        def schema():
            required('accommodation.geo.latitude')
        
        document = {
            'accommodation': {
                'geo': {
                    'latitude': '12.5345'
                }
            }
        }
        messages = validate(schema, document)

        assert messages == []

    def test_it_reports_a_missing_required_field(self):
        def schema():
            required('accommodation.name')
        
        document = { 'accommodation': {} }
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'missing_field'
        assert message.field == 'accommodation.name'
    
    def test_it_accepts_a_missing_required_field_if_its_parent_is_missing(self):
        def schema():
            required('accommodation.name')
        
        document = {}
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_reports_if_parent_field_is_not_an_object(self):
        def schema():
            required('accommodation.name')
        
        document = { 'accommodation': 'name' }
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'accommodation'
        assert message.expected == {
            'type': 'object'
        }
    
    def test_it_reports_if_field_with_list_as_parent_is_missing(self):
        def schema():
            required('accommodation.ratings[].score')
        
        document = {
            'accommodation': {
                'ratings': [ { 'score': 3.9 }, {} ]
            }
        }

        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'missing_field'
        assert message.field == 'accommodation.ratings[1].score'
    
    def test_it_reports_if_parent_field_inside_list_is_not_an_object(self):
        def schema():
            required('accommodation.ratings[].score')
        
        document = {
            'accommodation': {
                'ratings': [ { 'score': 3.9 }, 4.2 ]
            }
        }

        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'accommodation.ratings[1]'
        assert message.expected == {
            'type': 'object'
        }
    
    def test_it_skips_nested_field_if_required_parent_is_missing(self):
        def schema():
            required('accommodation')
            required('accommodation.name')

        document = {}
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.field == 'accommodation'
    
    def test_it_accepts_a_required_object_with_the_correct_type(self):
        def schema():
            required('accommodation', type='object')
        
        document = { 'accommodation': {} }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_reports_a_required_object_with_the_incorrect_type(self):
        def schema():
            required('accommodation', type='object')
        
        document = { 'accommodation': True }
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'accommodation'
        assert message.expected == {
            'type': 'object'
        }
    
    def test_it_accepts_an_optional_object_with_the_correct_type(self):
        def schema():
            optional('trace', type='object')
        
        document = { 'trace': {} }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_reports_an_optional_object_with_the_incorrect_type(self):
        def schema():
            optional('trace', type='object')
        
        document = { 'trace': True }
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'trace'
        assert message.expected == {
            'type': 'object'
        }
    
    def test_it_accepts_a_value_with_custom_type(self):
        def schema():
            def custom_validator(field, value):
                pass
            
            required('accommodation', type='custom', validator=custom_validator)
        
        document = { 'accommodation': {} }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_accepts_a_value_with_number_type(self):
        def schema():
            required('stars', type='number', min=0, max=5)
        
        document = { 'stars': 3 }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_accepts_a_value_with_string_type(self):
        def schema():
            required('unit', type='string', options=['sqm', 'sqft'])
        
        document = { 'unit': 'sqft' }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_accepts_a_value_with_bool_type(self):
        def schema():
            required('has_bathroom', type='bool')
        
        document = { 'has_bathroom': False }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_accepts_a_value_with_int_type(self):
        def schema():
            required('stars', type='int', min=0, max=5)
        
        document = { 'stars': 4 }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_accepts_value_with_list_type(self):
        def schema():
            required('rooms', type='list')
        
        document = { 'rooms': [] }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_accepts_list_of_valid_scalars(self):
        def schema():
            required('scores[]', type='number')
        
        document = { 'scores': [ 1, 2, 3 ]}
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_reports_list_of_invalid_scalars(self):
        def schema():
            required('scores[]', type='number')
        
        document = { 'scores': [ 1, 'good', 4, 'excellent' ]}
        messages = validate(schema, document)

        assert len(messages) == 2
        message = messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'scores[1]'
        assert message.expected == {
            'type': 'number'
        }
    
    def test_it_accepts_valid_objects_in_a_list(self):
        def schema():
            required('accommodation.ratings[].aspect', type='string')
        
        document = {
            'accommodation': {
                'ratings': [{
                    'aspect': 'cleanliness'
                }]
            }
        }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_reports_invalid_objects_in_a_list(self):
        def schema():
            required('accommodation.ratings[].score', type='number', max=5)
        
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
        messages = validate(schema, document)

        assert len(messages) == 2
        message = messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'accommodation.ratings[1].score'
        assert message.expected == {
            'type': 'number'
        }
        message = messages[1]
        assert message.type == 'number_too_large'
        assert message.field == 'accommodation.ratings[2].score'
        assert message.expected == {
            'max': 5,
            'min': None,
            'options': None
        }
    
    def test_it_reports_object_with_missing_fields_in_a_list(self):
        def schema():
            required('accommodation.ratings[].score', type='number')
        
        document = {
            'accommodation': {
                'ratings': [{}]
            }
        }
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'missing_field'
        assert message.field == 'accommodation.ratings[0].score'
    
    def test_it_reports_multiple_objects_with_missing_fields_in_a_list(self):
        def schema():
            required('accommodation.ratings[].score', type='number')
        
        document = {
            'accommodation': {
                'ratings': [{}, {}]
            }
        }
        messages = validate(schema, document)

        assert len(messages) == 2
    
    def test_it_reports_non_objects_in_a_list(self):
        def schema():
            required('ratings[].aspect', type='string')
        
        document = {
            'ratings': [{ 'aspect': 'good' }, -1]
        }
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'ratings[1]'
        assert message.expected == {
            'type': 'object'
        }
    
    def test_it_accepts_a_list_of_scalars_inside_a_list_of_objects(self):
        def schema():
            required('facilities[].subtype[]', type='string')
        
        document = {
            'facilities': [{
                'subtype': [ 'indoor' ]
            }]
        }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_accepts_a_list_of_objects_inside_a_list_objects(self):
        def schema():
            required('rooms[].facilities[].type')
        
        document = {
            'rooms': [{
                'facilities': [{
                    'type': 'pool'
                }]
            }]
        }
        messages = validate(schema, document)

        assert messages == []

    def test_it_reports_missing_list(self):
        def schema():
            required('scores[]')
        
        document = {
            'scores': 5
        }
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'scores'
        assert message.expected == {
            'type': 'list'
        }
    
    def test_it_reports_missing_nested_list(self):
        def schema():
            required('facilities[].subtype[]', type='string')
        
        document = {
            'facilities': [{
                'subtype': 'indoor'
            }]
        }
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'facilities[0].subtype'
        assert message.expected == {
            'type': 'list'
        }
    
    def test_it_reports_invalid_value_in_nested_list(self):
        def schema():
            required('rooms[].facilities[].type', 'string')
        
        document = {
            'rooms': [{
                'facilities': [{
                    'type': 'pool'
                }, {
                    'type': 0
                }]
            }]
        }
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'rooms[0].facilities[1].type'
        assert message.expected == {
            'type': 'string'
        }
    
    def test_it_accepts_a_nested_list_of_scalars(self):
        def schema():
            required('matrix[][]', 'number')
        
        document = {
            'matrix': [
                [ 1, 2, 3 ],
                [ 4, 5, 6 ]
            ]
        }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_reports_an_extra_nested_field(self):
        def schema():
            optional('accommodation')
        
        document = {
            'accommodation': {
                'name': 'Hotel'
            }
        }
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'extra_field'
        assert message.field == 'accommodation.name'

    def test_it_reports_an_extra_field_nested_in_a_list(self):
        def schema():
            required('ratings[].aspect')
        
        document = {
            'ratings': [{
                'aspect': 'staff'
            }, {
                'aspect': 'cleanliness',
                'score': 3
            }]
        }
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'extra_field'
        assert message.field == 'ratings[1].score'
    
    def test_it_adds_specified_values_to_missing_field_message(self):
        def schema():
            required('metadata')
        
        document = {}
        message_values = {
            'source': 's3',
            'key': 'accommodations.json'
        }
        messages = validate(schema, document, message_values)

        assert len(messages) == 1
        message = messages[0]
        assert message.source == 's3'
        assert message.key == 'accommodations.json'
    
    def test_it_adds_specified_values_to_invalid_type_message(self):
        def schema():
            required('metadata', type='object')
            optional('accommodation', type='object')
        
        document = {
            'metadata': True,
            'accommodation': False
        }
        message_values = {
            'source': 's3',
            'key': 'accommodations.json'
        }
        messages = validate(schema, document, message_values)

        assert len(messages) == 2
        message = messages[0]
        assert message.source == 's3'
        assert message.key == 'accommodations.json'
        message = messages[1]
        assert message.source == 's3'
        assert message.key == 'accommodations.json'
    
    def test_it_adds_specified_values_to_invalid_parent_message(self):
        def schema():
            required('metadata.accommodation_id', type='object')
            optional('accommodation.name', type='object')
        
        document = {
            'metadata': True,
            'accommodation': False
        }
        message_values = {
            'source': 's3',
            'key': 'accommodations.json'
        }
        messages = validate(schema, document, message_values)

        assert len(messages) == 2
        message = messages[0]
        assert message.source == 's3'
        assert message.key == 'accommodations.json'
        message = messages[1]
        assert message.source == 's3'
        assert message.key == 'accommodations.json'
    
    def test_it_adds_specified_values_to_extra_field_message(self):
        def schema():
            pass
        
        document = {
            'review': {}
        }
        message_values = {
            'source': 's3',
            'key': 'accommodations.json'
        }
        messages = validate(schema, document, message_values)

        assert len(messages) == 1
        message = messages[0]
        assert message.source == 's3'
        assert message.key == 'accommodations.json'
    
    def test_it_makes_required_available_to_schema_outside_of_validator_instance(self):
        def schema():
            required('metadata')
            required('accommodation')
        
        document = {
            'metadata': {}
        }
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'missing_field'
        assert message.field == 'accommodation'
    
    def test_it_makes_optional_available_to_schema_outside_of_validator_instance(self):
        def schema():
            optional('metadata', type='object')
            optional('accommodation')
        
        document = {
            'metadata': 8
        }
        messages = validate(schema, document)

        assert len(messages) == 1
        message = messages[0]
        assert message.type == 'invalid_type'
        assert message.field == 'metadata'
    
    def test_it_makes_ignore_extra_fields_available_to_schema_outside_of_validator_instance(self):
        def schema():
            ignore_extra_fields()
        
        document = {
            'metadata': {}
        }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_accepts_a_parameterless_schema(self):
        def schema():
            pass
        
        document = {}
        messages = validate(schema, document)

        assert messages == []

    def test_it_raises_when_type_is_invalid(self):
        def schema():
            required('metadata', type='unknown')
        
        document = {
            'metadata': {}
        }
        with pytest.raises(SchemaError):
            validate(schema, document)
    
    def test_it_raises_when_optional_field_is_already_required(self):
        def schema():
            required('metadata', type='object')
            optional('metadata', type='object')
        
        document = {
            'metadata': {}
        }
        with pytest.raises(SchemaError):
            validate(schema, document)
    
    def test_it_raises_when_required_field_is_already_optional(self):
        def schema():
            optional('accommodation', type='object')
            required('accommodation', type='object')
        
        document = {
            'accommodation': {}
        }
        with pytest.raises(SchemaError):
            validate(schema, document)
    
    def test_it_raises_when_list_is_optional_and_elements_are_required(self):
        def schema():
            optional('scores', type='list')
            required('scores[]')
        
        document = {
            'scores': []
        }
        with pytest.raises(SchemaError):
            validate(schema, document)
    
    def test_it_raises_when_list_is_required_and_elements_are_optional(self):
        def schema():
            required('scores', type='list')
            optional('scores[]')
        
        document = {
            'scores': []
        }
        with pytest.raises(SchemaError):
            validate(schema, document)
    
    def test_it_raises_schemaerror_when_schema_raises(self):
        def schema():
            raise RuntimeError()
        
        document = {}
        with pytest.raises(SchemaError) as exception_info:
            validate(schema, document)
        
        assert type(exception_info.value.__cause__) == RuntimeError
    
    def test_it_doesnt_wrap_schemaerror(self):
        def schema():
            def validator(field, name):
                raise RuntimeError()
            
            optional('accommodation', type='custom', validator=validator)
        
        document = {
            'accommodation': {}
        }
        with pytest.raises(SchemaError) as exception_info:
            validate(schema, document)
        
        assert type(exception_info.value.__cause__) == RuntimeError
    
    def test_it_runs_multiple_type_validators_on_a_single_field(self):
        def cost_validator(field, value):
            if not isinstance(value, dict):
                return

            if value['is_free'] and value['price'] > 0:
                return Message(
                    type='free_and_price',
                    field=field
                )

        def schema():
            optional('accommodation.facilities[].cost', type='object')
            optional('accommodation.facilities[].cost', type='custom', validator=cost_validator)
            ignore_extra_fields()
        
        document = {
            'accommodation': {
                'facilities': [{
                    'type': 'pool',
                    'cost': 0
                }, {
                    'type': 'wifi',
                    'cost': {
                        'is_free': True,
                        'price': 5,
                        'currency': 'eur'
                    }
                }]
            }
        }

        messages = validate(schema, document)

        assert len(messages) == 2
        assert messages[0].type == 'invalid_type'
        assert messages[1].type == 'free_and_price'

    def test_it_accepts_an_optional_nullable_null_value(self):
        def schema():
            optional('metadata', type='object?')
        
        document = { 'metadata': None }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_reports_an_optional_non_nullable_null_value(self):
        def schema():
            optional('metadata', type='object')
        
        document = { 'metadata': None }
        messages = validate(schema, document)

        assert len(messages) == 1
        assert messages[0].type == 'null_value'
        assert messages[0].field == 'metadata'
        assert messages[0].expected == {
            'type': 'object'
        }
    
    def test_it_accepts_a_required_nullable_null_value(self):
        def schema():
            required('metadata', type='object?')
        
        document = { 'metadata': None }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_reports_a_required_non_nullable_null_value(self):
        def schema():
            required('metadata', type='object')
        
        document = { 'metadata': None }
        messages = validate(schema, document)

        assert len(messages) == 1
        assert messages[0].type == 'null_value'
        assert messages[0].field == 'metadata'
        assert messages[0].expected == {
            'type': 'object'
        }
    
    def test_it_accepts_a_typeless_nullable_null_value(self):
        def schema():
            optional('metadata', type='any?')
        
        document = { 'metadata': None }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_reports_a_typeless_non_nullable_null_value(self):
        def schema():
            optional('metadata', type='any')
        
        document = { 'metadata': None }
        messages = validate(schema, document)

        assert len(messages) == 1
        assert messages[0].type == 'null_value'
        assert messages[0].field == 'metadata'
        assert messages[0].expected == {
            'type': 'any'
        }
    
    def test_it_reports_required_null_value_by_default(self):
        def schema():
            required('metadata')
        
        document = { 'metadata': None }
        messages = validate(schema, document)

        assert len(messages) == 1
        assert messages[0].type == 'null_value'
        assert 'type' not in messages[0].expected
    
    def test_it_reports_optional_null_value_by_default(self):
        def schema():
            optional('metadata')
        
        document = { 'metadata': None }
        messages = validate(schema, document)

        assert len(messages) == 1
        assert messages[0].type == 'null_value'
        assert 'type' not in messages[0].expected
    
    def test_it_raises_when_nullable_field_is_already_non_nullable(self):
        def schema():
            optional('metadata', type='object')
            optional('metadata', type='object?')
        
        document = {}

        with pytest.raises(SchemaError):
            validate(schema, document)
    
    def test_it_raises_when_non_nullable_field_is_already_nullable(self):
        def schema():
            optional('metadata', type='object?')
            optional('metadata', type='object')
        
        document = {}

        with pytest.raises(SchemaError):
            validate(schema, document)
    
    def test_it_accepts_nullable_list_elements(self):
        def schema():
            required('values[]', type='number?')
        
        document = { 'values': [ None, None ] }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_reports_non_nullable_list_elements(self):
        def schema():
            required('values[]', type='number')
        
        document = { 'values': [ None, None ]}
        messages = validate(schema, document)

        assert len(messages) == 2
        assert messages[0].type == 'null_value'
        assert messages[0].field == 'values[0]'
        assert messages[1].type == 'null_value'
        assert messages[1].field == 'values[1]'
    
    def test_it_makes_required_list_non_nullable_by_default(self):
        def schema():
            required('values[]')
        
        document = { 'values': None }
        messages = validate(schema, document)

        assert len(messages) == 1
        assert messages[0].type == 'null_value'
        assert messages[0].field == 'values'
    
    def test_it_makes_optional_list_non_nullable_by_default(self):
        def schema():
            optional('values[]')
        
        document = { 'values': None }
        messages = validate(schema, document)

        assert len(messages) == 1
        assert messages[0].type == 'null_value'
        assert messages[0].field == 'values'
    
    def test_it_accepts_nullable_required_list_after_list_elements(self):
        def schema():
            required('values[]')
            required('values', type='list?')
        
        document = { 'values': None }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_accepts_nullable_required_list_before_list_elements(self):
        def schema():
            required('values', type='list?')
            required('values[]')
        
        document = { 'values': None }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_reports_non_nullable_optional_list(self):
        def schema():
            optional('values[]')
            optional('values', type='list')
        
        document = { 'values': None }
        messages = validate(schema, document)

        assert len(messages) == 1
        assert messages[0].type == 'null_value'
        assert messages[0].field == 'values'
    
    def test_it_makes_implicit_object_non_nullable(self):
        def schema():
            required('author.name')
        
        document = { 'author': None }
        messages = validate(schema, document)

        assert len(messages) == 2
        assert messages[0].type == 'null_value'
        assert messages[0].field == 'author'
        assert messages[0].expected == {
            'type': 'object'
        }
        assert messages[1].type == 'missing_field'
        assert messages[1].field == 'author.name'
    
    def test_it_accepts_nullable_object_after_implicit_object(self):
        def schema():
            required('author.name')
            required('author', type='object?')
        
        document = { 'author': None }
        messages = validate(schema, document)

        assert messages == []
    
    def test_it_accepts_nullable_object_before_implicit_object(self):
        def schema():
            required('author', type='object?')
            required('author.name')
        
        document = { 'author': None }
        messages = validate(schema, document)

        assert messages == []

    def test_it_raises_when_root_is_optional(self):
        def schema():
            optional('.')
        
        document = {}
        
        with pytest.raises(SchemaError):
            validate(schema, document)
    
    def test_it_passes_root_to_custom_validator(self):
        custom_value = None
        def validate_root(field, value):
            nonlocal custom_value
            custom_value = value

        def schema():
            required('.', type='custom', validator=validate_root)

        document = { 'author': 'Vikram Seth' }        
        validate(schema, document)

        assert custom_value == document

    def test_it_accepts_a_number_as_root(self):
        def schema():
            required('.', type='number')
        
        document = 12.8
        messages = validate(schema, document)

        assert len(messages) == 0
    
    def test_it_accepts_nullable_root(self):
        def schema():
            required('.', type='any?')
        
        document = None
        messages = validate(schema, document)

        assert len(messages) == 0

    def test_it_reports_a_null_parent_when_parent_is_a_non_nullable_object(self):
        def schema():
            required('author', type='object')
            required('author.name')
        
        document = { 'author': None }
        messages = validate(schema, document)

        assert len(messages) == 2
        message = messages[0]
        assert message.type == 'null_value'
        assert message.field == 'author'
        assert message.expected == {
            'type': 'object'
        }
        message = messages[1]
        assert message.type == 'missing_field'
        assert message.field == 'author.name'
    
    def test_it_accepts_a_null_parent_when_parent_is_a_nullable_object(self):
        def schema():
            required('author', type='object?')
            required('author.name')
        
        document = { 'author': None }
        messages = validate(schema, document)

        assert messages == []
        

def empty_schema():
    pass