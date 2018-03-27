from question import Question
from exceptions import InstantiationError
import pytest


def test_question():
    q = Question({"hello": 1, "goodbye": 2, "id": "q.3.2.a", "response": {"@type": "select one"}})
    assert q["hello"] == 1
    assert q.get("goodbye") == 2
    assert q.get("narf", 4) == 4
    assert q.setdefault("something", 5) == 5
    assert q.ttype == "select one"
    assert q.pid == "q.3.2"

def test_question2():
    with pytest.raises(InstantiationError):
        Question({"hello": 1, "goodbye": 2})
