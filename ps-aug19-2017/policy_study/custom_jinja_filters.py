import re
from utils import opt_id_from, listify, get_qid, is_float, strip_clone
from bnf import resolve_insert as bnf_resolve_insert
import json
from policy_study import app


import re


def regexreplace(s, find, replace):
    """A non-optimal implementation of a regex filter"""
    return re.sub(find, replace, s)

def count_dots(s):
    return s.count(".")

def index_contains_any_qid(qindex, qids):
    if not isinstance(qindex, dict):
        return False
    if qindex.get("@qref", None) in qids:
        return qindex.get("@qref")
    else:
        for k,v in qindex.items():
            if isinstance(v, list):
                for item in v:
                    ret = index_contains_any_qid(item, qids)
                    if ret:
                        return ret
            elif isinstance(v, dict):
                ret = index_contains_any_qid(v, qids)
    return False

def resolve_insert(insert, questions, id_map):
    ans = bnf_resolve_insert(insert, questions, id_map)
    # if ans == 0, that's ok
    if ans == None or ans == "" or ans == False:
        return None
    return ans

def json_dump(obj):
    return json.dumps(obj)

def reset_general_comments(session):
    ret = session["general_comments_email"]
    del session["general_comments_email"]
    return ret


app.jinja_env.filters['resolve_insert'] = resolve_insert
app.jinja_env.filters['listify'] = listify
app.jinja_env.filters['regexreplace'] = regexreplace
app.jinja_env.filters['index_contains_any_qid'] = index_contains_any_qid
app.jinja_env.filters['count_dots'] = count_dots
app.jinja_env.filters['is_float'] = is_float
app.jinja_env.filters['json_dump'] = json_dump
app.jinja_env.filters['strip_clone'] = strip_clone
app.jinja_env.filters['map'] = map
app.jinja_env.filters['reset_general_comments'] = reset_general_comments
app.jinja_env.globals.update(get_qid=get_qid,
                             opt_id_from=opt_id_from,
                             index_contains_any_qid=index_contains_any_qid,
                             count_dots=count_dots,
                             is_float=is_float,
                             listify=listify,
                             json_dump=json_dump,
                             strip_clone=strip_clone,
                             map=map,
                             reset_general_comments=reset_general_comments,
                             resolve_insert=resolve_insert)