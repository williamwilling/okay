import gzip
import pytest
import pyfakefs.fake_filesystem_unittest
from sources import FileSystemSource

class TestFileSystemSource:
    def test_it_opens_a_single_file(self, fs):
        fs.create_file('test.txt', contents=b'Hello, world!')
        source = FileSystemSource('test.txt')
        stores = source.stores()
        
        store = next(stores)
        assert store.name == 'test.txt'
        contents = store.stream.read()
        assert contents == b'Hello, world!'

        with pytest.raises(StopIteration):
            next(stores)
    
    def test_it_opens_all_files_in_a_directory(self, fs):
        fs.create_file('test/hello.txt', contents=b'Hello, world!')
        fs.create_file('test/farewell.txt', contents=b'Farewell, cruel world!')
        source = FileSystemSource('test')
        stores = source.stores()
        
        store = next(stores)
        assert store.name == 'test/hello.txt'
        contents = store.stream.read()
        assert contents == b'Hello, world!'
        store = next(stores)
        assert store.name == 'test/farewell.txt'
        contents = store.stream.read()
        assert contents == b'Farewell, cruel world!'
    
    def test_it_opens_a_zipped_file(self, fs):
        fs.create_file('test.txt', contents=gzip.compress(b"It's a small world after all."))
        source = FileSystemSource('test.txt')
        stores = source.stores()

        store = next(stores)
        assert store.name == 'test.txt'
        contents = store.stream.read()
        assert contents == b"It's a small world after all."
