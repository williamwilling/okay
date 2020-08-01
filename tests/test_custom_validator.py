import pytest
from okay import SchemaError
from okay.type_validators import CustomValidator
from okay.message import Message

class TestCustomValidator:
    def test_it_runs_a_custom_validation_function(self):
        has_run = False
        def validator(field, value):
            nonlocal has_run
            has_run = True
        validate_custom = CustomValidator('field', validator=validator)
        
        message = validate_custom(None, None)

        assert has_run
        assert message is None
    
    def test_it_relays_validation_messages(self):
        def validator(field, value):
            return Message(
                type='dummy',
                field='dummy'
            )
        validate_custom = CustomValidator('field', validator=validator)
        
        message = validate_custom(None, None)

        assert message.type == 'dummy'
        assert message.field == 'dummy'
    
    def test_it_raises_when_validation_function_returns_invalid_value(self):
        def validator(field, value):
            return 'not good'
        validate_custom = CustomValidator('field', validator=validator)
        
        with pytest.raises(SchemaError):
            validate_custom(None, None)
    
    def test_it_raises_when_validation_function_is_not_callable(self):
        with pytest.raises(SchemaError):
            validate_custom = CustomValidator('field', validator='validator')

    def test_it_raises_when_validation_function_contains_a_bug(self):
        def validator(field, value):
            bug = [ 1, 2, 3 ][4]
        validate_custom = CustomValidator('field', validator=validator)
        
        with pytest.raises(SchemaError) as exception_info:
            validate_custom(None, None)
        
        assert type(exception_info.value.__cause__) == IndexError
    
    def test_it_raises_when_validation_function_is_missing(self):
        with pytest.raises(SchemaError):
            CustomValidator('field')