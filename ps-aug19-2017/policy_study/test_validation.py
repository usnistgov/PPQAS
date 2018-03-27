from policy_study.validation import (clean_display_when_questions, would_be_displayed,
                                     validate_minlength, validate_maxlength,
                                     validate_step, validate_min, validate_max,
                                     validate_gt, validate_lt, validate_lte, validate_gte,
                                     validate_eq)
from policy_study import views
from copy import deepcopy
from pprint import pprint
from datadiff import diff


def test_clean_display_when_questions():
    views.initialize()
    qaire = {
        u'policy_name': u'USDA',
        u'questions': {u'q.1.1': u'q.1.1.A',
                       u'q.1.1.1': u'q.1.1.1.A',
                       u'q.1.2.1': u'q.1.2.1.A',
                       u'q.1.2.2.1': u'q.1.2.2.1.C',
                       u'q.1.2.2.2': u'q.1.2.2.2.C',
                       u'q.1.2.3': u'q.1.2.3.A',
                       u'q.2.1': u'q.2.1.A',
                       u'q.2.1.A.b': u'3',
                       u'q.2.1>q.2.1.A.a': u'recommends',
                       u'q.2.2': u'q.2.2.A',
                       u'q.2.2.A.b': u'88',
                       u'q.2.20': u'q.2.20.B',
                       u'q.2.20.1': [u'q.2.20.1.A', u'q.2.20.1.G', u'q.2.20.1.H'],
                       u'q.2.2>q.2.2.A.a': u'requires',
                       u'q.2.3.1': [u'q.2.3.1.A'],
                       u'q.2.3.1.1': u'q.2.3.1.1.C',
                       u'q.2.3.1.2': u'q.2.3.1.2.A',
                       u'q.2.3.1.2.1.b': u'2',
                       u'q.2.3.1.2.1>q.2.3.1.2.1.a': u'requires',
                       u'q.2.3.1.3': u'q.2.3.1.3.B',
                       u'q.2.3.1.3.1.b': u'43',
                       u'q.2.3.1.3.1>q.2.3.1.3.1.a': u'recommends'},
        u'state': u'draft',
        u'username': u'bob'}
    output = deepcopy(qaire)
    clean_display_when_questions(output, views.idmap)
    pprint(output["questions"])
    pprint(qaire['questions'])
    print diff(qaire, output)
#    assert output == qaire



def test_would_be_displayed():
    ret = would_be_displayed({}, {})
    assert ret

def test_would_be_displayed2():
    ret = would_be_displayed({"@display_when": "1.2.A"}, {"1.2": "1.2.B"})
    assert not ret

def test_would_be_displayed3():
    ret = would_be_displayed({"@display_where": "q.3.13.A"}, {})
    assert not ret

def test_validate_minlength():
    ret = validate_minlength({"minlength": 5}, "q.1.2", {"q.1.2": "fkej"})
    assert not ret

def test_validate_minlength2():
    ret = validate_minlength({"minlength": 5}, "q.1.2", {"q.1.2": "fkejd"})
    assert ret

def test_validate_minlength3():
    ret = validate_minlength({"minlength": "5"}, "q.1.2", {"q.1.2": "fkejd"})
    assert ret

def test_validate_minlength4():
    ret = validate_minlength({"minlength": "5"}, "q.1.2", {"q.1.2": "fd"})
    assert not ret


def test_validate_maxlength():
    ret = validate_maxlength({"maxlength": 5}, "q.1.2", {"q.1.2": "fkej"})
    assert ret

def test_validate_maxlength2():
    ret = validate_maxlength({"maxlength": 5}, "q.1.2", {"q.1.2": "fkejdx"})
    assert not ret

def test_validate_maxlength3():
    ret = validate_maxlength({"maxlength": "5"}, "q.1.2", {"q.1.2": "fkejdd"})
    assert not ret

def test_validate_maxlength4():
    ret = validate_maxlength({"maxlength": "5"}, "q.1.2", {"q.1.2": "fd"})
    assert ret

def test_validate_step():
    ret = validate_step({"min": 2, "step": 5}, "q.1.2", {"q.1.2": 17})
    assert ret

def test_validate_step2():
    ret = validate_step({"min": 2, "step": 5}, "q.1.2", {"q.1.2": 18})
    assert not ret

def test_validate_min():
    ret = validate_min({"min": 2}, "q.1.2", {"q.1.2": 18})
    assert ret

def test_validate_max():
    ret = validate_max({"max": 2}, "q.1.2", {"q.1.2": 18})
    assert not ret

def test_validate_min2():
    ret = validate_min({"min": "2"}, "q.1.2", {"q.1.2": 18})
    assert ret

def test_validate_max2():
    ret = validate_max({"max": "2"}, "q.1.2", {"q.1.2": 18})
    assert not ret

def test_validate_gt():
    ret = validate_gt({"gt": "q.1.3"}, "q.1.2", {"q.1.2": 4, "q.1.3": "4"})
    assert not ret

def test_validate_lt():
    ret = validate_lt({"lt": "q.1.3"}, "q.1.2", {"q.1.2": 4, "q.1.3": "4"})
    assert not ret

def test_validate_lt2():
    ret = validate_lt({"lt": "q.1.3"}, "q.1.2", {"q.1.2": 5, "q.1.3": "4"})
    assert not ret

def test_validate_lt3():
    ret = validate_lt({"lt": "q.1.3"}, "q.1.2", {"q.1.2": "3", "q.1.3": 4})
    assert ret

def test_validate_gte():
    ret = validate_gte({"gte": "q.1.3"}, "q.1.2", {"q.1.2": "3", "q.1.3": [4, 5, 6]})
    assert ret

def test_validate_lte():
    ret = validate_lte({"lte": "q.1.3"}, "q.1.2", {"q.1.2": ["A", "B"], "q.1.3": "5"})
    assert ret

def test_validate_eq():
    ret = validate_eq({"eq": "q.1.3"}, "q.1.2", {"q.1.2": ["A", "B"], "q.1.3": [1, 2]})
    assert ret
