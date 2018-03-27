import hashlib


SECRET_KEY = "devkey"
CSRF_ENABLED = True
DBNAME = "policydb"
USER_COLL_NAME = "users"
CONFIG_COLL_NAME = "config"
QUESTIONNAIRE_COLL_NAME = "questionnaire"
LOG_COLL_NAME = "logs"
HASHFUNC = hashlib.sha512
POLICY_DIR = "resources/policies/"
POLICY_FILE = "resources/policies.txt"
INPUT_FILE = "resources/test.xml"

#INPUT_FILE = "resources/pp_test-18nov2016.xml"

MAIL_SERVER = "smtp.nist.gov"
CONVERT_NONE_TO = ""
