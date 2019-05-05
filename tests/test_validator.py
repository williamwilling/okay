from validator import Validator

class TestValidator:
    def test_accepts_any_document_when_the_schema_is_empty(self):
        def schema(validator):
            pass
        
        document = {}
        validator = Validator(schema)
        is_valid = validator.validate(document)

        assert is_valid