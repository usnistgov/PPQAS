import xmltodict
from test_consts import xml_string, xml_string_for_ids
from policy_study.elements import (listify_elements,
                                   populate_idmap, build_pages_,
                                   get_index_tree, get_questionnaire,
                                   parse_clozes, add_required_rec, convert_tf_select_multi,
                                   annotate_questions, include_to_question,
                                   get_all_elements, pagify_group, pages_from_group,
                                   pages_from_page_list, parse_cloze_string, convert_nones_to)
import json
from collections import OrderedDict
from datadiff import diff
from pprint import pprint


def test_parse_cloze_string():
    inputstr = """The  policy {"cloze":{ "id":"6.1.3.1a", "type":"select one", "options":["requires" , "recommends"]}} that no more than {"cloze":{ "id":"6.1.3.1b", "type":"numerical", "validation":"1-9", "default":"____"}} characters in the password are upper case letters."""

    output = parse_cloze_string(inputstr)
    expected = ['The  policy ',
                {u'cloze': {u'id': u'6.1.3.1a',
                            u'options': [u'requires', u'recommends'],
                            u'type': u'select one'}},
                ' that no more than ',
                {u'cloze': {u'default': u'____',
                            u'id': u'6.1.3.1b',
                            u'type': u'numerical',
                            u'validation': u'1-9'}},
                ' characters in the password are upper case letters.']

    assert output == expected


def test_listify_elements():
    def is_lists(adict):
        """Tests whether listify is listifying"""
        for k,v in adict.items():
            if k.startswith("#") or k.startswith("@"):
                assert not isinstance(v, list) and not isinstance(v, dict)
            else:
                assert isinstance(v, list)
                for item in v:
                    if isinstance(item, dict):
                        is_lists(item)

    obj = xmltodict.parse(xml_string)
    pprint(obj)
    ret = listify_elements(obj)
    is_lists(ret)

def test_convert_nones_to():
    test_dict = {"hello": [{"hi": None}, None, "something", 4],
                 "goodbye": None,
                 "hey": {"wazza":None,
                         "aloha": {"exuberant": False}}}
    convert_nones_to(test_dict, "")
    expected = {"hello": [{"hi": ""}, "", "something", 4],
                 "goodbye": "",
                 "hey": {"wazza":"",
                         "aloha": {"exuberant": False}}}
    assert not diff(test_dict, expected)

# def test_build_pages():
#     obj = xmltodict.parse(xml_string)
#     obj = listify_elements(obj)
#     ret = build_pages(obj["questionnaire"][0]["index"][0])
#     assert ret == [OrderedDict([(u'@title', u'Who'),
#                                (u'@comment_ref', u'c_2'),
#                                (u'@next', u'Next Page - Any Method'),
#                                (u'@back', u'Home'),
#                                (u'include', [OrderedDict([(u'@qref', u'1')]),
#                                              OrderedDict([(u'@qref', u'1.1')])]),
#                                ('instructions', [])]),
#                   OrderedDict([(u'@title', u'Any Method'),
#                                (u'@comment_ref', u'c_4'),
#                                (u'instructions',
#                                 [u'Text for instructions<br> for this page would go here and shown only when pages are shown']),
#                                (u'include', [OrderedDict([(u'@qref', u'2')]),
#                                              OrderedDict([(u'@qref', u'2.1')])])])]

def test_populate_idmap():
    obj = xmltodict.parse(xml_string_for_ids)
    idmap = {}
    populate_idmap(obj, idmap)
    expected = {u'1': OrderedDict(
        [(u'@id', u'1'),
         (u'text',
          u'Does the policy identify people with whom users <b>may not</b> communicate or share passwords?'),
         (u'response',
          OrderedDict([(u'@type',
                        u'select one'),
                       (u'option',
                        [OrderedDict([(u'@id', u'1.A'),
                                      (u'text', u'Yes')]),
                         OrderedDict([(u'@id', u'1.B'), (u'text', u'No')])])]))]),
                u'1.A': OrderedDict([(u'@id', u'1.A'), (u'text', u'Yes')]),
                u'1.B': OrderedDict([(u'@id', u'1.B'), (u'text', u'No')])}
    assert not diff(idmap, expected)

def test_get_index_tree():
    from policy_study import app
    app.config["INPUT_FILE"] = "resources/pp_test_blank.xml"
    from policy_study import views
    views.initialize()
    ti = get_index_tree(views.qindex)
    assert ti.keys() == [u'Group 1', u'group 2', u'group 3']
    print ti
    assert 1 == 1


def test_include_to_question():
    clone_map = {}
    questionnaire = get_questionnaire("resources/pp_test_blank.xml")
    questionnaire = parse_clozes(questionnaire)
    questions = questionnaire["questions"]
    convert_tf_select_multi(questions)
    annotate_questions(questions, clone_map)
    idmap = {}
    populate_idmap(questionnaire, idmap)
    elements = questionnaire["static_text"]
    qindex = listify_elements(questionnaire["index"])
    qindex = include_to_question(qindex, idmap)
    pprint(qindex)
    assert 1 == 1

def test_add_required_rec():
    questionnaire = get_questionnaire("resources/test_add_required.xml")
    questionnaire = parse_clozes(questionnaire)
    add_required_rec(questionnaire)
    print(json.dumps(questionnaire, indent=4))
    assert 1 == 1

def test_get_all_elements():
    questionnaire = get_questionnaire("resources/pp_test_blank.xml")
    qindex = listify_elements(questionnaire["index"])
    pgs = get_all_elements("page", qindex["group"][0])
    pprint(pgs)
    assert 1 == 1


def test_pagify_group():
    questionnaire = get_questionnaire("resources/pp_test_blank.xml")
    qindex = listify_elements(questionnaire["index"])
    idmap = {}
    populate_idmap(questionnaire, idmap)
    qindex = include_to_question(qindex, idmap)
    pg = pagify_group(qindex["group"][0], [('instructions', "I like cheese")], 2, False)
    pprint(pg)
    assert 1 == 1

def test_build_pages_():
    questionnaire = get_questionnaire("resources/pp_test_blank.xml")
    qindex = listify_elements(questionnaire["index"])
    idmap = {}
    populate_idmap(questionnaire, idmap)
    qindex = include_to_question(qindex, idmap)
    pages = build_pages_(qindex)
    pprint(pages)
    assert 1 == 1

def test_pages_from_group():
    questionnaire = get_questionnaire("resources/pp_test_blank.xml")
    qindex = listify_elements(questionnaire["index"])
    idmap = {}
    populate_idmap(questionnaire, idmap)
    qindex = include_to_question(qindex, idmap)
    pgs = pages_from_group(qindex["group"][0], level="2")
    pprint(pgs)
    assert 1 == 1

def test_pages_from_page_list():
    questionnaire = get_questionnaire("resources/pp_test.xml")
    qindex = listify_elements(questionnaire["index"])
    idmap = {}
    populate_idmap(questionnaire, idmap)
    qindex = include_to_question(qindex, idmap)
    print qindex
    pgs = pages_from_page_list(qindex["group"][0]["group"][1]["group"][1]["page"], [])
    pprint(pgs)
    assert 1 == 1
