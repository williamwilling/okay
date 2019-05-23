import io
import pytest
import sys
from readers import JSONLinesReader

class TestJSONLinesReader:
    def test_it_produces_no_documents_from_empty_input(self):
        source = io.BytesIO(b'')
        reader = JSONLinesReader(source)

        documents = list(reader.documents())

        assert documents == []
    
    def test_it_reads_an_empty_document(self):
        source = io.BytesIO(b'')
        reader = JSONLinesReader(source)

        documents = reader.documents()

        with pytest.raises(StopIteration):
            next(documents)
    
    def test_it_parses_a_json_document(self):
        source = io.BytesIO(b'{ "key": "value" }')
        reader = JSONLinesReader(source)

        documents = reader.documents()
        document = next(documents)

        assert document == { 'key': 'value' }
    
    def test_it_produces_multiple_documents(self):
        source = io.BytesIO(b'''
            { "aspect": "cleanliness" }
            { "aspect": "staff" }
            { "aspect": "location" }
        ''')
        reader = JSONLinesReader(source)

        documents = reader.documents()
        
        document = next(documents)
        assert document['aspect'] == 'cleanliness'
        document = next(documents)
        assert document['aspect'] == 'staff'
        document = next(documents)
        assert document['aspect'] == 'location'
    
    def test_it_stitches_a_document_back_together(self):
        source = ChunkedBytesIO(b'{ "aspect": "cleanliness" }', buffer_size=10)
        reader = JSONLinesReader(source)

        documents = reader.documents()
        document = next(documents)

        assert document['aspect'] == 'cleanliness'
    
    def test_it_stitches_multiple_documents_back_together(self):
        source = ChunkedBytesIO(b'''
            { "aspect": "cleanliness" }
            { "aspect": "location" }
        ''', buffer_size=10)
        reader = JSONLinesReader(source)

        documents = reader.documents()
        
        document = next(documents)
        assert document['aspect'] == 'cleanliness'
        document = next(documents)
        assert document['aspect'] == 'location'
    
    def test_it_reports_an_unparsable_line(self):
        source = io.BytesIO(b'not json')
        reader = JSONLinesReader(source)

        documents = reader.documents()

        with pytest.raises(StopIteration):
            document = next(documents)
        assert len(reader.messages) == 1
        message = reader.messages[0]
        assert message.type == 'malformed_json'
        assert message.document_number == 1
    
    def test_it_continues_after_an_unparsable_line(self):
        source = io.BytesIO(b'''
            { "aspect": "cleanliness" }
            { 'not': 'json' }
            { "aspect": "location" }
        ''')
        reader = JSONLinesReader(source)

        documents = reader.documents()
        next(documents)
        document = next(documents)

        assert document['aspect'] == 'location'
        assert len(reader.messages) == 1
        message = reader.messages[0]
        assert message.type == 'malformed_json'
        assert message.document_number == 2
        


class ChunkedBytesIO:
    def __init__(self, data, buffer_size=sys.maxsize):
        self._data = data
        self._buffer_size = buffer_size
        self._offset = 0
    
    def read(self):
        data = self._data[self._offset:self._offset + self._buffer_size]
        self._offset += self._buffer_size
        return data