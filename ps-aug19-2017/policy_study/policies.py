from policy_study import app, db

filename = app.config["POLICY_FILE"]
try:
    policy_file = open(filename)
except:
    policy_file = open("../" + filename)

pfile_lines = policy_file.readlines()

policy_names_ordered = [line.split("|")[0] for line in pfile_lines]
policies = [[line.split("|")[0], line.split("|")[1]] for line in pfile_lines]
policies_dict = {line.split("|")[0]: line.split("|")[1] for line in pfile_lines}
conf = db.conns["config"].find_one()

if not conf:
    db.conns["config"].insert({})
conf = db.conns["config"].find_one()
conf.setdefault("policy_filenames", {}).update(policies_dict)

conf["policies"] = policies
if not "policies_used" in conf:
    conf["policies_used"] = { pol[0]: 0 for pol in policies }
else:
    for p in policies:
        if not p[0] in conf["policies_used"]:
            conf["policies_used"][p[0]] = 0

# set up a default comment email address
if not conf.get('comments_emails', []):
    conf["comments_emails"] = ["michelle.steves@nist.gov"]

db.conns["config"].save(conf)
