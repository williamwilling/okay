import io
import pytest
import sys
from store import Store
from readers import JSONLinesReader

class TestJSONLinesReader:
    def test_it_produces_no_documents_from_empty_input(self):
        source = SourceStub(b'')
        reader = JSONLinesReader(source)

        documents = list(reader.documents())

        assert documents == []
    
    def test_it_reads_an_empty_document(self):
        source = SourceStub(b'')
        reader = JSONLinesReader(source)

        documents = reader.documents()

        with pytest.raises(StopIteration):
            next(documents)
    
    def test_it_parses_a_json_document(self):
        source = SourceStub(b'{ "key": "value" }')
        reader = JSONLinesReader(source)

        documents = reader.documents()
        document = next(documents)

        assert document.number == 1
        assert document.contents == { 'key': 'value' }
    
    def test_it_produces_multiple_documents(self):
        source = SourceStub(b'''
            { "aspect": "cleanliness" }
            { "aspect": "staff" }
            { "aspect": "location" }
        ''')
        reader = JSONLinesReader(source)

        documents = reader.documents()
        
        document = next(documents)
        assert document.number == 1
        assert document.contents['aspect'] == 'cleanliness'
        document = next(documents)
        assert document.number == 2
        assert document.contents['aspect'] == 'staff'
        document = next(documents)
        assert document.number == 3
        assert document.contents['aspect'] == 'location'
    
    def test_it_stitches_a_document_back_together(self):
        source = SourceStub(b'{ "aspect": "cleanliness" }', buffer_size=10)
        reader = JSONLinesReader(source)

        documents = reader.documents()
        document = next(documents)

        assert document.number == 1
        assert document.contents['aspect'] == 'cleanliness'
    
    def test_it_stitches_multiple_documents_back_together(self):
        source = SourceStub(b'''
            { "aspect": "cleanliness" }
            { "aspect": "location" }
        ''', buffer_size=10)
        reader = JSONLinesReader(source)

        documents = reader.documents()
        
        document = next(documents)
        assert document.number == 1
        assert document.contents['aspect'] == 'cleanliness'
        document = next(documents)
        assert document.number == 2
        assert document.contents['aspect'] == 'location'
    
    def test_it_reports_an_unparsable_line(self):
        source = SourceStub(b'not json')
        reader = JSONLinesReader(source)

        documents = reader.documents()

        with pytest.raises(StopIteration):
            document = next(documents)
        assert len(reader.messages) == 1
        message = reader.messages[0]
        assert message.type == 'malformed_json'
        assert message.document_number == 1
    
    def test_it_continues_after_an_unparsable_line(self):
        source = SourceStub(b'''
            { "aspect": "cleanliness" }
            { 'not': 'json' }
            { "aspect": "location" }
        ''')
        reader = JSONLinesReader(source)

        documents = reader.documents()
        next(documents)
        document = next(documents)

        assert document.contents['aspect'] == 'location'
        assert len(reader.messages) == 1
        message = reader.messages[0]
        assert message.type == 'malformed_json'
        assert message.document_number == 2
    
    def test_it_reads_from_multiple_streams(self):
        source = SourceStub(
            b'{ "aspect": "cleanliness" }',
            b'{ "aspect": "staff" }'
        )
        reader = JSONLinesReader(source)

        documents = reader.documents()

        document = next(documents)
        assert document.number == 1
        assert document.contents['aspect'] == 'cleanliness'
        document = next(documents)
        assert document.number == 2
        assert document.contents['aspect'] == 'staff'
    
    def test_it_includes_store_names_in_the_result(self):
        source = SourceStub(
            (
                'data.json',
                b'''
                    { "aspect": "cleanliness" }
                ''' 
            ),
            (
                'oh-no-more-data.json',
                b'{ "aspect": "staff" }'
            )
        )
        reader = JSONLinesReader(source)

        documents = reader.documents()

        document = next(documents)
        assert document.store_name == 'data.json'
        document = next(documents)
        assert document.store_name == 'oh-no-more-data.json'


class SourceStub:
    def __init__(self, *args, buffer_size=None):
        if isinstance(args[0], tuple):
            self._stores = list(args)
        else:
            self._stores = [ (None, source) for source in list(args) ]

        self._buffer_size = buffer_size
    
    def stores(self):
        if self._buffer_size:
            return ( Store(store[0], ChunkedBytesIO(store[1], self._buffer_size)) for store in self._stores )
        else:
            return ( Store(store[0], io.BytesIO(store[1])) for store in self._stores )


class ChunkedBytesIO:
    def __init__(self, data, buffer_size=sys.maxsize):
        self._data = data
        self._buffer_size = buffer_size
        self._offset = 0
    
    def read(self):
        data = self._data[self._offset:self._offset + self._buffer_size]
        self._offset += self._buffer_size
        return data