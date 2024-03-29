import pytest
from decimal import Decimal
from okay.type_validators import NumberValidator

class TestNumberValidator:
    def test_it_accepts_an_integer(self):
        validate_number = NumberValidator()

        message = validate_number('score', 4)

        assert message is None
    
    def test_it_reports_a_non_number(self):
        validate_number = NumberValidator()

        message = validate_number('score', 'good')

        assert message.type == 'invalid_type'
        assert message.field == 'score'
        assert message.expected == {
            'type': 'number'
        }
    
    def test_it_accepts_a_floating_point_number(self):
        validate_number = NumberValidator()

        message = validate_number('score', 4.2)

        assert message is None
    
    def test_it_accepts_a_decimal(self):
        validate_number = NumberValidator()
        
        message = validate_number('score', Decimal(4.2))

        assert message is None
    
    def test_it_accepts_a_number_at_least_the_minimum(self):
        validate_number = NumberValidator(min=1)
        
        message = validate_number('score', 2)

        assert message is None
    
    def test_it_reports_a_number_smaller_than_the_minimum(self):
        validate_number = NumberValidator(min=1)
        
        message = validate_number('score', 0)
        
        assert message.type == 'number_too_small'
        assert message.field == 'score'
        assert message.expected == {
            'min': 1,
            'max': None,
            'options': None
        }
    
    def test_it_accepts_a_number_at_most_the_maximum(self):
        validate_number = NumberValidator(max=5)
        
        message = validate_number('score', 2)

        assert message is None
    
    def test_it_reports_a_number_larger_than_the_maximum(self):
        validate_number = NumberValidator(max=5)
        
        message = validate_number('score', 8)

        assert message.type == 'number_too_large'
        assert message.field == 'score'
        assert message.expected == {
            'max': 5,
            'min': None,
            'options': None
        }
    
    def test_it_reports_the_minimum_when_number_larger_than_the_maximum(self):
        validate_number = NumberValidator(min=0, max=5)

        message = validate_number('score', 7)

        assert message.type == 'number_too_large'
        assert message.field == 'score'
        assert message.expected == {
            'max': 5,
            'min': 0,
            'options': None
        }

    def test_it_reports_the_maximum_when_number_larger_than_the_minimum(self):
        validate_number = NumberValidator(min=1, max=5)

        message = validate_number('score', 0)

        assert message.type == 'number_too_small'
        assert message.field == 'score'
        assert message.expected == {
            'max': 5,
            'min': 1,
            'options': None
        }
    
    def test_it_reports_when_number_smaller_than_minimum_of_zero(self):
        validate_number = NumberValidator(min=0)

        message = validate_number('score', -1)

        assert message.type == 'number_too_small'
        assert message.field == 'score'
        assert message.expected == {
            'min': 0,
            'max': None,
            'options': None
        }
    
    def test_it_reports_when_number_larger_than_maximum_of_zero(self):
        validate_number = NumberValidator(max=0)

        message = validate_number('score', 1)

        assert message.type == 'number_too_large'
        assert message.field == 'score'
        assert message.expected == {
            'max': 0,
            'min': None,
            'options': None
        }
    
    def test_it_accepts_a_number_in_a_list_of_options(self):
        validate_number = NumberValidator(options=[1, 2, 3])

        message = validate_number('score', 2)

        assert message is None

    def test_it_reports_a_number_not_in_a_list_of_options(self):
        validate_number = NumberValidator(options=[1, 2, 3])

        message = validate_number('score', 1.23)

        assert message.type == 'invalid_number_option'
        assert message.field == 'score'
        assert message.expected == {
            'options': [1, 2, 3],
            'min': None,
            'max': None
        }

    def test_it_accepts_a_number_out_of_range_but_in_a_list_of_options(self):
        validate_number = NumberValidator(options=[2, 4, 6], min=10)

        message = validate_number('score', 4)

        assert message is None
    
    def test_it_accepts_a_number_not_in_a_list_of_options_but_within_range(self):
        validate_number = NumberValidator(options=list(range(1, 10)), max=100)

        message = validate_number('score', 22)

        assert message is None
    
    def test_it_reports_when_number_is_not_in_a_list_of_options_and_out_of_range(self):
        validate_number = NumberValidator(options=[1, 2, 3], min=4, max=5)

        message = validate_number('score', 6)

        assert message.type == 'number_too_large'