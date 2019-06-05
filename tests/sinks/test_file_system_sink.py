import pyfakefs.fake_filesystem_unittest
from document import Document
from sinks import FileSystemSink

class TestFileSystemSink:
    def test_it_writes_documents_to_a_file(self, fs):
        writer = WriterFake()
        path = 'result'

        with FileSystemSink(writer, path) as sink:
            sink.add(Document(1, { 'stars': 3 }))
            sink.add(Document(2, { 'stars': 5 }))
        
        with open('result', 'rb') as result:
            assert result.read() == b'stars:3/stars:5/END'
    
    def test_it_writes_documents_to_multiple_files(self, fs):
        writer = WriterFake()
        mapper = mapper_fake
        
        with FileSystemSink(writer, mapper) as sink:
            sink.add(Document(1, { 'aspect': 'staff'}, 'aspects'))
            sink.add(Document(2, { 'aspect': 'location'}, 'aspects'))
            sink.add(Document(2, { 'stars': 5 }, 'stars'))
        
        with open('aspects_output', 'rb') as result:
            assert result.read() == b'aspect:staff/aspect:location/END'
        
        with open('stars_output', 'rb') as result:
            assert result.read() == b'stars:5/END'


class WriterFake:
    def add(self, document):
        result = b''
        for key, value in document.items():
            result += f'{key}:{value}/'.encode()
        
        return result
    
    def end(self):
        return b'END'

def mapper_fake(input_store_name):
    return input_store_name + '_output'