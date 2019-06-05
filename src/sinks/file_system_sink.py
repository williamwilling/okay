class FileSystemSink:
    def __init__(self, writer, mapper):
        self._writer = writer
        if isinstance(mapper, str):
            self._mapper = lambda _: mapper
        else:
            self._mapper = mapper

        self._file = None
        self._current_store = None

    def __enter__(self):
        return self
    
    def add(self, document):
        self._set_output_stream(document.store_name)
        
        buffer = self._writer.add(document.contents)
        self._file.write(buffer)
    
    def __exit__(self, exception_type, exception_value, exception_trace):
        self._close_file()

    def _set_output_stream(self, input_store):
        output_store = self._mapper(input_store)
        if output_store != self._current_store:
            self._current_store = output_store
            if self._file is not None:
                self._close_file()
            
            self._file = open(output_store, 'wb')
    
    def _close_file(self):
        buffer = self._writer.end()
        self._file.write(buffer)
        self._file.close()