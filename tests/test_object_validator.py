from okay.type_validators import ObjectValidator

class TestObjectValidator:
    def test_it_accepts_an_object(self):
        validate_object = ObjectValidator()
        field = 'accommodation'
        value = {}

        message = validate_object(field, value)

        assert message is None
    
    def test_it_reports_a_non_object(self):
        validate_object = ObjectValidator()
        field = 'accommodation'
        value = 12

        message = validate_object(field, value)

        assert message.type == 'invalid_type'
        assert message.field == 'accommodation'
        assert message.expected == {
            'type': 'object'
        }