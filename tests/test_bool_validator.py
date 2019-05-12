from type_validators import validate_bool

class TestBooleanValidator:
    def test_it_accepts_a_bool(self):
        message = validate_bool('has_bathroom', True)

        assert message is None
    
    def test_it_reports_a_non_bool(self):
        message = validate_bool('has_bathroom', 'yes')
        
        assert message.type == 'invalid_type'
        assert message.field == 'has_bathroom'
        assert message.expected == 'boolean'