from type_validators import validate_string

class TestStringValidator:
    def test_it_accepts_a_string(self):
        message = validate_string('city', 'Amsterdam')

        assert message is None
    
    def test_it_reports_a_non_string(self):
        message = validate_string('city', True)

        assert message.type == 'invalid_type'
        assert message.field == 'city'
        assert message.expected == 'string'
    
    def test_it_accepts_a_string_matching_a_regex(self):
        message = validate_string('phone', '+00 (0)00-0000', regex=r'[\d\(\)\+\- ]+')
        
        assert message is None
    
    def test_it_reports_a_string_not_matching_a_regex(self):
        message = validate_string('phone', '+xx (x)xx-xxxx', regex=r'[\d\(\)\+\- ]+')
        
        assert message.type == 'no_match'
        assert message.field == 'phone'
        assert message.expected == r'[\d\(\)\+\- ]+'
    
    def test_it_accepts_a_string_in_a_list_of_options(self):
        message = validate_string('unit', 'sqm', options=['sqm', 'sqft'])

        assert message is None
    
    def test_it_reports_a_string_not_in_a_list_of_options(self):
        message = validate_string('unit', 'm2', options=['sqm', 'sqft'])

        assert message.type == 'invalid_option'
        assert message.field == 'unit'
        assert message.expected == ['sqm', 'sqft']