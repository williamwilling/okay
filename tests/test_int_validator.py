from okay.type_validators import IntValidator

class TestIntValidator:
    def test_it_accepts_an_int(self):
        validate_int = IntValidator()

        message = validate_int('room_count', 3)

        assert message is None
    
    def test_it_reports_a_non_int(self):
        validate_int = IntValidator()

        message = validate_int('room_count', 'many')

        assert message.type == 'invalid_type'
        assert message.field == 'room_count'
        assert message.expected == 'int'
    
    def test_it_accepts_a_floating_point_without_fraction(self):
        validate_int = IntValidator()

        message = validate_int('vote_count', 12.0)

        assert message is None
    
    def test_it_reports_a_floating_point_with_fraction(self):
        validate_int = IntValidator()

        message = validate_int('vote_count', 12.7)

        assert message.type == 'invalid_type'
        assert message.field == 'vote_count'
        assert message.expected == 'int'
    
    def test_it_accepts_an_int_in_a_specified_range(self):
        validate_int = IntValidator(min=0, max=5)

        message = validate_int('score', 3)
        
        assert message is None