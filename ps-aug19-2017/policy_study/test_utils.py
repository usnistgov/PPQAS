from utils import (parents_for_title, get_qid,
                   opt_id_from, qid_from, base_qid_from, json_map,
                   qualify_cloze_id, is_bare_cloze_id, get_clone_str,
                   is_float, get_with_clone, get_type, is_cloze_id)

from test_consts import xml_string
from datadiff import diff

import xmltodict

from constants_test import index

def test_get_qid():
    assert get_qid("q.3.2.A.a") == "q.3.2"

def test_get_qid2():
    assert get_qid("q.3.2.A") == "q.3.2"

def test_get_qid3():
    assert get_qid("q.3.2") == "q.3.2"


def test_get_qid4():
    assert get_qid("c.3.2") == "c.3.2"

def test_json_map():
    obj = xmltodict.parse(xml_string)
    ret = json_map(lambda a: a, obj)
    assert not diff(obj, ret)

def test_is_cloze_id():
    assert is_cloze_id("q.1.2.a")

def test_is_cloze_id2():
    assert not is_cloze_id("q.1.2.A")


def test_parents_for_title():
    output = parents_for_title(index, "Alphanumeric Characters")
    expected = ["Alphanumeric Characters",
                "Character Occurrence",
                "Characters",
                "Password Composition",
                "Creating Passwords"]
    assert set(output) == set(expected)

def test_add_string_to_ids():
    pass
#    views.initialize()
#    add_string_to_ids("XXXXXX", views.questions)
#    pprint(views.questions)
#    assert 1 == 2

def test_opt_id_from():
    ret = opt_id_from("q.1.2.3clone1>q.1.2.3.A.bclone1")
    assert ret == "q.1.2.3.Aclone1"

def test_opt_id_from2():
    ret = opt_id_from("q.2.7.1.1>q.2.7.1.1.a")
    assert ret == None

def test_opt_id_from3():
    ret = opt_id_from("c.2.7.1.1>c.2.7.1.1.a")
    assert ret == None

def test_qid_from():
    ret = qid_from("q.1.2.3clone1>q.1.2.3.A.bclone1")
    assert ret == "q.1.2.3clone1"

def test_qid_from2():
    ret = qid_from("q.1.2.3.Aclone1")
    assert ret == "q.1.2.3clone1"

def test_qid_from3():
    ret = qid_from("q.1.2.3.a")
    assert ret == "q.1.2.3"

def test_qid_from4():
    ret = qid_from("q.1.2.3.A.a")
    assert ret == "q.1.2.3"

def test_qid_from5():
    ret = qid_from("q.1.2.3.A.aclone1")
    assert ret == "q.1.2.3clone1"

def test_qid_from6():
    ret = qid_from("b.1.2.3.A.aclone1")
    assert ret == "b.1.2.3clone1"

def test_qid_from7():
    ret = qid_from("b.1.2.3.A")
    assert ret == "b.1.2.3"

def test_qid_from8():
    ret = qid_from("c.1.2.3.A")
    assert ret == "c.1.2.3"



def test_base_qid_from():
    ret = base_qid_from("q.1.2.3clone1>q.1.2.3.A.bclone1")
    assert ret == "q.1.2.3"

def test_qualify_cloze_id():
    ret = qualify_cloze_id("q.2.3.a")
    assert ret == "q.2.3>q.2.3.a"

def test_qualify_cloze_id2():
    ret = qualify_cloze_id("q.2.3.A.a")
    assert ret == "q.2.3>q.2.3.A.a"


def test_qualify_cloze_id3():
    ret = qualify_cloze_id("q.2.3.A.aclone1")
    assert ret == "q.2.3clone1>q.2.3.A.aclone1"

def test_qualify_cloze_id4():
    ret = qualify_cloze_id("c.2.3.A.aclone1")
    assert ret == "c.2.3clone1>c.2.3.A.aclone1"


def test_is_bare_cloze_id():
    assert is_bare_cloze_id("q.1.3.a")

def test_is_bare_cloze_id2():
    assert is_bare_cloze_id("q.1.3.A.a")

def test_is_bare_cloze_id3():
    assert not is_bare_cloze_id("q.1.3>q.1.3.a")

def test_is_bare_cloze_id4():
    assert not is_bare_cloze_id("q.1.3.A>q.1.3.A.a")

def test_is_bare_cloze_id5():
    assert is_bare_cloze_id("q.1.3.aclone1")

def test_is_bare_cloze_id6():
    assert is_bare_cloze_id("c.1.3.aclone1")

def test_get_clone_str():
    assert get_clone_str("q.2.3.aclone4") == "clone4"

def test_get_clone_str2():
    assert get_clone_str("q.2.3clone44>q.2.3.aclone44") == "clone44"

def test_is_float():
    assert is_float("3") == True

def test_is_float2():
    assert is_float("x") == False

def test_is_float3():
    assert is_float([1, 2, 3]) == False

def test_is_float4():
    assert is_float(6) == True


def test_get_with_clone():
    adict = {"q.1.1": {"@id": "q.1.1", "response": {"option": {"@id": "q.1.1.A"}}}}
    expected = {"@id": "q.1.1clone1", "response": {"option": {"@id": "q.1.1.Aclone1"}}}
    assert get_with_clone(adict, "q.1.1clone1") == expected


def test_get_with_clone2():
    adict = {"q.1.1": {"@id": "q.1.1", "response": {"option": {"@id": "q.1.1.A"}}}}
    expected = {"@id": "q.1.1", "response": {"option": {"@id": "q.1.1.A"}}}
    assert get_with_clone(adict, "q.1.1") == expected


def test_get_type():
    t1 = {"@id": "q.1.3", "response": [{"@type": "select multi"}]}
    t2 = {"@id": "q.1.3", "response": {"@type": "select multi"}}
    t3 = {"id": "q.1.3", "type":"select one"}
    t4 = {"@type": "select one"}
    assert get_type(t1) == "select multi"
    assert get_type(t2) == "select multi"
    assert get_type(t3) == "select one"
    assert get_type(t4) == "select one"
