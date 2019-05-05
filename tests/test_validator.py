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


def empty_schema(validator):
    pass