import xmltodict
from collections import OrderedDict
from policy_study.tree import build_tree

from policy_study.utils import listify, delistify, get_type, set_id_bnf_mapping
from pprint import pformat
import re
import logging as log
import sys
import json


class DuplicateIDError(Exception):
    def __init__(self, idname, value, oldval):
        self.idname = idname
        self.value = value
        self.oldval = oldval
    def __str__(self):
        return "Duplicate IDs found in input file for id " + self.idname + \
            "values are:\n" + str(self.value) + "\nand:\n" + str(self.oldval)


def parse_cloze_string(inputstr):
    """
    Takes a string which may contain embedded json for representing a cloze statement.
    Returns a list containing strings and dicts in order that they appear in the input string.
    """
    if isinstance(inputstr, list):
        return inputstr
    if not isinstance(inputstr, str) and not isinstance(inputstr, unicode):
        log.error("shouldn't be here! in parse_cloze_string, type=" + str(type(inputstr)) + " inputstr=" + str(inputstr))
        return inputstr
    ret_list = []
    reg_string = ""
    cloze_string = ""
    in_cloze = False
    json_stack = 0
    for ch in inputstr:
        if not in_cloze:
            if ch != "{":
                reg_string += ch
            else:
                in_cloze = True
                cloze_string += ch
                json_stack += 1
                if reg_string:
                    ret_list.append(reg_string)
                    reg_string = ""
        elif in_cloze:
            cloze_string += ch
            if ch == "{":
                json_stack += 1
            elif ch == "}":
                json_stack -= 1
                if not json_stack:
                    in_cloze = False
                    try:
                        ret_list.append(json.loads(cloze_string))
                    except Exception as e:
                        print("Exception in parse_cloze_string, check json in '" + inputstr + "'")
                        print(str(e))
                        print("")
                        ret_list.append(cloze_string)
                    cloze_string = ""
    if reg_string:
        ret_list.append(reg_string)
    if cloze_string:
        ret_list.append(cloze_string)
    return ret_list


# deprecated
def convert_tf_select_multi(questions):
    """True/Falses are annoying to deal with - I'll convert them to select
    multis with only one options, and during
    'build_forward_display_refs', I'll convert any display_whens that
    refer to them to refer to the option
    """
    for question in questions["question"]:
        resp = question.get("response", None)
        if isinstance(resp, list):
            raise Exception("should only be a single response object per question")
        if resp and resp["@type"] == "true/false":
            resp["@type"] = "select multi"
            resp["option"] = [OrderedDict({"@id": question["@id"] + ".A",
                                          "text": resp.get("text", None)})]
            del resp["text"]

def remake_clones(clone_map, idmap):

    clone_map = dict()

    for k, v in idmap.iteritems():
        if k.startswith("q") and  "@hasclones" in v :
            if v["@hasclones"]:
                print v
                for opt in listify(v["response"].get("option", [])):
                    if "@clone" in opt:
                        for clone_qid in opt["@clone"].split(","):
                            clone_map[clone_qid] = opt["@id"]

    return clone_map


def annotate_questions(questions, clone_map):
    """If a question can be cloned, add a hasclones attribute to it"""
    for question in questions["question"]:
        resp = question.get("response", None)
        if isinstance(resp, list):
            raise Exception("should only be a single response object per question")
        if resp:
            for opt in listify(resp.get("option", [])):
                if "@clone" in opt:
                    question["@hasclones"] = True
                    for clone_qid in opt["@clone"].split(","):
                        clone_map[clone_qid] = opt["@id"]


def convert_nones_to(top, string):
    """Tags which are present but empty will have the value None - this
    will convert all Nones to empty strings"""
    for k,v in top.items():
        if v == None:
            top[k] = string
        if isinstance(v, dict):
            convert_nones_to(v, string)
        elif isinstance(v, list):
            for i,item in enumerate(v):
                if isinstance(item, dict):
                    convert_nones_to(item, string)
                elif item == None:
                    v[i] = string



def populate_idmap(top, idmap):
    """create a dict where the keys are all ids in xml document"""
    for k,v in top.items():
        if k == "@id" or k == "id":
            if not v in idmap:
                idmap[v] = top
            else:
                raise DuplicateIDError(v, top, idmap[v])
        if isinstance(v, dict):
            populate_idmap(v, idmap)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    populate_idmap(item, idmap)

def populate_map(top, themap, idname):
    """create a dict where the keys are all idname in xml doc"""
    for k,v in top.items():
        if k == idname:
            if not v in themap:
                themap[v] = top
            else:
                raise DuplicateIDError(v, top, themap[v])
        if isinstance(v, dict):
            populate_map(v, themap, idname)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    populate_map(item, themap, idname)


def parse_clozes(obj):
    """function to go through and call parse_cloze_string on stuff"""
    for k,v in obj.items():
        if k=="@type" and (v=="json"):
            if "#text" in obj:
                obj["#text"] = parse_cloze_string(obj["#text"])
        if isinstance(v, dict):
            parse_clozes(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    parse_clozes(item)
    return obj

def add_required_rec(obj):
    """Make all questions required by default, except select multi questions, and comments questions"""
    for k,v in obj.items():
        if k == "additional_comments":
            continue
        elif k == "response" or k == "cloze":
            for item in listify(v):
                add_required(item)
                add_required_rec(item)
        else:
            for item in listify(v):
                if isinstance(item, dict):
                    add_required_rec(item)



def add_required(item):
    """Takes in a response or cloze object and adds the default required-ness to validation"""
    # TODO - consider adding default invalid_text as well
    if get_type(item) == "select multi":
        return
    else:
        item.setdefault("validation", {}).setdefault("required", "required")


def listify_elements(obj):
    """function to normalize everything by listifying it even when there's only one"""
    if isinstance(obj, dict):
        ret = OrderedDict()
        for k,v in obj.items():
            if not k.startswith("@") and not k.startswith("#"):
                if isinstance(v, list):
                    ret[k] = [listify_elements(item) for item in v]
                else:
                    ret[k] = [listify_elements(v)]
            else:
                ret[k] = v
        return ret
    elif isinstance(obj, list):
        log.error("obj passed to listify_elements should not be a list. %s", pformat(obj))
    else:
        return obj

def include_to_question(index, idmap):
    if not isinstance(index, dict):
        return
    for k,vlist in index.items():
        if k == "include":
            qlist = []
            for v in listify(vlist):
                if "@qref" in v:
                    qlist.append(idmap[v["@qref"]])
            index["question"] = qlist
            del index["include"]
        else:
            for item in listify(vlist):
                include_to_question(item, idmap)
    return index



def build_page(element):
    '''Make a page object from an arbitrary dict (used for building demographic survey page)'''
    page = []
    for k,v in element.items():
        for obj in listify(v):
            page.append([k, obj])
    return page

def build_pages_(index):
    level = index["@grouping"]
    pages = []
    interweave = True if index["@interweave_next_level"] == "true" else False
    for group in listify(index.get("group", [])):
        pages.extend(pages_from_group(group, level, interweave=interweave))
    return pages


def pages_from_group(group, level, base_page=None, interweave=True):
    pages = []
    if not base_page:
        base_page = []
    base_page.extend(page_attributes(group))

    if "page" in group and "group" in group:
        raise InvalidIndexError(group)

    # if we are at, or deeper than the target level, we'll only return one page
    if level != "page" and level != "last" and int(group["@level"]) >= int(level):
        pages.append(pagify_group(group, base_page, int(level), interweave))
    elif "page" in group:
        if level == "page":
            pages.extend(
                pages_from_page_list(
                    listify(group["page"]),
                    base_page))
        else:
            pages.append(pagify_group(group, base_page, int(level), interweave))
    elif "group" in group:
        for g in listify(group["group"]):
            pages.extend(pages_from_group(g, level, base_page=base_page))

    return pages

def pagify_group(group, base_page, level, interweave):
    
    
    page = [
        ("title", group["@title"]),
    ]
    if "text" in group:
        page.append(("text", delistify(group["text"])))
    page.extend(base_page)

    group_level = int(group["@level"])
    #if group_level == level:
    #if "instructions" in group:
        #page.append(("instructions", delistify(group["instructions"])))

    if group_level - level < 0:
        if "instructions" in group:
			page.append(("instructions", delistify(group["instructions"])))
 
    #if group_level - level == 1 and interweave:
        #if "instructions" in group:
            #page.append(("instructions", delistify(group["instructions"])))

    for k,v in group.items():
        if k == "page":
            page.extend(page_from_page_list(listify(v)))
        elif k == "group":
            for g in listify(v):
                if int(g["@level"]) - level == 1 and interweave:
                    if "instructions" in g:
                        page.append(("instructions", delistify(g["instructions"])))
                page.extend(page_from_page_list(get_all_elements(["page"], g)))
    try:
        page.append(("comment_ref", group["@comment_ref"]))
    except KeyError:
        print "Looks like there is a group without a comment ref, the group's title is '{}'".format(group.get("@title", ""))
        sys.exit(1)
    return page

def page_from_page_list(page_list):
    '''Get all relevant elements from a list of pages and put them in
    order on a single page - used when level is an integer.
    '''
    page = []
    take_names = ["question"]
    ignore_names = ["@title", "@comment_ref", "instructions", "text"]

    for page_element in page_list:
        for name,value_list in page_element.items():
            for value in listify(value_list):
                if name in take_names:
                    page.append((re.sub("^@", "", name), value))
                elif name not in ignore_names:
                    log.error("Unexpected element while building pages from index. " + name + " " + value)
    return page

def get_all_elements(names, obj):
    '''Return a list of all elements whose key is in names. If the element is a
    list, extend the return value with it rather than appending'''
    if not isinstance(obj, dict):
        return []
    ret = []
    for k,v in obj.items():
        if k in names:
            ret.extend(listify(v))
        elif isinstance(v, dict) or isinstance(v, list):
            for item in listify(v):
                ret.extend(get_all_elements(names, item))
    return ret

def pages_from_page_list(page_list, base_page):
    pages = []
    for page_tag in page_list:
        pages.append(pagify_page(page_tag, base_page))
    return pages


def pagify_page(page_tag, base_page):
    page = [('title', page_tag['@title'])] + base_page
    page.extend(page_elements(page_tag,
                              ["text", "instructions", "question"]))
    page.append(("comment_ref", page_tag.get("@comment_ref", "default")))
    return page


def page_elements(page_tag, take_names):
    page = []
    for k,vlist in page_tag.items():
        if k in take_names:
            for v in listify(vlist):
                page.append((re.sub("^@", "", k), v))
    return page



def page_attributes(group):
    '''Takes in a single group element and returns the start of a page
    with the group's top level attributes filled in. This is for when
    target level is < group level. To get a single page from a group,
    use pagify_group.
    '''
    ignore_names = ["group", "page", "@level", "text", "@title", "@comment_ref", "instructions"] # , "question"
    take_names = []
    page = []
    for name,value in group.items():
        if name in ignore_names:
            continue
        elif name in take_names:
            page.append((re.sub("^@", "", name), value))
        else:
            log.error("Unexpected element while building pages from index. " + str(name) + " " + str(value))
    return page




def build_forward_display_refs(questions, idmap):
    """Take any question that has a display_when or display_where, and add
an attribute to the option referenced... this is to aid in building
the page. For display_when, add displayq=qid to the option. When an
option with displayq is encountered, logic can be added to display the
question when necessary. For display_where, make_space=qid is added to
the option - when building the html, we'll create an empty div with an
attribute so that when rendering the question we can find the div and
render it there.
    """
    for question in questions["question"]:
        dwlist = []
        for dwoptid in question.get("@display_when", "").split(","):
            if dwoptid == "":
                continue
            # this if is for display_whens that refer to questions
            # instead of options (true/false) which are converted to
            # select multi
            if re.search(".*[0-9]$", dwoptid):
                dwoptid = dwoptid + ".A"
            opt = idmap[dwoptid]
            opt.setdefault("displayq", []).append(question["@id"])
            dwlist.append(dwoptid)
        if "@display_when" in question:
            question["@display_when"] = dwlist
        if "@display_where" in question:
            opt = idmap[question["@display_where"]]
            opt.setdefault("make_space", []).append(question["@id"])


def get_questionnaire(filename):
    """Grab XML file from disk and turn it into a python dictionary"""
    try:
        xml = open(filename).read()
    except:
        xml = open("../" + filename).read()

    questionnaire = xmltodict.parse(xml)["questionnaire"]
    return questionnaire

def get_index_tree(index):
    tree = build_tree(index, "@title", ["group", "page"])
    return tree



def get_id_bnf_mapping(questions):
    # Each BNF statement maps to either, an option, or a question (or a response, which makes it map to the question id)
    # The BNF statement is generated if the option is selected, or if the question is shown
    # EXCEPT in the case of the BNF_mapping containing a <when> in which case it is only shown if the reffed option is selected
    id_to_bnf = {}
    for q in questions["question"]:
        set_id_bnf_mapping(id_to_bnf, q)
#        if "BNF_mapping" in q:
#            id_to_bnf[q["@id"]] = listify(q["BNF_mapping"])
#        if not "response" in q:
#            continue
#        else:
#            if "BNF_mapping" in delistify(q["response"]):
#                id_to_bnf[q["@id"]] = listify(q["response"]["BNF_mapping"])
#            for opt in delistify(q["response"]).get("option", []):
#                if "BNF_mapping" in opt:
#                    id_to_bnf[opt["@id"]] = listify(opt["BNF_mapping"])

    return id_to_bnf


class InvalidIndexError(Exception):
    def __init__(self, element):
        self.element = element

    def _app_attr(self, name, ret_str):
        if name in self.element:
            ret_str += (name +  "=" + str(self.element[name]) + " ")
        return ret_str

    def __str__(self):
        ret_str = "Element: "
        ret_str = self._app_attr("@title", ret_str)
        ret_str = self._app_attr("@level", ret_str)
        ret_str = self._app_attr("@comment_ref", ret_str)
        return  ret_str + " contains both a group and a page."
