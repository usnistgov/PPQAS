#!/usr/bin/python
"""
Usage:
  report.py bnf [options] <outputdir>
  report.py [options] extra <outfile>
  report.py [options] <outfile>
  report.py [options] <field> <outputdir>

Options:
  --dbname <dbname>
"""
import codecs
from docopt import docopt
import sys
import pymongo, cStringIO
import os, errno
from pprint import pformat
import unicode_csv as csv

if __name__ != "__main__":
    from policy_study import app
    from policy_study import db
else:
    sys.path = [sys.path[0]+"/.."] + sys.path
    from policy_study import app
    from policy_study import db


fields = ["xmlversion", "qaversion",
          "bnf_version", "_id", "app_version", "timestamp",
          "policy_name", "state", "user_agent_os",
          "user_agent_browser", "user_agent_version",
          "user_agent_language", "user_type",
          "type", "user_id", "url"]
fields_disp = ["xmlversion", "qaversion",
               "bnf_version", "object_id", "app_version", "timestamp",
               "policy_name", "state", "user_agent_os",
               "user_agent_browser", "user_agent_version",
               "user_agent_language", "user_type",
               "type", "user_id", "url"]

fields_147 = ["_id", "username", "policy_name", "state", "date_completed"]
fields_147_disp = ["object_id", "username", "policy_name", "state", "date_completed"]
# context handled differently

def quote(athing):
    return "\"" + (unicode(athing).replace("\n", "\\n").replace("\"", "\\\"") + "\"").encode("utf8")

dbname = app.config["DBNAME"]
logs = pymongo.MongoClient()[dbname][app.config["LOG_COLL_NAME"]]


def header_string(fields):
    ret = ", ".join(fields)
    return ret

def report_string(query_result):
    ret = ""
    for log in query_result:
        values = [ log.get(f, "NoField") for f in fields ]
        for k,v in log.get('context', {}).items():
            vstr=""
            if( isinstance(v, (list, tuple))):
                vstr +=', '.join(v)
            else:
                vstr = v

            values.append(unicode(k) + ":" + unicode(vstr))
        ret += ', '.join([ quote(v) for v in values ]) + "\n"
    return ret


def write_report(csvwriter, query_result):
    for log in query_result:
        values = [ log.get(field, "NoField") for field in fields ]
        for k,v in log.get('context', {}).items():
            vstr=""
            if( isinstance(v, (list, tuple))):
                vstr +=', '.join(v)
            else:
                vstr = v

            values.append(unicode(k) + ":" + unicode(vstr))
        csvwriter.writerow(values)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def write_bnf(dbname, outputdir):
    mkdir_p(outputdir)
    qaires_conn = db.conns["questionnaire"]
    qaires = qaires_conn.find()
    fname_set = set()
    for q in qaires:
        if not 'bnf_statements' in q:
            continue
        filename = (outputdir + "/" + q.get("state").capitalize()
                    + q["policy_name"].replace(" ", "_") + "_" + unicode(q["_id"])[:8])
        while filename in fname_set:
            filename = filename + "_2"
        fname_set.add(filename)

        bnfs = q['bnf_statements']
        outstr = "# " + pformat(q).replace("\n", "\n# ")
        with open(filename, 'w') as f:
            f.write((outstr + "\n").encode('utf-8'))
            for s in bnfs:
                f.write((s + "\n").encode('utf-8'))


def write_147(dbname, outfile):
    qaires_conn = db.conns["questionnaire"]
    qaires = qaires_conn.find()
    with open(outfile, 'w') as out:
        out.write(", ".join(fields_147_disp).encode("utf8") + ", statement\n".encode("utf8"))
        for q in qaires:
            if not 'bnf_statements' in q:
                continue
            first8_cols = ", ".join(map(lambda field: unicode(q.get(field, "None")), fields_147))
            for bnf in q['bnf_statements']:
                out.write((first8_cols + ", " + bnf + "\n").encode('utf8'))



def main(args):
    if args["--dbname"]:
        dbname = args["--dbname"]
    else:
        dbname = app.config["DBNAME"]

    if args["bnf"]:
        write_bnf(dbname, args["<outputdir>"])
        return

    if args["extra"]:
        write_147(dbname, args["<outfile>"])
        return


    logs = pymongo.MongoClient()[dbname][app.config["LOG_COLL_NAME"]]

    outputdir = args['<outputdir>']
    field = args['<field>']
    outfile = args['<outfile>']

    if outfile:
        with open(outfile, 'w') as f:
            csvwriter = csv.writer(f,quoting=csv.QUOTE_ALL)
            csvwriter.writerow(fields_disp)

            write_report(csvwriter , logs.find())
            # for log in logs.find():
            #     values = [ log.get(field, "NoField") for field in fields ]
            #     for k,v in log.get('context', {}).items():
            #         values.append(unicode(k) + ":" + unicode(v))
            #     csvwriter.writerow(values)
            #
            # f.write(header_string(fields_disp))
            # f.write("\n".encode('utf8'))
            # f.write(report_string(logs.find()))

    if outputdir and field:
        if field not in fields:
            print "<field> must be one of: \n" + "\n".join(fields)
            sys.exit(1)
        mkdir_p(outputdir)
        query = logs.find({}, fields={field: 1})
        field_vals = set([x[field] for x in query])
        for val in field_vals:
            if val is None:
                fname = safe_filename("%s_%s" % (field,val))
            else:
                fname = safe_filename(val)
            with open(outputdir + "/" + fname, 'w') as f:
                csvwriter = csv.writer(f,quoting=csv.QUOTE_ALL)
                csvwriter.writerow(fields)
                write_report(csvwriter , logs.find({field: val}))

                # f.write(header_string(fields).encode('utf8'))
                # f.write("\n".encode('utf8'))
                # f.write(report_string(logs.find({field: val})).encode('utf8'))

def safe_filename(fname):
    fname = unicode(fname)
    keep_chars = [('.', '_', '~', '-', '+')]
    ret = "".join([ch for ch in fname if ch.isalpha() or ch.isdigit() or ch in keep_chars])
    return ret



if __name__ == "__main__":
    args = docopt(__doc__)
    for a in args:
        if a == "--dbname" and args[a] is None:
            print a + " = " + "None given - using default (from config) of '" + dbname + "'"
        else:
            print a + " = " + unicode(args[a])
    main(args)
