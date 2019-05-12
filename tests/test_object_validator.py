from type_validators import validate_object

class TestObjectValidator:
    def test_it_accepts_an_object(self):
        field = 'accommodation'
        value = {}

        message = validate_object(field, value)

        assert message is None
    
    def test_it_reports_a_non_object(self):
        field = 'accommodation'
        value = 12

        message = validate_object(field, value)

        assert message.type == 'invalid_type'
        assert message.field == 'accommodation'
        assert message.expected == 'object'