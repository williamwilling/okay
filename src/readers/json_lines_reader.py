import json
from document import Document
from message import Message

class JSONLinesReader:
    def __init__(self, source):
        self._source = source
        self.messages = []
    
    def documents(self):
        document_number = 1

        for store in self._source.stores():
            buffer = ''

            while True:
                end_of_line = buffer.find('\n')
                while end_of_line == -1:
                    chunk = store.stream.read()
                    buffer += chunk.decode('utf8')
                    if chunk == b'':
                        break
                    end_of_line = buffer.find('\n')
                
                if end_of_line == -1:
                    line = buffer
                else:
                    line = buffer[:end_of_line + 1]
                    buffer = buffer[end_of_line + 1:]

                if line.strip():
                    try:
                        yield Document(document_number, json.loads(line), store.name)
                    except json.JSONDecodeError as error:
                        self.messages.append(Message(
                            type='malformed_json',
                            document_number=document_number,
                            extra=str(error)
                        ))
                    document_number += 1
            
                if chunk == b'':
                    break