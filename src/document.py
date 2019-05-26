class Document:
    def __init__(self, number, contents, store_name=None):
        self.number = number
        self.contents = contents
        self.store_name = store_name