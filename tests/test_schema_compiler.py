import pytest
from okay import SchemaError
from okay.schema_compiler import required, optional, compile

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
    
    def test_it_raises_when_list_and_list_is_optional_and_elements_are_required(self):
        def schema():
            optional('accommodation.payment_methods', type='list')
            required('accommodation.payment_methods[]')
        
        with pytest.raises(SchemaError) as exception_info:
            compile(schema)
        
        exception = exception_info.value
        assert exception.type == 'already_optional'
        assert exception.field == 'accommodation.payment_methods'

    def test_it_raises_when_list_and_list_is_required_and_elements_are_optional(self):
        def schema():
            required('accommodation.payment_methods', type='list')
            optional('accommodation.payment_methods[]')
        
        with pytest.raises(SchemaError) as exception_info:
            compile(schema)
        
        exception = exception_info.value
        assert exception.type == 'already_required'
        assert exception.field == 'accommodation.payment_methods'