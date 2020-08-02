import pytest
from okay import SchemaError, Message
from okay.schema_compiler import required, optional, compile
from okay.type_validators import AnyValidator, IntValidator, ObjectValidator, CustomValidator, StringValidator, NumberValidator, ListValidator

class TestSchemaCompiler:
    def test_it_extracts_no_names_for_empty_schema(self):
        def schema():
            pass
        
        compiled_schema = compile(schema)

        assert compiled_schema.fields == {}
    
    def test_it_extracts_required_top_level_name(self):
        def schema():
            required('accommodation')
        
        compiled_schema = compile(schema)

        assert 'accommodation' in compiled_schema.fields
    
    def test_it_extracts_optional_top_level_name(self):
        def schema():
            optional('metadata')

        compiled_schema = compile(schema)

        assert 'metadata' in compiled_schema.fields
    
    def test_it_extracts_nested_names(self):
        def schema():
            required('accommodation.geo.longitude')
        
        compiled_schema = compile(schema)

        assert 'accommodation' in compiled_schema.fields
        assert 'accommodation.geo' in compiled_schema.fields
        assert 'accommodation.geo.longitude' in compiled_schema.fields
    
    def test_it_extracts_list_names(self):
        def schema():
            required('accommodation.payment_methods[]')

        compiled_schema = compile(schema)

        assert 'accommodation' in compiled_schema.fields
        assert 'accommodation.payment_methods' in compiled_schema.fields
        assert 'accommodation.payment_methods[]' in compiled_schema.fields
    
    def test_it_extracts_nested_names_from_lists(self):
        def schema():
            required('accommodation.ratings[].score')
        
        compiled_schema = compile(schema)

        assert 'accommodation' in compiled_schema.fields
        assert 'accommodation.ratings' in compiled_schema.fields
        assert 'accommodation.ratings[]' in compiled_schema.fields
        assert 'accommodation.ratings[].score' in compiled_schema.fields
    
    def test_it_extracts_names_from_nested_lists(self):
        def schema():
            required('accommodation.units[].review.ratings[].score')
        
        compiled_schema = compile(schema)

        assert 'accommodation' in compiled_schema.fields
        assert 'accommodation.units' in compiled_schema.fields
        assert 'accommodation.units[]' in compiled_schema.fields
        assert 'accommodation.units[].review' in compiled_schema.fields
        assert 'accommodation.units[].review.ratings[]' in compiled_schema.fields
        assert 'accommodation.units[].review.ratings[].score' in compiled_schema.fields
    
    def test_it_extracts_element_name_from_list(self):
        def schema():
            required('accommodation.units', type='list')
        
        compiled_schema = compile(schema)

        assert 'accommodation.units[]' in compiled_schema.fields
    
    def test_it_extracts_nested_list_names(self):
        def schema():
            required('matrix3d[][]', type='list')
        
        compiled_schema = compile(schema)

        assert 'matrix3d' in compiled_schema.fields
        assert 'matrix3d[]' in compiled_schema.fields
        assert 'matrix3d[][]' in compiled_schema.fields
        assert 'matrix3d[][][]' in compiled_schema.fields
    
    def test_it_extracts_names_from_multiple_rules(self):
        def schema():
            required('accommodation.name')
            required('accommodation.ratings[].aspect')
            required('accommodation.ratings[].score')
        
        compiled_schema = compile(schema)

        assert 'accommodation' in compiled_schema.fields
        assert 'accommodation.name' in compiled_schema.fields
        assert 'accommodation.ratings' in compiled_schema.fields
        assert 'accommodation.ratings[]' in compiled_schema.fields
        assert 'accommodation.ratings[].aspect' in compiled_schema.fields
        assert 'accommodation.ratings[].score' in compiled_schema.fields
    
    def test_it_marks_a_top_level_field_as_required(self):
        def schema():
            required('accommodation')
        
        compiled_schema = compile(schema)

        assert compiled_schema.fields['accommodation'].strictness == 'required'
    
    def test_it_marks_a_top_level_field_as_optional(self):
        def schema():
            optional('accommodation')
        
        compiled_schema = compile(schema)

        assert compiled_schema.fields['accommodation'].strictness == 'optional'
    
    def test_it_marks_parents_of_a_nested_field_with_unknown_strictness(self):
        def schema():
            required('accommodation.check_in.from')
        
        compiled_schema = compile(schema)

        assert compiled_schema.fields['accommodation'].strictness == 'unknown'
        assert compiled_schema.fields['accommodation.check_in'].strictness == 'unknown'
        assert compiled_schema.fields['accommodation.check_in.from'].strictness == 'required'
    
    def test_it_marks_strictness_of_both_elements_and_list(self):
        def schema():
            required('accommodation.payment_methods[]')
        
        compiled_schema = compile(schema)

        assert compiled_schema.fields['accommodation.payment_methods'].strictness == 'required'
        assert compiled_schema.fields['accommodation.payment_methods[]'].strictness == 'required'
    
    def test_it_marks_strictness_of_both_list_and_elements(self):
        def schema():
            required('accommodation.payment_methods', type='list')
        
        compiled_schema = compile(schema)

        assert compiled_schema.fields['accommodation.payment_methods'].strictness == 'required'
        assert compiled_schema.fields['accommodation.payment_methods[]'].strictness == 'required'
    
    def test_it_marks_strictness_of_nested_lists(self):
        def schema():
            required('matrix3d[][]', type='list')
        
        compiled_schema = compile(schema)

        assert compiled_schema.fields['matrix3d'].strictness == 'required'
        assert compiled_schema.fields['matrix3d[]'].strictness == 'required'
        assert compiled_schema.fields['matrix3d[][]'].strictness == 'required'
        assert compiled_schema.fields['matrix3d[][][]'].strictness == 'required'
    
    def test_it_doesnt_mark_a_required_field_with_unknown_strictness(self):
        def schema():
            required('accommodation')
            required('accommodation.name')
        
        compiled_schema = compile(schema)

        assert compiled_schema.fields['accommodation'].strictness == 'required'

    def test_it_doesnt_mark_an_optional_field_with_unknown_strictness(self):
        def schema():
            optional('metadata')
            required('metadata.partner')
        
        compiled_schema = compile(schema)

        assert compiled_schema.fields['metadata'].strictness == 'optional'
    
    def test_it_raises_when_required_field_is_marked_optional(self):
        def schema():
            required('metadata')
            optional('metadata')
        
        with pytest.raises(SchemaError) as exception_info:
            compiled_schema = compile(schema)
        
        exception = exception_info.value
        assert exception.type == 'already_required'
        assert exception.field == 'metadata'
    
    def test_it_raises_when_optional_field_is_marked_required(self):
        def schema():
            optional('metadata')
            required('metadata')
        
        with pytest.raises(SchemaError) as exception_info:
            compile(schema)
        
        exception = exception_info.value
        assert exception.type == 'already_optional'
        assert exception.field == 'metadata'
    
    def test_it_raises_when_list_is_optional_and_elements_are_required(self):
        def schema():
            optional('accommodation.payment_methods', type='list')
            required('accommodation.payment_methods[]')
        
        with pytest.raises(SchemaError) as exception_info:
            compile(schema)
        
        exception = exception_info.value
        assert exception.type == 'already_optional'
        assert exception.field == 'accommodation.payment_methods'

    def test_it_raises_when_list_is_required_and_elements_are_optional(self):
        def schema():
            required('accommodation.payment_methods', type='list')
            optional('accommodation.payment_methods[]')
        
        with pytest.raises(SchemaError) as exception_info:
            compile(schema)
        
        exception = exception_info.value
        assert exception.type == 'already_required'
        assert exception.field == 'accommodation.payment_methods'
    
    def test_it_raises_when_elements_are_optional_and_list_is_required(self):
        def schema():
            optional('accommodation.payment_methods[]')
            required('accommodation.payment_methods', type='list')
        
        with pytest.raises(SchemaError) as exception_info:
            compile(schema)
        
        exception = exception_info.value
        assert exception.type == 'already_optional'
        assert exception.field == 'accommodation.payment_methods'
    
    def test_it_raises_when_elements_are_required_and_list_is_optional(self):
        def schema():
            required('accommodation.payment_methods[]')
            optional('accommodation.payment_methods', type='list')
        
        with pytest.raises(SchemaError) as exception_info:
            compile(schema)
        
        exception = exception_info.value
        assert exception.type == 'already_required'
        assert exception.field == 'accommodation.payment_methods'
    
    def test_it_caches_the_rule(self):
        def schema():
            required('metadata.accommodation_id', type='int')
        
        compiled_schema = compile(schema)

        rules = compiled_schema.fields['metadata.accommodation_id'].rules
        assert len(rules) == 1
        assert isinstance(rules[0].validate, IntValidator)
        rules = compiled_schema.fields['metadata'].rules
        assert len(rules) == 1
        assert isinstance(rules[0].validate, ObjectValidator)
    
    def test_it_caches_multiple_rules_on_the_same_field(self):
        def schema():
            def validate_rating(field, value):
                if field['out_of'] < field['score']:
                    return Message(
                        type='too_large',
                        field=field,
                        expected=field['out_of']
                    )
            
            required('rating', type='object')
            required('rating', type='custom', validator=validate_rating)
        
        compiled_schema = compile(schema)

        rules = compiled_schema.fields['rating'].rules
        assert len(rules) == 2
        assert isinstance(rules[0].validate, ObjectValidator)
        assert isinstance(rules[1].validate, CustomValidator)
    
    def test_it_caches_the_rule_on_list_elements(self):
        def schema():
            required('accommodation.scores[]', type='number')
        
        compiled_schema = compile(schema)

        rules = compiled_schema.fields['accommodation.scores'].rules
        assert len(rules) == 1
        assert isinstance(rules[0].validate, ListValidator)
        rules = compiled_schema.fields['accommodation.scores[]'].rules
        assert len(rules) == 1
        assert isinstance(rules[0].validate, NumberValidator)
    
    def test_it_caches_an_any_rule_for_rules_without_type(self):
        def schema():
            optional('metadata')
        
        compiled_schema = compile(schema)

        rules = compiled_schema.fields['metadata'].rules
        assert len(rules) == 1
        assert isinstance(rules[0].validate, AnyValidator)
    
    def test_it_caches_a_rule_that_supports_preprocessing(self):
        def schema():
            optional('accommodation.phone', type='string', regex=r'[\(\)\-\+ 0-9]+')
        
        compiled_schema = compile(schema)

        rules = compiled_schema.fields['accommodation.phone'].rules
        assert len(rules) == 1
        assert isinstance(rules[0].validate, StringValidator)
    
    def test_it_doesnt_cache_parents_object_rule_if_parent_already_has_object_rule(self):
        def schema():
            required('accommodation', 'object')
            optional('accommodation.name', 'string')
        
        compiled_schema = compile(schema)

        rules = compiled_schema.fields['accommodation'].rules
        assert len(rules) == 1

    def test_it_overwrites_object_rule_that_came_from_nested_field(self):
        def schema():
            optional('accommodation.name', 'string')
            required('accommodation', 'object')
        
        compiled_schema = compile(schema)

        rules = compiled_schema.fields['accommodation'].rules
        assert len(rules) == 1
    
    def test_it_doesnt_cache_parents_list_rule_if_parent_already_has_list_rule(self):
        def schema():
            required('accommodation.scores', 'list')
            required('accommodation.scores[]', 'number')
        
        compiled_schema = compile(schema)

        rules = compiled_schema.fields['accommodation.scores'].rules
        assert len(rules) == 1

    def test_it_overwrites_list_rule_that_came_from_child_of_list(self):
        def schema():
            required('accommodation.scores[]', 'number')
            required('accommodation.scores', 'list')
        
        compiled_schema = compile(schema)

        rules = compiled_schema.fields['accommodation.scores'].rules
        assert len(rules) == 1
    
    def test_it_raises_when_root_is_optional(self):
        def schema():
            optional('.')
        
        with pytest.raises(SchemaError) as exception_info:
            compile(schema)
        
        exception = exception_info.value
        assert exception.type == 'optional_not_allowed'
        assert exception.field == '.'
    
    def test_it_caches_the_any_rule(self):
        def schema():
            optional('metadata', type='any?')
        
        compiled_schema = compile(schema)

        field = compiled_schema.fields['metadata']
        assert field.nullable == True
        assert len(field.rules) == 1
        assert isinstance(field.rules[0].validate, AnyValidator)
    
    def test_it_makes_any_the_default_type(self):
        def schema():
            required('metadata')

        compiled_schema = compile(schema)

        field = compiled_schema.fields['metadata']
        assert len(field.rules) == 1
        assert isinstance(field.rules[0].validate, AnyValidator)

    def test_it_raises_when_nullable_field_is_marked_non_nullable(self):
        def schema():
            required('metadata', type='object?')
            required('metadata', type='object')
        
        with pytest.raises(SchemaError) as exception_info:
            compiled_schema = compile(schema)
        
        exception = exception_info.value
        assert exception.type == 'already_nullable'
        assert exception.field == 'metadata'
    
    def test_it_raises_when_non_nullable_field_is_marked_nullable(self):
        def schema():
            optional('metadata', type='object')
            optional('metadata', type='object?')
        
        with pytest.raises(SchemaError) as exception_info:
            compile(schema)
        
        exception = exception_info.value
        assert exception.type == 'already_non_nullable'
        assert exception.field == 'metadata'