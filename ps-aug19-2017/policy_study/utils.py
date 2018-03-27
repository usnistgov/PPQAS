import re
from pprint import pformat
from itertools import chain
from copy import deepcopy
from exceptions import IDError
from collections import OrderedDict

### ID manipulation functions ###

pattern = re.compile("[qcdb]\.([a-zA-Z0-9\.])+")

def get_qid(cloze_or_opt_id):
    """Get's qid from string like q.2.3.a or q.2.3.A.a (would return
    q.2.3). Does not work with clone qids or ids with >"""
    i = -1
    while re.match("[A-Za-z\.]", cloze_or_opt_id[i]):
        i -= 1
    if i == -1:
        i = len(cloze_or_opt_id)
    else:
        i += 1
    return cloze_or_opt_id[:i]

def opt_id_from(cloze_id):
    if ">" in cloze_id:
        cloze_id = re.sub("^[^>]*>", "", cloze_id)
    clone_str = get_clone_str(cloze_id)
    if clone_str:
        cloze_id = re.sub("clone[0-9]+$", "", cloze_id)
    opt_id = re.sub("\.[a-z]$", "", cloze_id)
    if not re.match(".*[A-Z]$", opt_id):
        return None
    if clone_str:
        opt_id = opt_id + clone_str
    return opt_id

def is_cloze_id(anid):
    if re.search("[a-z]$", strip_clone(anid)):
        return True
    else:
        return False

def qid_from(cloze_or_opt_id):
    """Returns a valid top level question id (no cloze or option info)"""
    qid = re.sub(">.*$", "", cloze_or_opt_id)
    clone_num = None
    if "clone" in qid:
        clone_num= qid[qid.find("clone"):]
        qid = qid[: qid.find("clone")]
    qid = get_qid(re.sub("\.[A-Z]", "", qid))
    if clone_num:
        qid += clone_num
    return qid

def base_qid_from(anid):
    qid = qid_from(anid)
    qid = strip_clone(qid)
    return qid

def strip_clone(anid):
    anid = re.sub("clone[0-9]*", "", anid)
    return anid

def is_bare_cloze_id(tid):
    """A bare cloze id is one without the '>' denoting the question it is
       under. i.e. q.2.3.a is bare an q.2.3>q.2.3.a is it's fully qualified
       counterpart"""
    if re.match("[qcdb]\.[0-9]+\.([0-9]\.)*([A-Z]*\.)?[a-z]+", tid):
        return True

def qualify_cloze_id(bare_cloze_id):
    """Takes a cloze id like q.2.3.a and returns q.2.3>q.2.3.a or
       q.2.3.A.a and returns q.2.3>q.2.3.A.a
       If given a regular qid, just returns it"""
    match = re.search("^([qcdb]\.[0-9.]+)(\.[A-Z]+)?\.[a-z]+", bare_cloze_id)

    # if not a bare cloze id
    if not match:
        # if a normal qid in q.#.#(clone#) form
        if re.match("^[qcdb]\.([0-9]+\.)*[0-9]+(clone[0-9]+)?", bare_cloze_id):
            return bare_cloze_id
        else:
            raise IDError(bare_cloze_id)

    q_or_opt_id = match.group(1)
    clone_str = get_clone_str(bare_cloze_id)
    return q_or_opt_id + clone_str + ">" + bare_cloze_id


def get_clone_str(tid):
    """Grabs the clone part of an id. i.e. takes clone3 from q.1.2clone3"""
    clone_match = re.search("(clone[0-9]+)$", tid)
    if clone_match:
        clone_str = clone_match.group(0)
    else:
        clone_str = ""
    return clone_str

def get_with_clone(adict, anid, default=None):
    """If anid is a clone id, strip the clone out to get from the dict, then
return a copy of the result object with the clone string added back in
to the ids"""
    if not "clone" in anid:
        return adict.get(anid, default)
    else:
        clone_str = get_clone_str(anid)
        obj = adict.get(strip_clone(anid))
        cobj = deepcopy(obj)
        add_string_to_ids(clone_str, cobj, None, None)
        print (cobj)
        return cobj

def set_id_bnf_mapping(id_to_bnf, q):
    if "BNF_mapping" in q:
        id_to_bnf[q["@id"]] = listify(q["BNF_mapping"])
    if not "response" in q:
        return
    else:
        if "BNF_mapping" in delistify(q["response"]):
            id_to_bnf[q["@id"]] = listify(q["response"]["BNF_mapping"])
        for opt in delistify(q["response"]).get("option", []):
            if "BNF_mapping" in opt:
                id_to_bnf[opt["@id"]] = listify(opt["BNF_mapping"])


def deepcopyChangeID(thing, appendix):
    if isinstance(thing, dict):
        for k, v in thing.iteritems():
            if isinstance(v, dict):
                deepcopyChangeID(v, appendix)
            if isinstance(v, list):
                for item in v:
                    deepcopyChangeID(item, appendix)
            if '@id' == k or 'id' == k :
                thing[k]=thing[k].split("clone")[0] + appendix


    if isinstance(thing, list):
        for item in thing:
            deepcopyChangeID(item, appendix)
    return thing

def add_string_to_whens(string, athing, idmap):
    if isinstance(athing, dict):
        for k,v in athing.items():
            if k=="displayq" or k=="make_space"  or k=="@display_when" :
                    for index,item in enumerate(v):
                        old_id=item
                        new_id=old_id.split("clone")[0] + string
                        if new_id in idmap:
                            v[index]=new_id
                            print("List Item Changed "+k+ " to value: "+ v[index])
            elif k=="@display_where":
                new_id=v.split("clone")[0] + string
                if new_id in idmap:
                    v=new_id
                    print("Display_where Changed "+k+ " to value: "+ v)
            #athing[k] = v
            add_string_to_whens( string, v, idmap)
    elif isinstance(athing, list):
        for t in athing:
            add_string_to_whens(string, t, idmap)


def get_questions_from_idmap(idmap):
    questions = []

    for key in idmap:
        if "response" in idmap[key] and idmap[key]["@id"].startswith("q") :
            questions.append(idmap[key])
    return questions


def add_string_to_ids(string, athing, idmap, clone_map):
    if isinstance(athing, dict):
        for k,v in athing.items():
            if k=="id" or k=="@id" :
                old_id=v
                new_id=v.split("clone")[0] + string
                if idmap:
                    print("Changing old id: "+ old_id+" with value: " +str(idmap[old_id]) + " to new id: " + new_id)
                    cloned_q = deepcopy(idmap[old_id])

                    #change the id and @id to the new ids
                    cloned_q = deepcopyChangeID(cloned_q, string)
                    idmap[new_id] = cloned_q
                    print("Deep Cloned and added to idmap with new ID: "+ new_id + " and value: " +str(cloned_q))

                athing[k] = new_id
            add_string_to_ids(string, v, idmap, clone_map)
    elif isinstance(athing, list):
        for t in athing:
            add_string_to_ids(string, t, idmap, clone_map)


def add_string_to_qrefs(string, athing, toclonelist):
    if isinstance(athing, dict):
        for k,v in athing.items():
            #have to handle 'mod' as well with recursive string replace
            #print("saw key " +str(k)+" of: " + str(v))
            keysToDelete=[]
            keysToAdd={}
            if k=="qref" or k=="cref":
                #only clone it if it starts with the string id of the elements to be cloned
                needToClone=False
                for clonelistitem in toclonelist:
                    if v.split("clone")[0].startswith(clonelistitem):
                        needToClone = True


                if needToClone:
                    athing[k] =  v.split("clone")[0] + string
                else:
                    athing[k] =  v.split("clone")[0]
                    #whoops!  found something we shouldn't have... don't change it and get out of here
                    break
            elif k== "mod" :
                #if this is a string, and the front of it looks like our id, then tack the clone string on the end
                for key in athing[k]:
                    value = athing[k][key]
                    print(key)
                    m1 = pattern.search(key)
                    #print("m1 group" + m1.group())
                    m2 = pattern.search( athing[k][key])
                    #print("m2 group" + m2.group())
                    if m2:
                        #in order to make any of this work, we can't just change the strings - we actually have to deep copy them and change the registered names too
                        value = value[:m2.span()[1]].split("clone")[0] + string  + value[m2.span()[1]:]
                        print("found value to change: "+ value)
                    if m1:
                        keysToAdd[ key[:m1.span()[1]].split("clone")[0] + string  + key[m1.span()[1]:]]= value
                        keysToDelete.append(key)
                        print("span for m1: "+str(m1.span()))

                for keyToAdd in keysToAdd:
                    athing[k][keyToAdd]=keysToAdd[keyToAdd]
                for keyToDelete in keysToDelete:
                    del athing[k][keyToDelete]


            #saw key mod of: {u'q.4.10.4.B': u'Lowercase Letters', u'q.4.10.4.C': u'Letters', u'q.4.10.4.A': u'Uppercase letters',
            # u'q.4.10.4.D': u"Special Characters: {'insert':{'qref': 'q.4.10.4.D.a'}}", u'q.4.10.4.E': u'Numbers'}


            add_string_to_qrefs(string, v, toclonelist)
    elif isinstance(athing, list):
        for t in athing:
            add_string_to_qrefs(string, t, toclonelist)


def add_string_to_clones(string, athing):
    if isinstance(athing, dict):
       for k,v in athing.items():
            if k=="clone" or k=="@clone":
                newCloneString=""
                for clone_qid in athing[k].split(","):
                   newCloneString+=(clone_qid.split("clone")[0]+string +",")
                athing[k]=newCloneString[:-1]
            add_string_to_clones(string, v)
    elif isinstance(athing, list):
        for t in athing:
           add_string_to_clones(string, t)


### Index functions ###

def get_first_page_title(index):
    if "page" not in index and "group" not in index:
        return index["@title"]
    for key, value in index.items():
        if key == "page":
            return value[0]["@title"]
        elif key == "group":
            return get_first_page_title(value[0])

def parents_for_title(index, title, parents=None):
    """Go through index and return a list of all titles which are parents
    of the element with the title which is passed in"""
    if not parents:
        parents = []
    for key, value in index.items():
        if key == "page":
            if not isinstance(value, list):
                value = [value]
            for item in value:
                if item["@title"] == title:
                    return parents
        elif key == "group":
            if not isinstance(value, list):
                value = [value]
            for item in value:
                parents.append(item["@title"])
                if item["@title"] == title:
                    return parents
                else:
                    ret = parents_for_title(item, title, parents)
                    if ret:
                        return ret
                parents.pop()

def first_page_name_for_section(section, qindex, level=None):
    if not level:
        level = qindex["@grouping"]
    new_obj = find_by_title(section, qindex)
    return first_child_of_level(new_obj, level)["@title"]

def first_child_of_level(obj, level):
    if "page" in obj and level!="page":
        return obj
    elif "page" in obj:
        return obj["page"][0]
    else:
        for g in obj["group"]:
            if g["@level"] == level:
                return g
            else:
                return first_child_of_level(g, level)

def find_by_title(title, qindex):
    if not isinstance(qindex, dict):
        return None
    if qindex.get("@title", None) == title:
        return qindex
    else:
        for k,v in qindex.items():
            if isinstance(v, list):
                for item in v:
                    ret = find_by_title(title, item)
                    if ret:
                        return ret
            elif isinstance(v, dict):
                ret = find_by_title(title, v)
    return None

### Convenience methods for handling input file objects generically ###

def get_type(obj):
    if "@type" in obj:
        return obj["@type"]
    elif "type" in obj:
        return obj["type"]
    elif "response" in obj and "@type" in delistify(obj["response"]):
        return delistify(obj["response"])["@type"]
    else:
        # TODO better exception or remove
        raise Exception("Object was expected to have a type but did not " + pformat(obj))

### Generic utility methods ###

def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)

def listify(x):
    if isinstance(x, list):
        return x
    else:
        return [x]

def delistify(x):
    if not isinstance(x, list):
        return x
    else:
        if len(x) == 1:
            return x[0]
        else:
            raise Exception("Tried to delistify a non unit list: " + str(x))

def json_map(f, json_obj):
    """call f on every non-list, non-dict item recursively"""
    if isinstance(json_obj, dict):
        ret = OrderedDict()
        for k,v in json_obj.items():
            ret[k] = json_map(f, v)
        return ret
    elif isinstance(json_obj, list):
        ret = []
        for v in json_obj:
            ret.append(json_map(f, v))
        return ret
    else:
        return f(json_obj)

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


### Page Operations ###
# A questionnaire page is represented by a list of two-tuples
# The first element of each tuple is the "key" and the second
# element is the "value". Ex.
# [('title', "Page 1"),
#  ('question', OrderedDict(blah blah blah)),
#  ('comment', OrderedDict(blah blah blah))]

def tuple_listify(input_dict):
    """Convert something like {'instructions': 'blah blah', 'question':
    [{...}, {...}]} to [('instructions', 'blah blah'), ('question',
    {...}), ('question', {...})]"""

    ret = []
    for k,v in input_dict.items():
        if isinstance(v, list):
            for item in v:
                ret.append((k, item))
        else:
            ret.append((k, v))
    return ret

def find_key(k, two_tuple_list):
    for item in two_tuple_list:
        if item[0] == k:
            return item[1]

def count_key(k, two_tuple_list):
    count = 0
    for item in two_tuple_list:
        if item[0] == k:
            count += 1
    return count