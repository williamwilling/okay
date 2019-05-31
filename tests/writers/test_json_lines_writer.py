import json
from writers import JSONLinesWriter

class TestJSONLinesWriter:
    def test_it_writes_a_single_document(self):
        original_json = b'{"aspect": "cleanliness"}'
        original_dict = json.loads(original_json)
        writer = JSONLinesWriter()
        
        result = writer.add(original_dict)
        assert result == original_json
        result = writer.end()
        assert result == b''
    
    def test_it_write_multiple_documents(self):
        writer = JSONLinesWriter()
        
        original_json = b'{"aspect": "staff"}'
        original_dict = json.loads(original_json)
        result = writer.add(original_dict)
        assert result == original_json
        
        original_json = b'{"aspect": "location"}'
        original_dict = json.loads(original_json)
        result = writer.add(original_dict)
        assert result == original_json

        result = writer.end()
        assert result == b''