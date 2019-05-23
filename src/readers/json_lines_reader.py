import json
from message import Message

class JSONLinesReader:
    def __init__(self, source):
        self._source = source
        self.messages = []
    
    def documents(self):
        buffer = ''
        document_number = 1

        while True:
            end_of_line = buffer.find('\n')
            while end_of_line == -1:
                chunk = self._source.read()
                buffer += chunk
                if chunk == '':
                    break
                end_of_line = buffer.find('\n')
            
            if end_of_line == -1:
                line = buffer
            else:
                line = buffer[:end_of_line + 1]
                buffer = buffer[end_of_line + 1:]

            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as error:
                    self.messages.append(Message(
                        type='malformed_json',
                        document_number=document_number,
                        extra=str(error)
                    ))
                document_number += 1
        
            if chunk == '':
                break