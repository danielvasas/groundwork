import os
from groundwork.patterns import GwDocumentsPattern


class DocumentPlugin(GwDocumentsPattern):
    def __init__(self, *args, **kwargs):
        self.name = self.__class__.__name__
        super().__init__(*args, **kwargs)

    def activate(self):
        self.documents.register("test_document", "test_content")
