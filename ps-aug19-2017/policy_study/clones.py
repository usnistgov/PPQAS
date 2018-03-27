import re
from copy import deepcopy
from utils import listify, delistify, add_string_to_ids, add_string_to_clones, add_string_to_qrefs, set_id_bnf_mapping, \
    add_string_to_whens, get_clone_str
from elements import populate_idmap

def prepare_clones(page, data, idmap, id_to_bnf, clones_map):
    """Given a page to be rendered, generate all clones based on responses to questions, and return the     new page with the clones added.
    Arguments:
    page: list of 2-tuples [("instructions", "instructions text"), ("question", question_object)...],
    data: dictionary of responses"""
    newpage = []
    for item in page:
        newpage.append(deepcopy(item))
        # for each question in the page
        if item[0] == "question":
            # for each option that has a clone attribute
            for opt in filter(lambda x: "@clone" in x, listify(delistify(item[1].get("response", {})).get("option", []))):
                clones = get_clones(opt, item[1], data, idmap, id_to_bnf, clones_map)
                if clones:
                    clones = prepare_clones(clones, data, idmap, id_to_bnf, clones_map)
                    #print("Clones is: " + str(clones))
                    newpage.extend(clones)
    return newpage

def get_clones(opt, q, data, idmap, id_to_bnf, clones):
    ret = []
    qs_to_check_for_when = []
   # print("This is the q: " + str(q) + " and this is opt id: "+ str ( opt["@id"]) + " and this is the listify: " + str(listify(data.get(q["@id"], []))))
    if opt["@id"] in listify(data.get(q["@id"], [])):
        clone_list = opt["@clone"].split(",")
        for clone_qid in clone_list:
            cloned_q = deepcopy(idmap[clone_qid])
            print ("Before being cloned:" + str(cloned_q))

            if "clone" in q["@id"]:
                clone_num = str(int(q["@id"].split("clone")[1]) + 1)
                add_string_to_ids("clone" + clone_num, cloned_q, idmap, clones)
                add_string_to_qrefs("clone" + clone_num, cloned_q, [ clone_name.split("clone")[0] for clone_name in clone_list ])
                add_string_to_clones("clone" + clone_num, cloned_q)
                qs_to_check_for_when.append(cloned_q)
            else:
                add_string_to_ids("clone1", cloned_q, idmap, clones)
                add_string_to_qrefs("clone1", cloned_q, clone_list)
                add_string_to_clones("clone1", cloned_q)
                qs_to_check_for_when.append(cloned_q)
            # check for any instances of old id still left around


            print ("after being cloned:" + str(cloned_q))
            idmap[cloned_q["@id"]] = cloned_q
            set_id_bnf_mapping(id_to_bnf, cloned_q )
            #print(str(idmap))
            ret.append(("question", cloned_q))

        # this has to happen AFTER all the clones have been created and inserted into the idmap
        for clone in qs_to_check_for_when:
            clone_str = get_clone_str(clone["@id"])
            add_string_to_whens(clone_str,  clone, idmap  )
            idmap[clone["@id"]] = clone
    return ret

def inc_clone(astr):
    """Given a clone id, increase the clone number by one"""
    m = re.search("clone([0-9]*)", astr)
    if m:
        m = int(m.group(1))
        m += 1
        newclonestr = "clone" + str(m)
        newstr = re.sub("clone[0-9]*", newclonestr, astr)
        return newstr
    else:
        return cloneify(astr, 1)

def cloneify(astr, num):
    """Add 'clone' + num to the id in astr in the correct places"""
    m = re.search("([^>]*)>?(.*$)?", astr)
    ret = m.group(1) + "clone" + str(num)
    if m.group(2):
        ret += ">" + m.group(2) + "clone" + str(num)
    return ret

def dec_clone(astr):
    """Given a clone id, decrease the clone number by 1"""
    if not "clone" in astr:
        raise NoCloneError(astr)
    num = clone_num(astr)
    if "clone1" in astr:
        return re.sub("clone1", "", astr)
    else:
        return re.sub("clone[0-9]*", "clone" + str(num-1), astr)

def clone_num(astr):
    """Get the number of the clone from a clone id"""
    m = re.search("clone([0-9]*)", astr)
    if m:
        m = int(m.group(1))
        return m


class NoCloneError(Exception):
    def __init__(self, astr):
        self.astr = astr
    def __str__(self):
        return "String " + self.astr + " does not contain a clone to increment"