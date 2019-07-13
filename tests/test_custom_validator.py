import pytest
from okay import SchemaError
from okay.type_validators import validate_custom
from okay.message import Message

class TestCustomValidator:
    def test_it_runs_a_custom_validation_function(self):
        has_run = False
        def validator(field, value):
            nonlocal has_run
            has_run = True
        
        message = validate_custom(None, None, validator=validator)

        assert has_run
        assert message is None
    
    def test_it_relays_validation_messages(self):
        def validator(field, value):
            return Message(
                type='dummy',
                field='dummy'
            )
        
        message = validate_custom(None, None, validator=validator)

        assert message.type == 'dummy'
        assert message.field == 'dummy'
    
    def test_it_raises_when_validation_function_returns_invalid_value(self):
        def validator(field, value):
            return 'not good'
        
        with pytest.raises(SchemaError):
            validate_custom(None, None, validator=validator)
    
    def test_it_raises_when_validation_function_is_not_callable(self):
        with pytest.raises(SchemaError):
            validate_custom(None, None, 'validator')
    
    def test_it_raises_when_validation_function_contains_a_bug(self):
        def validator(field, value):
            bug = [ 1, 2, 3 ][4]
        
        with pytest.raises(SchemaError) as exception_info:
            validate_custom(None, None, validator)
        
        assert type(exception_info.value.__cause__) == IndexError