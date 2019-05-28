import os
from gzip import GzipFile
from store import Store

class FileSystemSource:
    def __init__(self, path):
        self._path = path
    
    def stores(self):
        try:
            paths = [ os.path.join(self._path, file_name) for file_name in os.listdir(self._path) ]
        except NotADirectoryError:
            paths = [ self._path ]

        for path in paths:
            with open(path, 'rb') as file:
                if _is_zipped(file):
                    file = GzipFile(fileobj=file)
                yield Store(path, file)


def _is_zipped(file):
    gzip_identifier = file.read(2)
    file.seek(0)
    return gzip_identifier == b'\x1f\x8b'