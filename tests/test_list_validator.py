from type_validators import validate_list

class TestListValidator:
    def test_it_accepts_a_list(self):
        message = validate_list('rooms', [])

        assert message is None
    
    def test_it_reports_a_non_list(self):
        message = validate_list('rooms', 3)

        assert message.type == 'invalid_type'
        assert message.field == 'rooms'
        assert message.expected == 'list'
    
    def test_it_accepts_a_list_with_at_least_minimum_elements(self):
        message = validate_list('rooms', [ {} ], min=1)

        assert message is None
    
    def test_it_reports_a_list_with_less_than_minimum_elements(self):
        message = validate_list('rooms', [], min=1)

        assert message.type == 'too_few_elements'
        assert message.field == 'rooms'
        assert message.expected == 1
    
    def test_it_accepts_a_list_with_at_most_maximum_elements(self):
        message = validate_list('bathrooms', [ {} ], max=2)

        assert message is None
    
    def test_it_reports_a_list_with_more_than_maximum_elements(self):
        message = validate_list('bathrooms', [ {}, {}, {} ], max=2)

        assert message.type == 'too_many_elements'
        assert message.field == 'bathrooms'
        assert message.expected == 2