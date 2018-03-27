import collections
from policy_study import app
import re
import elements
from policy_study.utils import (get_qid, listify, flatten,
                                qualify_cloze_id, base_qid_from,
                                get_type, is_cloze_id, is_float)
from validation import is_answered_and_valid, is_question_valid, num_from_thing
from copy import deepcopy
from pprint import pformat, pprint
from question import Question

import logging as log

def is_question_valid_qid(k, responses, id_map):
    qid = base_qid_from(k)
    q = id_map[qid]
    return is_question_valid(q, responses, id_map)

def get_bnf(questionnaire, questions, id_to_bnf, id_map):
    '''Assuming a pre-cleaned set of responses, generate the corresponding
    BNF statements based on the rules in the XML document'''
    if not questionnaire:
        return []
    all_responses = questionnaire['questions']

    responses={};
    #### sanitize responses to only include responses from valid questions
    for k,v in all_responses.items():
        if is_question_valid(k, all_responses, id_map):
            responses[k]=v

    all_answers = [item for sublist in [listify(v) for v in responses.values()] for item in sublist]
    relevant_bnfs = [id_to_bnf[x] for x in all_answers if x in id_to_bnf] # get all option BNF_mappings
    qid_keys = responses_by_only_qid(responses).keys()
    relevant_bnfs.extend(id_to_bnf[x] for x in qid_keys if x in id_to_bnf) # add all question (and response) BNF_mappings

    # Since it's always a full question that gets cloned, we're going
    # to get the qids from responses (take out >) that have 'clone' in
    # them. Then we'll copy all BNFs that have those ids (minus the
    # 'cloneX') and add cloned BNF objects to our list with cref's
    # changed to have cloneX appended

    # Get all question BNF_mappings for clones
#    resps_with_clone = filter(lambda x: "clone" in x, responses_by_only_qid(responses).keys())
#    for qidclone in resps_with_clone:
#        qid, clone_num = qidclone.split('clone')
#        for bnf_obj in id_to_bnf.get(qid, []):
#            relevant_bnfs.append([add_string_to_bnf_obj("clone" + clone_num, bnf_obj)])

    # Get all option BNF_mappings for clones
#    clone_answers = [x for x in all_answers if x != None and "clone" in x]
#    for ans in clone_answers:
#        opt_id, clone_num = ans.split('clone')
#        for bnf_obj in id_to_bnf.get(opt_id, []):
#            relevant_bnfs.append([add_string_to_bnf_obj("clone" + clone_num, bnf_obj)])

    return relevant_bnfs

def add_string_to_bnf_obj(string, bnf_obj):
    obj_copy = deepcopy(bnf_obj)
    add_string_to_vals(string, obj_copy, ["cref"])
    return obj_copy

def add_string_to_vals(string, athing, keys):
    if isinstance(athing, dict):
        for k,v in athing.items():
            if k in keys:
                athing[k] = v + string
            add_string_to_vals(string, v, keys)
    elif isinstance(athing, list):
        for t in athing:
            add_string_to_vals(string, t, keys)

def generate_bnf_statements(bnf_obj_list, questions, id_map):
    statements = []
    print("this is the bnf_obj_list: " + str(bnf_obj_list))
    for obj in flatten(bnf_obj_list):
        try:
            text = bnf_from_obj(obj, questions, id_map)
            if not text:
                raise Exception("Why is text false? should have raised exception text: {0}".format(text))
            statements.append(text)
        except ValidationError:
            log.debug("Validation error during bnf generation", exc_info=True)
        except BNFWhenNotSatisfied:
            log.debug("BNF When not satisfied", exc_info=True)

    return statements

def bnf_from_obj(bnf_obj, questions, id_map):
    responses_by_id = responses_by_only_id(questions)
    text = ""

    if "@when" in bnf_obj:
        a_when_exists = False
        when_optids = bnf_obj["@when"].split(",")
        not_found_opt_ids = []
        for optid in when_optids:
            answer = responses_by_id.get(get_qid(optid), [])
            if optid in answer or optid == answer:
                a_when_exists = True
            else:
                not_found_opt_ids.append(optid)
        if not_found_opt_ids:
            text += "INCOMPLETE BNF ({0}):".format(", ".join(not_found_opt_ids))

        if not a_when_exists:
            raise BNFWhenNotSatisfied()

    if bnf_obj.get("@type") != "json":
        return text + bnf_obj["#text"]
    for item in bnf_obj["#text"]:
        if isinstance(item, str) or isinstance(item, unicode):
            text += item
        else:
            newtext = resolve_bnf_json(item, responses_by_id, id_map)
            if newtext or newtext == "":
                text += unicode(newtext)
            else:
                raise Exception("Failure to resolve BNF json {0} should have raised an exception".format(item))
    return text

def resolve_bnf_json(obj, responses_by_id, id_map):
    if "insert" in obj:
        insert = obj["insert"]
        refd_id = insert.get("cref") if "cref" in insert else insert.get("qref")
        if not is_answered_and_valid(Question(id_map[refd_id]), responses_by_qualified_id(responses_by_id), id_map):
            raise ValidationError(insert)

        return resolve_insert(insert, responses_by_id, id_map)
    # elif "ident"  in obj:
    #     return resolve_bnf_ident(obj['ident'], responses_by_id)
    else:
        log.error("BNF json is not of any recognizable format:")
        log.error(pformat(obj))

def resolve_json(t, questions, id_map):
    if "insert" in t:
        return resolve_insert(t["insert"], questions, id_map)
    elif "cloze" in t:
      return resolve_cloze(t["cloze"], questions, id_map)

def resolve_insert(insert, questions, id_map):
    """For historical reasons, both cref and qref are supported as keys
    for the referenced id. If the referenced question is a select multi,
    it will be handled differently than other questions (and require a
    'separator')"""
    responses_by_id = responses_by_only_id(questions)

    if "cref" in insert or "qref" in insert:
        ref_id = insert["cref"] if "cref" in insert else insert["qref"]
        if get_type(id_map[ref_id]) == "select multi":
            insert["qref"] = ref_id
            retval=  resolve_select_multi_insert(insert, responses_by_id, id_map)
            return retval
        else:
            insert["cref"] = ref_id
            retval= resolve_cref_insert(insert, responses_by_id, id_map)
            return retval
    else:
        raise InsertError("NEITHER CREF NOR QREF IN INSERT:\n%s", unicode(insert))

#def resolve_cref_insert(insert, responses_by_id):
#    """Resolve inserts for questions that are not select multi"""
#    mod_dict = insert.get("mod", {})
#    ans = responses_by_id.get(insert['cref'])
#    if not isinstance(ans, list) and ans in mod_dict:
#       ans = mod_dict[ans]
#    ans = handle_insert_count(insert, ans)
#    ans = handle_insert_math(insert, ans)
#    if ans == None:
#        ans = app.config["QUESTIONNAIRE"]["default_insert_text"]
#    return ans

def resolve_cref_insert(insert, responses_by_id, id_map):
    """Resolve inserts for questions that are not select multi"""
    mod_dict = insert.get("mod", {})
    ans = responses_by_id.get(insert['cref'])
    if not isinstance(ans, list) and ans in mod_dict:
        ans = process_mod_text(mod_dict[ans], responses_by_id, id_map)
    ans = handle_insert_count(insert, ans)
    ans = handle_insert_math(insert, ans)
    if ans == None:
        ans = app.config["QUESTIONNAIRE"]["default_insert_text"]
    return get_text(id_map.get(ans, ans), responses_by_id, id_map)

def handle_insert_count(insert, ans):
    if "count" in insert and ans:
        if isinstance(ans, list):
            return len(ans)
        else:
            log.error("'count' present in insert with non-list (non select multi) answer. ans: %s  insert: %s", unicode(ans), unicode(insert))
    return ans

def handle_insert_math(insert, ans):
    if "math" in insert:
        if is_float(ans):
            return num_from_thing(ans) + num_from_thing(insert["math"])
        elif ans == None or ans=='':
            return app.config["QUESTIONNAIRE"]["default_insert_text"]
#            return "[Response to {0}]".format(insert.get("cref", insert.get("qref", None)))
        else:
            log.error("Insert contains math, but answer is not a number ans:%s  math: %s",
                      ans, unicode(insert["math"]))
    return ans



def resolve_select_multi_insert(insert, responses_by_id, id_map):
    '''Insert statements with "qref" point to select_multi questions, this
    gathers the list of responses, converts the ids to the corresponding
    text, handles any "mod" options, and then creates a string from the
    list of response text with the separator character joining the
    elements'''
    refd_id = insert["qref"]
    opt_id_list = responses_by_id.get(refd_id, []) # select multi response list
    if is_cloze_id(refd_id):
        opt_id_list = sorted(opt_id_list,
                             lambda x,y: id_map[refd_id]["options"].index(x) - id_map[refd_id]["options"].index(y))
    else:
        opt_id_list = sorted(opt_id_list)

    mod_obj = insert.get("mod", {})

    select_multi_responses_text = []
    for optid in opt_id_list:
        if optid not in mod_obj:
            # For a normal select multi, need to get the text from the
            # option. For a cloze select multi, the optid is the
            # actual text
            select_multi_responses_text.append(get_text(id_map.get(optid, optid), responses_by_id, id_map))
        else:
            select_multi_responses_text.append(process_mod_text(mod_obj[optid],
                                                                responses_by_id,
                                                                id_map))



    if "count" in insert or "math" in insert:
        ans = handle_insert_count(insert, select_multi_responses_text)
        ans = 0 if ans == [] else ans # not sure why handle_insert_count doesn't return 0 on []
        return unicode(handle_insert_math(insert, ans))
    else:
        return insert.get("separator", ", ").join(select_multi_responses_text)

def process_mod_text(txt, responses_by_id, id_map):
    txt = re.sub("~~\$", "\"", txt)
    strlist = elements.parse_cloze_string(txt)
    retstr = ""
    for thing in strlist:
        if isinstance(thing, dict):
            if "insert" in thing:
                try:
                    retstr += resolve_bnf_json(thing, responses_by_id, id_map)
                except ValidationError:
                    retstr += app.config["QUESTIONNAIRE"]["default_insert_text"]

        else: # better be a string
            retstr += thing
    return retstr

def get_text(obj, questions, id_map):
    if isinstance(obj, str) or isinstance(obj, unicode):
        return obj
    if isinstance(obj, collections.Iterable):
        if "text" in obj:
            txt = obj["text"]
        elif "#text" in obj:
            txt = obj["#text"]
        if isinstance(txt, dict):
            txt = txt.get("#text")
        if isinstance(txt, list):
            tlist = txt
            txt = ""
            for t in tlist:
                if isinstance(t, dict):
                    resolved = resolve_json(t, questions, id_map)
                    if resolved == None:
                        #TODO
                        raise Exception("Resolved should never be None, look into this")
                    txt += resolved
                else:
                    txt += t
    else:
        txt=obj
    return unicode(txt)

def resolve_cloze(cloze, questions, id_map):
    return questions.get(cloze["id"], app.config["QUESTIONNAIRE"]["default_insert_text"])

def resolve_bnf_ident(ident, responses_by_id):
    cref = ident["cref"]
    opt_text = ident["option_text"]
    bnf_text = ident.get('bnf_text', opt_text)
    answer_to_cloze = responses_by_id[cref]
    if answer_to_cloze == opt_text:
        return bnf_text
    elif isinstance(answer_to_cloze, list) and opt_text in answer_to_cloze:
        return bnf_text
    else:
        return None

def responses_by_only_qid(responses):
    """take in responses to questionnaire, return same dict, but keys with
'>' get only the latter(TODO - this should read 'former'?) part, CAUTION, could end up with key
collisions since some qids have multiple cloze ids inside them - just
used for getting all the qids in the response set"""
    new_responses = {}
    for k,v in responses.items():
        if ">" in k:
            k = k[:k.index(">")]
        new_responses[k] = v
    return new_responses

def responses_by_only_id(responses):
    """take in responses to questionnaire, return same dict, but keys with '>' get only the latter part"""
    new_responses = {}
    for k,v in responses.items():
        if ">" in k:
            k = k[k.index(">")+1:]
        new_responses[k] = v
    return new_responses

def responses_by_qualified_id(responses):
    new_responses = {}
    for k,v in responses.items():
        k = qualify_cloze_id(k)
        new_responses[k] = v
    return new_responses



class BNFError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return unicode(self.msg)

class InsertError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return unicode(self.msg)

class ValidationError(Exception):
    def __init__(self, failed_object):
        self.obj = failed_object
    def __str__(self):
        return "Validation failed for object {0}".format(self.obj)

class BNFWhenNotSatisfied(Exception):
    def __init__(self, *args, **kwargs):
        return Exception.__init__(self, *args, **kwargs)
