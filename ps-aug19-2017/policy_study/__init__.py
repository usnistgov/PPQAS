__version__ = "0.1.1"

from flask import Flask
app = Flask(__name__)
app.config.from_object("policy_study.config")

import logging as l
l.basicConfig(level=l.INFO)


import policy_study.policies
import policy_study.unicode_csv
import policy_study.custom_jinja_filters
import policy_study.jinja_extensions
import policy_study.views

policy_study.views.initialize()
