from type_validators import validate_custom
from message import Message

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