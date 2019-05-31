import json

class JSONLinesWriter:
    def add(self, document):
        return json.dumps(document).encode('utf-8')
    
    def end(self):
        return b''