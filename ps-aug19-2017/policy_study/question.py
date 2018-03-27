from exceptions import InstantiationError
from collections import OrderedDict
from utils import is_bare_cloze_id, qid_from

class Question(OrderedDict):
    def __init__(self, question):
        self.question = question
        self.tid = self._get_id()
        self.question["id"] = self.tid
        self.question["@id"] = self.tid
        self.pid = self._get_parent_id()
        self.ttype = self._get_type()
        self.question["type"] = self.ttype
        self.question["@type"] = self.ttype
        OrderedDict.__init__(self, question)

    def _get_id(self):
        obj = self.question
        if "id" in obj:
            return obj["id"]
        elif "@id" in obj:
            return obj["@id"]
        else:
            raise InstantiationError("Question", obj)

    def _get_type(self):
        obj = self.question
        if "type" in obj:
            return obj["type"]
        elif "response" in obj and "@type" in obj["response"]:
            return obj["response"]["@type"]
        else:
            return "" #no type
            #raise InstantiationError("Question", obj)

    def _get_parent_id(self):
        if is_bare_cloze_id(self.tid):
            return qid_from(self.tid)
