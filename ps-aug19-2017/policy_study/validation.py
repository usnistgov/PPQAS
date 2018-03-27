from utils import (flatten, listify, opt_id_from, qid_from, base_qid_from,
                   is_cloze_id, qualify_cloze_id, is_bare_cloze_id, get_clone_str,
                   add_string_to_ids, get_with_clone, delistify, strip_clone)
from clones import dec_clone, cloneify, clone_num, inc_clone
import re
from copy import deepcopy
from exceptions import UnsupportedCloningError
import logging as log
from pprint import pformat

def clean_clones(questionnaire, idmap, clone_map):
    """For any responses to clones, make sure that the previous question (which they were cloned from)     is answered in a way that would generate the current question - if not, delete the response to the     current question"""
    responses = questionnaire['questions']
    todelete = []
    answers = flatten([listify(resp) for resp in responses.values()])
    answers = list(answers)
    for qid in responses:
        if 'clone' in qid:
            cnum = clone_num(qid)
            base_qid = base_qid_from(qid)
            if(base_qid in clone_map):
                clone_opt = clone_map[base_qid]
                clone_opt = dec_clone(cloneify(clone_opt, cnum))
                if not clone_opt in answers:
                    log.info("clone appending " + qid)
                    log.info("because " + clone_opt + " is not in " + str(answers))
                    todelete.append(qid)
    for qid in todelete:
        del idmap[qid]
        del responses[qid]
    # recur until there are no new deletions
    if todelete:
        clean_clones(questionnaire, idmap, clone_map)

def clean_display_when_questions(questionnaire, idmap):
    '''clean up answers to questions which are not supposed to be
displayed because their display_when option is not there'''
    responses = questionnaire['questions'] # sorry, should have called it responses
    # todelete = []
    # for qid in responses:
    #     origqid = qid
    #     # TODO: consider replacing with base_qid_from
    #     if "clone" in qid:
    #         qid = re.sub("clone\d*", "", qid)
    #     if ">" in qid:
    #         qid = qid[:qid.index(">")]
    #     question = idmap[qid]
    #     if "@display_when" in question:
    #         todelete.append(origqid)
    #     for disp_when_opt in question.get("@display_when", []):
    #         disp_when_q = disp_when_opt[:-2] # cut off the ".A" or whatever
    #         if disp_when_opt in listify(responses.get(disp_when_q, [])):
    #             # Don't delete it
    #             todelete.remove(origqid)
    #             break
    #     if "@display_where" in question and not origqid in todelete:
    #         disp_where_opt = question["@display_where"]
    #         disp_where_q = disp_where_opt[:-2] # cut off the ".A" or whatever
    #         if disp_where_opt not in listify(responses[disp_where_q]):
    #             todelete.append(origqid)

    # if todelete:
    #     log.info("Deleting " + pformat(todelete))
    # for qid in todelete:
    #     del responses[qid]

    to_delete = []
    for qid in responses:
        if not qid_from(qid) in idmap:
            to_delete.append(qid)
        elif not would_be_displayed(idmap[qid_from(qid)], responses):
            to_delete.append(qid)
    for qid in to_delete:
        del responses[qid]

def clean_clozes_in_options(questionnaire, idmap):
    """Clean up answers to clozes whose parent option is not selected"""
    responses = questionnaire['questions']
    todelete = []
    answers = flatten([listify(resp) for resp in responses.values()])
    answers = list(answers)
    for qid in responses:
        # if it is a cloze_id
        if ">" in qid:
            opt_id = opt_id_from(qid)
            if unicode(opt_id) not in list(answers) and opt_id:
                print("appending " + qid)
                todelete.append(qid)
    for qid in todelete:
        del responses[qid]


def validate_questionnaire(questions, responses, idmap):
    """Checks all responses against validation parameters.

    Arguments:
    questions - the set of questions from the input file
    responses - the dict containing question ids and the user's responses
    idmap     - the dict which maps all input ids to input objects"""
    invalid = []
    for q in questions:
        if q["@id" ].startswith( "q.4.4.5.1"):
            print("here")
        # if q["@id" ] == "q.4.4.7.1.2":
        #     print("here")

        if not is_question_valid(q, responses, idmap):
            #have to remove the clone string - if a clone is invalid, so is its parent
            invalid.append(strip_clone(q["@id"]))
        #validate_all_clones(q, responses, idmap, invalid)
    # for k,v in responses.items():
    #     if "clone" in k and not ">" in k:
    #         clone_str = get_clone_str(k)
    #         cq = idmap[base_qid_from(k)]
    #         add_string_to_ids(clone_str, cq)
    #         if not is_question_valid(cq, responses, idmap):
    #             invalid.append(k)
    return invalid

def validate_all_clones(q, responses, idmap, invalid):
    if not q.get("@hasclones"):
        return
    resp = responses.get(q["@id"])
    if "clone" in q["@id"]:
        clone_str = inc_clone(get_clone_str(q["@id"]))
    else:
        clone_str = "clone1"
    go = True if resp else False
    while go:
        for r in listify(resp):
            go = False
            opt = get_with_clone(idmap, r)
            if opt and "@clone" in opt:
                for clone_qid in opt["@clone"].split(","):
                    cq = deepcopy(idmap[clone_qid])
                    add_string_to_ids(clone_str, cq, None, None)

                    if not is_question_valid(cq, responses, idmap):
                        invalid.append(base_qid_from(cq["@id"]))
                    # only one question in a list of cloned questions may have an option with clones
                    if "@hasclones" in cq:
                        resp = responses.get(cq["@id"])
                        if resp:
                            clone_str = inc_clone(clone_str)
                            #if we just got a clone that doesn't actually exist, don't try and validate it
                            if  clone_qid + clone_str in idmap:
                                go = True

                            #
                # if opt["@clone"] == q["@id"]:
                #     cq = deepcopy(q)
                #     add_string_to_ids(clone_str, cq)
                #     if not is_question_valid(cq, responses, idmap):
                #         invalid.append(base_qid_from(cq["@id"]))
                #     resp = responses.get(cq["@id"])
                #     if resp:
                #         go = True
                #         clone_str = inc_clone(clone_str)
                #     break
                # else:
                #     raise UnsupportedCloningError(q, opt)

def is_question_valid(q, responses, idmap):
    if would_be_displayed(q, responses):
        return is_fully_answered(q, responses, idmap)
    else:
        return True

def is_fully_answered(q, responses, idmap):
    if not "response" in q:
        return True
    response = delistify(q["response"])
    if response["@type"] == "select one":
        return is_select_one_answered(q, responses, idmap)
    elif response["@type"] == "cloze":
        return is_cloze_answered(q, responses)
    elif response["@type"] == "select multi":
        return is_select_multi_answered(q, responses, idmap)
    elif response["@type"] == "textbox":
        return is_textbox_answered(q, responses)
    elif response["@type"] == "memo":
        return is_memo_answered(q, responses)
    else:
        log.error("Unknown type of response in is_fully_answered, question follows:")
        log.error(pformat(q))

def is_textbox_answered(q, responses):
    validation = q["response"].get("validation", {})
    return validate_textbox(validation, q["@id"], responses)

def validate_textbox(validation, qid, responses):
    return validate_required(validation, qid, responses) and\
        validate_pattern(validation, qid, responses) and\
        validate_maxlength(validation, qid, responses) and\
        validate_minlength(validation, qid, responses)



def is_memo_answered(q, responses):
    validation = q["response"].get("validation", {})
    return validate_memo(validation, q["@id"], responses)

def validate_memo(validation, qid, responses):
    return validate_maxlength(validation, qid, responses) and\
        validate_minlength(validation, qid, responses) and\
        validate_required(validation, qid, responses)


def is_select_multi_answered(q, responses, idmap):
    validation = q["response"].get("validation", {})
    answered = True
    for optid in responses.get(q["@id"], []):
        option = get_with_clone(idmap, optid)
        answered = answered and is_option_answered(option, responses, q)
    return answered and validate_select_multi(validation, q["@id"], q["response"]["option"], responses)

def is_option_answered(option, responses, q):
    opt_text = option.get("text")
    if isinstance(opt_text, dict) and opt_text.get("@type", None) == "json":
        return is_cloze_list_answered(opt_text["#text"], q, responses)
    else:
        return True

def validate_select_multi(validation, qid, options, responses):
    return validate_required_select_multi(validation, qid, options, responses) and\
        validate_gt(validation, qid, responses) and\
        validate_gte(validation, qid, responses) and\
        validate_minlength(validation, qid, responses) and\
        validate_maxlength(validation, qid, responses) and\
        validate_lt(validation, qid, responses) and\
        validate_lte(validation, qid, responses) and\
        validate_eq(validation, qid, responses)

def validate_required_select_multi(validation, qid, options, responses):
    if "required" in validation:
        if not is_cloze_id(qid):
            ans_list = answer_list(responses)
            for opt in options:
                if opt in ans_list or opt['@id'] in ans_list :
                    return True
            return False
        else:
            resp = responses.get(qid)
            if resp is not None and resp != []:
                return True
            return False
    else:
        return True

def is_cloze_answered(q, responses):
    return is_cloze_list_answered(q["response"]["text"]["#text"], q, responses)

def is_cloze_list_answered(cloze_list, q, responses):
    ret = True
    for item in cloze_list:
        if isinstance(item, dict) and "cloze" in item:
            item = item["cloze"]
            qid = q["@id"] + ">" + item["id"]
            validation = item.get("validation", {})
            if not validate_required(validation, qid, responses):
                return False
            if item["type"] == "textbox":
                ret = validate_textbox(validation, qid, responses)
            elif item["type"] == "select multi":
                ret = validate_select_multi(validation, qid, item["options"], responses)
            elif item["type"] == "memo":
                ret = validate_memo(validation, qid, responses)
            elif item["type"] == "select one":
                ret = validate_select_one_cloze(validation, qid, responses)
            elif item["type"] == "numerical":
                ret = validate_numerical(validation, qid, responses)
            else:
                log.error("Unknown type of cloze in is_cloze_list_answered in validation.py")
            if not ret:
                return False

    return True

def is_answered_and_valid(question_obj, responses, idmap):
    """Used by bnf.py to determine whether questions/clozes referenced by inserts are validly answered"""
    if is_bare_cloze_id(question_obj.tid):
        return is_cloze_list_answered([{"cloze": question_obj}], {"@id": question_obj.pid}, responses)
    else:
        return is_question_valid(question_obj, responses, idmap)

def is_select_one_answered(q, responses, idmap):
    selected_optid = responses.get(q["@id"], None)
    if not selected_optid:
        if q.get("response", {}).get("validation", {}).get("required", "") == "required":
            return False
        else:
            return True
    opt = get_with_clone(idmap, selected_optid)
    return is_option_answered(opt, responses, q)

def validate_select_one_cloze(validation, qid, responses):
    if "required" in validation:
        if not responses.get(qid, None):
            return False
    return True

def validate_numerical(validation, qid, responses):
    return validate_min(validation, qid, responses) and\
        validate_pattern(validation, qid, responses) and\
        validate_max(validation, qid, responses) and\
        validate_step(validation, qid, responses) and\
        validate_gt(validation, qid, responses) and\
        validate_gte(validation, qid, responses) and\
        validate_lt(validation, qid, responses) and\
        validate_lte(validation, qid, responses) and\
        validate_eq(validation, qid, responses)


def validate_gt(validation, qid, responses):
    if "gt" in validation and qid in responses:
        target_qid = qualify_cloze_id(validation["gt"])
        target_val = num_from_thing(responses.get(target_qid, None))
        if target_val != None:
            return num_from_thing(responses[qid]) > target_val
    return True

def validate_lt(validation, qid, responses):
    if "lt" in validation and qid in responses:
        target_qid = qualify_cloze_id(validation["lt"])
        target_val = num_from_thing(responses.get(target_qid, None))
        if target_val != None:
            return num_from_thing(responses[qid]) < target_val
    return True


def validate_gte(validation, qid, responses):
    if "gte" in validation and qid in responses:
        target_qid = qualify_cloze_id(validation["gte"])
        target_val = num_from_thing(responses.get(target_qid, None))
        if target_val != None:
            return num_from_thing(responses[qid]) >= target_val
    return True

def validate_lte(validation, qid, responses):
    if "lte" in validation and qid in responses:
        target_qid = qualify_cloze_id(validation["lte"])
        target_val = num_from_thing(responses.get(target_qid, None))
        if target_val != None:
            return num_from_thing(responses[qid]) <= target_val
    return True

def validate_eq(validation, qid, responses):
    if "eq" in validation and qid in responses:
        target_qid = qualify_cloze_id(validation["eq"])
        target_val = num_from_thing(responses.get(target_qid, None))
        if target_val != None:
            return num_from_thing(responses[qid]) == target_val
    return True

def validate_min(validation, qid, responses):
    if responses.get(qid, None) != None and "min" in validation:
        try:
            ans = num_from_thing(responses[qid])
            return ans >= num_from_thing(validation["min"])
        except Exception:
            log.error("Question response is not a number: " + responses[qid], exc_info=True)
            return False
    return True

def validate_max(validation, qid, responses):
    if responses.get(qid, None) != None and "max" in validation:
        try:
            ans = num_from_thing(responses[qid])
            return ans <= num_from_thing(validation["max"])
        except Exception:
            log.error("Question response is not a number: " + responses[qid], exc_info=True)
            return False
    return True

def validate_step(validation, qid, responses):
    if responses.get(qid, None) != None and "step" in validation and "min" in validation:
        try:
            ans = num_from_thing(responses[qid])
            mini = num_from_thing(validation["min"])
            step = num_from_thing(validation["step"])
            return ans == ((ans - mini) / step) * step + mini
        except Exception:
            log.error("Question response is not a number: " + responses[qid], exc_info=True)
            return False
    return True

def validate_required(validation, qid, responses):
    if "required" in validation:
        if responses.get(qid, None):
            return True
        else:
            return False
    return True

def validate_pattern(validation, qid, responses):
    if "pattern" in validation:
        resp = responses.get(qid, "")
        patt = validation["pattern"]
        # html5 pattern must match entire string
        if patt[-1] != "$":
            patt = patt + "$"

        if not re.match(patt, resp):
            return False
    return True

def validate_maxlength(validation, qid, responses):
    if "maxlength" in validation:
        resp = responses.get(qid, None)
        maxlen = validation["maxlength"]
        # check if it was answered at all - not answered is still valid if not required
        if resp != None:
            return len(resp) <= num_from_thing(maxlen)
    return True

def validate_minlength(validation, qid, responses):
    if "minlength" in validation:
        resp = responses.get(qid, None)
        minlen = validation["minlength"]
        # check if it was answered at all - not answered is still valid if not required
        if resp != None:
            return len(resp) >= num_from_thing(minlen)
    return True


def would_be_displayed(q, responses):
    ## TODO - clone friendly?
   # if(q["@id"]=='q.4.4.5.1.1'):
    #    print("here")
    if (not "@display_when" in q) and (not "@display_where" in q):
        return True
    elif "@display_when" in q:
        any_display_when = False
        for opt_id in (q["@display_when"]):
            #any_display_when = any_display_when or (opt_id in map(strip_clone, answer_list(responses)))
            any_display_when = any_display_when or (opt_id in answer_list(responses))
        if not any_display_when:
            return False

    elif "@display_where" in q:
        if not q["@display_where"] in answer_list(responses):
            return False
    return True

def answer_list(responses):
    answers = flatten([listify(resp) for resp in responses.values()])
    return list(answers)


def num_from_thing(thing):
    if isinstance(thing, list):
        return len(thing)
    elif isinstance(thing, int):
        return thing
    elif isinstance(thing, str):
        try:
            return int(thing)
        except Exception:
            return float(thing)
    elif isinstance(thing, unicode):
        try:
            return int(thing)
        except Exception:
            return float(thing)
    elif thing == None:
        return None
    else:
        raise Exception("Unknown thing to convert to num: " + str(thing) + " type: " + str(type(thing)))
