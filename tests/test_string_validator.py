from okay.type_validators import StringValidator

class TestStringValidator:
    def test_it_accepts_a_string(self):
        validate_string = StringValidator()

        message = validate_string('city', 'Amsterdam')

        assert message is None
    
    def test_it_reports_a_non_string(self):
        validate_string = StringValidator()

        message = validate_string('city', True)

        assert message.type == 'invalid_type'
        assert message.field == 'city'
        assert message.expected == 'string'
    
    def test_it_accepts_a_string_matching_a_regex(self):
        validate_string = StringValidator(regex=r'[\d\(\)\+\- ]+')
        
        message = validate_string('phone', '+00 (0)00-0000')
        
        assert message is None
    
    def test_it_reports_a_string_not_matching_a_regex(self):
        validate_string = StringValidator(regex=r'[\d\(\)\+\- ]+')
        
        message = validate_string('phone', '+xx (x)xx-xxxx')
        
        assert message.type == 'no_match'
        assert message.field == 'phone'
        assert message.expected == r'[\d\(\)\+\- ]+'
    
    def test_it_accepts_a_string_in_a_list_of_options(self):
        validate_string = StringValidator(options=['sqm', 'sqft'])
        
        message = validate_string('unit', 'sqm')

        assert message is None
    
    def test_it_reports_a_string_not_in_a_list_of_options(self):
        validate_string = StringValidator(options=['sqm', 'sqft'])
        
        message = validate_string('unit', 'm2')

        assert message.type == 'invalid_option'
        assert message.field == 'unit'
        assert message.expected == ['sqm', 'sqft']
    
    def test_it_accepts_a_string_in_a_list_of_options_if_regex_doesnt_match(self):
        validate_string = StringValidator(regex=r'\+[\d\(\)\+\- ]+', options=['112'])
        
        message = validate_string('phone', '112')
        
        assert message is None
    
    def test_it_accepts_a_string_matching_a_regex_if_it_is_not_in_a_list_of_options(self):
        validate_string = StringValidator(regex=r'\+[\d\(\)\+\- ]+', options=['112'])
        
        message = validate_string('phone', '+00 (0)00-0000')
        
        assert message is None
    
    def test_it_reports_a_string_not_matching_a_regex_and_not_in_a_list_of_options(self):
        validate_string = StringValidator(regex=r'\+[\d\(\)\+\- ]+', options=['112'])
        
        message = validate_string('phone', '911')
        
        assert message.type == 'no_match'
        assert message.field == 'phone'
        assert message.expected == {
            'regex': r'\+[\d\(\)\+\- ]+',
            'options': ['112']
        }
    
    def test_it_accepts_a_string_in_a_list_of_case_insensitive_options(self):
        validate_string = StringValidator(options=['SQm', 'SQft'], case_sensitive=False)
        
        message = validate_string('unit', 'sqM')

        assert message is None
    
    def test_it_reports_a_string_in_a_list_of_case_sensitive_options(self):
        validate_string = StringValidator(options=['SQm', 'SQft'], case_sensitive=True)
        
        message = validate_string('unit', 'sqM')

        assert message.type == 'invalid_option'
        assert message.field == 'unit'
        assert message.expected == ['SQm', 'SQft']
    
    def test_it_accepts_a_string_in_a_list_of_case_insensitive_options_if_regex_doesnt_match(self):
        validate_string = StringValidator(regex=r'sq[a-z]+', options=['SQm', 'SQft'], case_sensitive=False)
        
        message = validate_string('unit', 'sqM')

        assert message is None
    
    def test_it_accepts_a_string_shorter_than_the_maximum_length(self):
        validate_string = StringValidator(max=5)

        message = validate_string('color', 'red')

        assert message is None
    
    def test_it_rejects_a_string_longer_than_the_maximum_length(self):
        validate_string = StringValidator(max=5)

        message = validate_string('color', 'yellow')

        assert message.type == 'string_too_long'
        assert message.field == 'color'
        assert message.expected == 5
    
    def test_it_accepts_a_string_longer_than_the_minimum_length(self):
        validate_string = StringValidator(min=4)

        message = validate_string('color', 'green')

        assert message is None
    
    def test_it_rejects_a_string_shorter_than_the_minimum_length(self):
        validate_string = StringValidator(min=4)

        message = validate_string('color', 'red')

        assert message.type == 'string_too_short'
        assert message.field == 'color'
        assert message.expected == 4
    
    def test_it_accepts_a_string_in_length_range_and_not_in_options(self):
        validate_string = StringValidator(min=2, max=5, options=['red', 'green', 'yellow'])

        message = validate_string('color', 'blue')

        assert message is None
    
    def test_it_accepts_a_string_in_options_and_outside_length_range(self):
        validate_string = StringValidator(min=2, max=5, options=['red', 'green', 'yellow'])

        message = validate_string('color', 'yellow')

        assert message is None

    def test_it_accepts_a_string_in_length_range_and_not_matching_a_regex(self):
        validate_string = StringValidator(min=2, max=5, regex=r'#[0-9a-f]{6}')

        message = validate_string('color', 'red')

        assert message is None
    
    def test_it_accepts_a_string_matching_a_regex_and_not_in_length_range(self):
        validate_string = StringValidator(min=2, max=5, regex=r'#[0-9a-f]{6}')

        message = validate_string('color', '#ff0000')

        assert message is None
    
    def test_it_reports_a_string_not_matching_a_regex_and_not_in_length_range(self):
        validate_string = StringValidator(regex=r'#[0-9a-f]{6}', min=2, max=6)
        
        message = validate_string('color', 'magenta')
        
        assert message.type == 'no_match'
        assert message.field == 'color'
        assert message.expected == {
            'regex': r'#[0-9a-f]{6}',
            'min': 2,
            'max': 6
        }
    
    def test_it_reports_a_string_not_in_options_and_not_in_length_range(self):
        validate_string = StringValidator(options=['red', 'green', 'blue'], min=2, max=6)
        
        message = validate_string('color', 'magenta')
        
        assert message.type == 'string_too_long'
        assert message.field == 'color'
        assert message.expected == {
            'options': ['red', 'green', 'blue'],
            'min': 2,
            'max': 6
        }
    
    def test_it_reports_a_string_not_matching_a_regex_and_not_in_options_and_not_in_length_range(self):
        validate_string = StringValidator(regex=r'#[0-9a-f]{6}', min=2, max=6, options=['red', 'green', 'blue'])
        
        message = validate_string('color', 'magenta')
        
        assert message.type == 'no_match'
        assert message.field == 'color'
        assert message.expected == {
            'regex': r'#[0-9a-f]{6}',
            'options': ['red', 'green', 'blue'],
            'min': 2,
            'max': 6
        }