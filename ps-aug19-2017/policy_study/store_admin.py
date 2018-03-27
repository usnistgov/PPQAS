#!/usr/bin/python
"""
Usage:
  store_admin.py cp [options] <target_name>
  store_admin.py rm <db_to_remove>

Options:
  --dbname <dbname>
"""
import pymongo
import sys
from docopt import docopt
if __name__ != "__main__":
    from policy_study import app
    from policy_study import db
else:
    sys.path = [sys.path[0]+"/.."] + sys.path
    from policy_study import app
    from policy_study import db

def main(args):
    if args["--dbname"]:
        dbname = args["--dbname"]
    else:
        dbname = app.config["DBNAME"]

    cli = pymongo.MongoClient()
    if args["cp"]:
        ret = cli.copy_database(dbname, args["<target_name>"], "localhost")
        print ret

    elif args["rm"]:
        if args["<db_to_remove>"] not in cli.database_names():
            print "Specified database '" + args["<db_to_remove>"] + "' does not exist"
            return
        print "Going to remove " + args["<db_to_remove>"] + " ...are you sure (yes/no)?"
        a = None
        while not a:
            a = raw_input()
            if a == "yes":
                 cli.drop_database(args["<db_to_remove>"])
                 print "dropped " + args["<db_to_remove>"]
                 return
            elif a == "no":
                return
            else:
                print "Please type yes or no"
                a = None


if __name__ == "__main__":
    args = docopt(__doc__)
    for a in args:
        if a == "--dbname" and args[a] is None:
            print a + " = " + "None given - using default (from config) of '" + app.config["DBNAME"] + "'"
        else:
            print a + " = " + unicode(args[a])
    main(args)
