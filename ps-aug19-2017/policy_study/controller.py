from policy_study import db
from policy_study import app
from datetime import datetime
import random
from copy import deepcopy
from policy_study import policies as pmod
hashfunc = app.config["HASHFUNC"]
from policy_study.exceptions import UserNotFoundError, ConfigItemNotFoundError, PSError
from validation import clean_display_when_questions, clean_clozes_in_options, clean_clones
import logging as log

users = db.conns["users"]
config = db.conns["config"]
questionnaire = db.conns["questionnaire"]
logs = db.conns["logs"]

def insert_response(idmap, clone_map, user=None, policy=None, question=None, response=None, rtype=None):
    q_obj = questionnaire.find_one({"username": user, "policy_name": policy, "state": { "$in": ["new", "draft"] }})
    if not q_obj:
        q_obj = {
            "username": user,
            "policy_name": policy,
            "state": "draft",
            "questions": {}}
    if q_obj["state"] == "new":
        q_obj["state"] = "draft"

#    print("response is: "+response)

    if rtype == "append":
        if response not in q_obj["questions"].setdefault(str(question), []):
            q_obj["questions"][str(question)].append(response)
    elif rtype == "remove":
        resps = q_obj["questions"].get(str(question), [])
        q_obj["questions"][str(question)] = [r for r in resps if r != response]
    elif response != None:
        q_obj["questions"][str(question)] = response
    else:
        print("Experimental - when calling controller.insert_response with response==None, delete the answer to the question given. This should fix the issue where deselecting a radio button which makes a clone wasn't working.")
        del q_obj["questions"][str(question)]

    clean_display_when_questions(q_obj, idmap)
    clean_clozes_in_options(q_obj, idmap)
    clean_clones(q_obj, idmap, clone_map)
    print q_obj
    questionnaire.save(q_obj)

def clear_responses(user, policy, qid):
    q_obj = questionnaire.find_one({"username": user.get_id(), "policy_name": policy, "state": "draft"})
    if not q_obj:
        log.warn("attempting to clear responses on non existent questionnaire. policy=%s user=%s",
               policy, user.get_id())
        raise QuestionnaireNotFoundError(user, policy)
    else:
        for tid in q_obj["questions"].keys():
            if tid == qid or tid.startswith(qid + ">"):
                del q_obj["questions"][tid]
    questionnaire.save(q_obj)

def is_draft(user, policy):
    q_obj = questionnaire.find_one({"username": user.get_id(), "policy_name": policy, "state": "draft"})
    if q_obj:
        return True
    else:
        return False

def create_policy_questionnaire(policy, user):
    q_obj = {
        "username": user,
        "policy_name": policy,
        "state": "new",
        "questions": {},
    }
    questionnaire.save(q_obj)
    return questionnaire.find_one(q_obj)


def insert_log(log):
    ret = logs.save(log)
    return ret

def get_current_questionnaire(user, policy):
    q_obj = questionnaire.find_one({"username": user.get_id(), "policy_name": policy, "state": { "$in": ["new", "draft"] }})
    if not q_obj:
        return {}
    return q_obj["questions"]

def get_current_questionnaire_document(user, policy):
    q_obj = questionnaire.find_one({"username": user.get_id(), "policy_name": policy, "state": { "$in": ["new", "draft"] }})
    if not q_obj:
        return {}
    return q_obj

def get_questionnaires(user):
    qs = questionnaire.find({"username": user.get_id()})
    return filter(lambda x: x["policy_name"] != "demosurvey" and x["policy_name"] != "general_comments", [ q for q in qs ])

def get_user(**kwargs):
    return users.find_one(kwargs)

def get_users(**kwargs):
    return users.find(kwargs)

def del_user(**kwargs):
    users.remove(kwargs)

def complete_study(current_user, policy_name):
    q_obj = questionnaire.find_one({"username": current_user.get_id(),
                                    "policy_name": policy_name,
                                    "state": "draft"})
    if not q_obj:
        q_obj = questionnaire.find_one({"username": current_user.get_id(),
                                        "policy_name": policy_name,
                                        "state": "new"})

    if not q_obj:
        q_obj = create_policy_questionnaire(policy_name, current_user.get_id())
    q_obj["state"] = "completed"
    q_obj["date_completed"] = datetime.today().isoformat()
    delete_from_user(current_user, policies=policy_name)
    questionnaire.save(q_obj)

def new_user(userid, isadmin=False, password=None):
    u = {
        "isadmin": isadmin,
        "date_created": datetime.today().isoformat(),
        "done_demographic_survey": False
    }
    if not isadmin:
        userhash = hashfunc(userid)
        userid = userhash.hexdigest()
        u.update({
            "name": userid,
            "hash_name": userhash.name,
        })
    else: # is admin
        passhash = hashfunc(password)
        u.update({
            "name": userid,
            "hash_name": passhash.name,
            "policies": [],
            "password_hash": passhash.hexdigest()
        })
    if users.find_one({"name": userid}):
        raise PSError("User name " + userid + " already taken")
    users.insert(u)

if not users.find_one({"name": "admin"}):
    new_user("admin", isadmin=True, password="admin")

def update_user(current_user, **kwargs):
    u_obj = users.find_one({"name": current_user.get_id()})
    u_obj.update(kwargs)
    users.save(u_obj)

def change_admin_password(admin_name, new_password):
    u = users.find_one({"name": admin_name})
    if u:
        u["password_hash"] = hashfunc(new_password).hexdigest()
        users.save(u)
    else:
        raise UserNotFoundError(admin_name)

def update_config(**kwargs):
    conf = config.find_one()
    conf.update(kwargs)
    config.save(conf)

def get_config(item=None, default=None):
    conf = config.find_one()
    ## set defaults ##
    if not "policies_per_user" in conf:
        conf["policies_per_user"] = 3
        config.save(conf)
    if not item:
        return conf
    else:
        return conf.get(item, default)

def delete_from_config(**kwargs):
    conf = config.find_one()
    for k,v in kwargs.items():
        if not k in conf:
            raise ConfigItemNotFoundError(k)
        cur_v = conf[k]
        if not isinstance(cur_v, list):
            continue
        if not isinstance(v, list):
            v = [v]
        for item in v:
            cur_v.remove(item)
    config.save(conf)

def append_config(**kwargs):
    conf = config.find_one()
    for k,v in kwargs.items():
        if not k in conf:
            log.warn("Warning - key: %s was expected in conf but not found... setting to empty list and adding %s", str(k), str(v))
            conf[k] = []
        cur_v = conf[k]
        if not isinstance(v, list):
            v = [v]
        conf[k] = cur_v + v
    config.save(conf)

def append_user(user, **kwargs):
    user = users.find_one({"name": user.get_id()})
    for k,v in kwargs.items():
        if not k in user:
            raise ConfigItemNotFoundError(k)
        cur_v = user[k]
        if not isinstance(v, list):
            v = [v]
        user[k] = cur_v + v
    users.save(user)

def add_policies_to_user(user, policies):
    user = users.find_one({"name": user.get_id()})
    for newpol in policies:
        if newpol not in user.setdefault("policies", []):
            user["policies"].append(newpol)
    users.save(user)


def delete_from_user(user, **kwargs):
    user = users.find_one({"name": user.get_id()})
    for k,v in kwargs.items():
        if not k in user:
            raise ConfigItemNotFoundError(k)
        cur_v = user[k]
        if not isinstance(cur_v, list):
            continue
        if not isinstance(v, list):
            v = [v]
        for item in v:
            cur_v.remove(item)
    users.save(user)

def get_policies_for_user(user, **kwargs):
    kwargs.update({"name": user.get_id()})
    u = users.find_one(kwargs)
    if "policies" in u:
        return filter(lambda x: x != "demosurvey", u["policies"])
    elif u["isadmin"]:
        u["policies"] = []
        users.save(u)
        return []
    else:
        policies = get_policy_set()
        u["policies"] = sorted(policies, key=pmod.policy_names_ordered.index)
        for policy in u["policies"]:
            create_policy_questionnaire(policy, user.get_id())
        users.save(u)
        return policies

def get_policy_set():
    policies = []
    conf = get_config()
    num_policies = conf["policies_per_user"]

    # policies_used is name:num_used map of all policies that have ever been in the system
    # filter it down to ones that are configured to be used now
    policies_used = deepcopy(conf["policies_used"])
    for name,num in policies_used.items():
        if name not in pmod.policy_names_ordered:
            del policies_used[name]

    if int(num_policies) > len(policies_used):
        log.warn("policies per user (%s) is greater than number of policies (%s), resetting to (%s)",
               num_policies,
               len(policies_used),
               len(policies_used))
        num_policies = len(policies_used)
        conf["policies_per_user"] = num_policies
    def least_used(pols_used):
        sp = sorted(pols_used, key=lambda a: a[1])
        return [p for p in sp if p[1] == sp[0][1]]
    while len(policies) < num_policies:
        pols_used = [(k, v) for k,v in policies_used.items() if k not in policies]
        lu = least_used(pols_used)
        pol = random.choice(lu)[0]
        policies.append(pol)
        policies_used[pol] += 1
    conf["policies_used"].update(policies_used)
    config.save(conf)
    return policies

class QuestionnaireNotFoundError(Exception):
    def __init__(self, user, policy):
        self.userid = user.get_id()
        self.policy = policy
    def __str__(self):
        return "Was not able to find questionnaire for user " + self.userid + " and policy name " + self.policy
