from okay.type_validators import BoolValidator

class TestBooleanValidator:
    def test_it_accepts_a_bool(self):
        validate_bool = BoolValidator()

        message = validate_bool('has_bathroom', True)

        assert message is None
    
    def test_it_reports_a_non_bool(self):
        validate_bool = BoolValidator()
        
        message = validate_bool('has_bathroom', 'yes')
        
        assert message.type == 'invalid_type'
        assert message.field == 'has_bathroom'
        assert message.expected == {
            'type': 'bool'
        }