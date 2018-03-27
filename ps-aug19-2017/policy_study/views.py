import time
import re
from copy import deepcopy
from policy_study import app
from policy_study import __version__
from bson.objectid import ObjectId
from bson.errors import InvalidId
from collections import OrderedDict
from flask_login import (login_user, logout_user, login_required,
                         LoginManager, current_user)
from flask import redirect, render_template, url_for, flash, request, g, session
from policy_study.user import User
from policy_study.utils import (parents_for_title, json_map,
                                first_page_name_for_section,
                                listify, find_key, get_questions_from_idmap)

from policy_study.validation import validate_questionnaire
from policy_study.tree import get_next_child_of_parent, get_prev_child_of_parent, treesearch

from policy_study import bnf
from policy_study.elements import (listify_elements, get_questionnaire,
                                   convert_tf_select_multi, parse_clozes, add_required_rec,
                                   annotate_questions, populate_idmap,
                                   build_forward_display_refs, convert_nones_to,
                                   populate_map, get_id_bnf_mapping, build_page,
                                   include_to_question, build_pages_, get_index_tree, remake_clones)
from policy_study.clones import prepare_clones

from policy_study.forms import (LoginForm, SignupForm,
                                AdminAccountDeletionForm,
                                AdminAccountCreationForm,
                                AdminAccountChangePasswordForm,
                                AdminPasswordForm, PoliciesPerUserForm,
                                CommentsEmailsForm, CommentsAddEmailForm,
                                AdminTestingForm)

from view_helpers import remove_duplicate_titles

import logging as log
import policy_study.report as r
import json
from flask_mail import Mail, Message

from policy_study.exceptions import UserNotFoundError, PSError
import policy_study.controller as c
from policy_study.controller import QuestionnaireNotFoundError
from policy_study.policies import policy_names_ordered
from decorators import admin_required, nocache
from pprint import pprint, pformat

hashfunc = app.config["HASHFUNC"]

mail = Mail(app)

# set globals vars to None
static_text, questionnaire, idmap, pages, qindex, questions, clone_map, id_to_bnf, index_tree = tuple(
    [None for i in range(9)])


def initialize():
    global questionnaire
    global questions
    global idmap
    global static_text
    global qindex
    global title_map
    global pages
    global id_to_bnf
    global clone_map
    global index_tree
    clone_map = {}
    questionnaire = get_questionnaire(app.config["INPUT_FILE"])
    questionnaire = parse_clozes(questionnaire)
    convert_nones_to(questionnaire, app.config["CONVERT_NONE_TO"])
    add_required_rec(questionnaire)
    questions = questionnaire["questions"]
    convert_tf_select_multi(questions)
    annotate_questions(questions, clone_map)
    idmap = {}
    populate_idmap(questionnaire, idmap)
    static_text = questionnaire["static_text"]
    static_text = json_map(lambda x: x if x != None else "", static_text)
    qindex = listify_elements(questionnaire["index"])
    qindexq = include_to_question(deepcopy(qindex), idmap)
    raw_pages = build_pages_(qindexq)
    pages = OrderedDict()
    for page in raw_pages:
        pages[find_key("title", page)] = page
    build_forward_display_refs(questions, idmap)
    build_forward_display_refs(questionnaire["demographics_survey"], idmap)
    build_forward_display_refs(questionnaire["general_comments"], idmap)
    title_map = {}
    populate_map(qindex, title_map, "@title")
    id_to_bnf = get_id_bnf_mapping(questions)
    index_tree = get_index_tree(qindex)

    app.config["QUESTIONNAIRE"] = questionnaire


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(uid):
    u = c.get_user(name=uid)
    if u:
        return User(u)
    return None


@app.route('/')
def index():
    g.log = {"type": "http"}
    if not hasattr(current_user, "is_admin"):
        return redirect(url_for("login"))
    if not current_user.is_admin() and not current_user.done_demo_survey():
        return redirect(url_for("demosurvey"))

    return redirect(url_for("policies_for_review"))


@app.route('/help')
def help():
    g.log = {"type": "http"}
    return render_template("help.html",
                           elements=static_text,
                           **static_text['help'])


@app.route("/login", methods=["GET", "POST"])
def login():

    g.log = {"type": "http"}
    loginerror = ""
    loginerror_title = ""
    signuperror = ""
    signuperror_title = ""
    form = LoginForm()
    if form.validate_on_submit():
		
        if(request.form['btn'] == 'Submit'):
			#raise Exception("Hit create button")
			form.signupid.data = form.signupid.data.lower()
			# check if user already exists
			try:
				uid = hashfunc(form.signupid.data).hexdigest()
			except UnicodeEncodeError:
				uid = None
			user = load_user(uid)
			if user or c.get_user(name=form.signupid.data):
				flash(static_text["sign_up"]["name_taken"])
				signuperror = static_text["sign_up"]["name_taken"]
				signuperror_title = static_text["sign_up"]["name_taken_title"]
			elif not re.match("^[A-Za-z0-9]+$", form.signupid.data):
				flash("Invalid username")
				signuperror = static_text["sign_up"]["name_invalid"]
				signuperror_title = static_text["sign_up"]["name_invalid_title"]
			else:
				c.new_user(form.signupid.data)
				flash(static_text["sign_up"]["success"])
				login_user(load_user(uid))
				g.log = {"type": "signup"}
				return redirect(url_for("index"))
        else:
			form.loginid.data = form.loginid.data.lower()
			try:
				uid = hashfunc(form.loginid.data).hexdigest()
			except UnicodeEncodeError:
				uid = None
			# try to load normal user
			user = load_user(uid)
			if not user:
				# try to load admin user
				user = load_user(form.loginid.data)
			if not user:
				flash(static_text["sign_in"]["error_text"])
				loginerror = static_text["sign_in"]["error_text"]
				loginerror_title = static_text["sign_in"]["error_title_text"]
			else:
				g.log = {"type": "login"}
				if not user.is_admin():
					login_user(user)
					flash("Logged in " + form.loginid.data + " successfully.")
					return redirect(request.args.get("next") or url_for("index"))
				elif user.is_admin():
					return redirect(url_for("admin_password", username=user.name))

    return render_template("login.html",
                           elements=static_text,
                           loginerror=loginerror,
                           loginerror_title=loginerror_title,
                           signuperror=signuperror,
                           signuperror_title=signuperror_title,
                           form=form, **static_text["sign_in"])


@app.route("/signup", methods=["GET", "POST"])
def signup():
    g.log = {"type": "http"}
    signuperror = ""
    signuperror_title = ""
    form = SignupForm()
    if form.validate_on_submit():
        form.userid.data = form.userid.data.lower()
        # check if user already exists
        try:
            uid = hashfunc(form.userid.data).hexdigest()
        except UnicodeEncodeError:
            uid = None
        user = load_user(uid)
        if user or c.get_user(name=form.userid.data):
            flash(static_text["sign_up"]["name_taken"])
            signuperror = static_text["sign_up"]["name_taken"]
            signuperror_title = static_text["sign_up"]["name_taken_title"]
        elif not re.match("^[A-Za-z0-9]+$", form.userid.data):
            flash("Invalid username")
            signuperror = static_text["sign_up"]["name_invalid"]
            signuperror_title = static_text["sign_up"]["name_invalid_title"]
        else:
            c.new_user(form.userid.data)
            flash(static_text["sign_up"]["success"])
            login_user(load_user(uid))
            g.log = {"type": "signup"}
            return redirect(url_for("index"))

    return render_template("signup.html",
                           signuperror=signuperror,
                           signuperror_title=signuperror_title,
                           elements=static_text,
                           form=form, **static_text["sign_up"])

@app.route("/adminlogin/<string:username>", methods=["GET", "POST"])
def admin_password(username):
    username = username.lower()
    form = AdminPasswordForm()
    if form.validate_on_submit():
        passhash = hashfunc(form.data["password"]).hexdigest()
        user_obj = c.get_user(name=username,
                              password_hash=passhash)
        if user_obj:
            user = load_user(user_obj["name"])
            login_user(user)
            return redirect(url_for('admin_accounts'))
        else:
            flash("Username or password incorrect")
            return redirect(url_for('index'))
    return render_template("adminlogin.html", form=form, elements=static_text)
	
@app.route("/api/checkuser", methods=["POST"])
def checkuser():
    username = request.get_data()
    username = username.lower()
    uid = hashfunc(username).hexdigest()
    user = load_user(uid)
    if user or c.get_user(name=username):
        return "NO"
    return "YES"


@app.route("/logout")
@login_required
def logout():
    if 'invalid_questions' in session:
        del session['invalid_questions']
    utype = "admin" if current_user.is_admin() else "participant"
    g.log = {"type": "logout",
             "user_id": current_user.get_id(),
             "user_type": utype}
    logout_user()
    return redirect(url_for("login"))

@app.route("/admin_accounts", methods=["GET"])
@admin_required
@login_required
def admin_accounts(account_del_form=None,
                   account_create_form=None,
                   account_pwchange_form=None):
    admins = c.get_users(isadmin=True)
    admins = [a["name"] for a in admins]
    if not account_del_form:
        account_del_form = AdminAccountDeletionForm()
    account_del_form.accounts.choices = [(a, a) for a in admins]
    if not account_create_form:
        account_create_form = AdminAccountCreationForm()
    if not account_pwchange_form:
        account_pwchange_form = AdminAccountChangePasswordForm()
    return render_template("admin_accounts.html",
                           elements=static_text,
                           account_del_form=account_del_form,
                           account_create_form=account_create_form,
                           sel={"admin_accounts": "selected"},
                           account_pwchange_form=account_pwchange_form)


@app.route("/admin/account_delete", methods=["POST"])
@admin_required
@login_required
def admin_del():
    form = AdminAccountDeletionForm()
    admins = c.get_users(isadmin=True)
    admins = [a["name"] for a in admins]
    form.accounts.choices = [(a, a) for a in admins]

    if form.validate_on_submit():
        for name in form.data["accounts"]:
            name = name.lower()
            c.del_user(name=name)
    return admin_accounts(account_del_form=form)


@app.route("/admin/account_create", methods=["POST"])
@admin_required
@login_required
def admin_create():
    form = AdminAccountCreationForm()
    if form.validate_on_submit():
        username = form.data["username"].lower()
        try:
            c.new_user(username,
                       isadmin=True,
                       password=form.data["password"])
            flash("New admin user created succesfully")
        except PSError as e:
            flash(unicode(e))
        return redirect(url_for("admin_accounts"))
    return admin_accounts(account_create_form=form)


@app.route("/admin/account_pwchange", methods=["POST"])
@admin_required
@login_required
def admin_pwchange():
    form = AdminAccountChangePasswordForm()
    if form.validate_on_submit():
        form.user.data = form.user.data.lower()
        try:
            c.change_admin_password(form.user.data,
                                    form.newpassword.data)
            flash("Password change successful")
        except UserNotFoundError:
            flash("The user" + form.username.data + " does not exist")
        return redirect(url_for("admin_accounts"))
    return admin_accounts(account_pwchange_form=form)


@app.route("/admin_configure", methods=["GET"])
@admin_required
@login_required
def admin_configure(policiesper_form=None, comments_form=None, add_email_form=None):
    if not policiesper_form:
        policiesper_form = PoliciesPerUserForm()
        policiesper_form.policies_per_user.data = c.get_config("policies_per_user")
    if not comments_form:
        comments_form = CommentsEmailsForm()
        comments_form.comments_emails.choices = [(e, e) for e in c.get_config("comments_emails", default=[])]
    if not add_email_form:
        add_email_form = CommentsAddEmailForm()

    return render_template("admin_configure.html",
                           policiesper_form=policiesper_form,
                           comments_form=comments_form,
                           add_email_form=add_email_form,
                           elements=static_text,
                           sel={"admin_configure": "selected"},
                           **static_text["admin_configure"])


@app.route("/admin/policiesperuser", methods=["POST"])
@admin_required
@login_required
def admin_policies_per_user():
    form = PoliciesPerUserForm()
    num_policies = len(c.get_config()["policies"])
    if form.validate_on_submit():
        if int(form.policies_per_user.data) <= num_policies:
            c.update_config(policies_per_user=form.policies_per_user.data)
            flash("Value changed")
            return redirect(url_for('admin_configure'))
        else:
            flash("Policies per user must be less than or equal to " + unicode(num_policies))
    return admin_configure(policiesper_form=form)


@app.route("/admin/delete_email", methods=["POST"])
@admin_required
@login_required
def admin_delete_email():
    form = CommentsEmailsForm()
    form.comments_emails.choices = [(e, e) for e in c.get_config("comments_emails")]
    if form.validate_on_submit():
        c.delete_from_config(comments_emails=form.data["comments_emails"])
        flash("Deleted Successfully")
        return redirect(url_for('admin_configure'))
    return admin_configure(comments_form=form)


@app.route("/admin/add_email", methods=["POST"])
@admin_required
@login_required
def admin_add_email():
    form = CommentsAddEmailForm()
    if form.validate_on_submit():
        c.append_config(comments_emails=form.add_address.data)
        flash("Added Successfully")
        return redirect(url_for('admin_configure'))
    flash("problem")
    return admin_configure(add_email_form=form)


@app.route("/admin_reporting", methods=["GET", "POST"])
@admin_required
@login_required
def admin_reporting():
    report_string = r.header_string(r.fields) + "\n" + r.report_string(r.logs.find({}).sort("timestamp", -1))
    return render_template("admin_reporting.html",
                           elements=static_text,
                           report=report_string,
                           sel={"admin_reporting": "selected"},
                           **static_text["admin_reporting"])


@app.route("/admin_testing", methods=["GET", "POST"])
@admin_required
@login_required
def admin_testing():
    return redirect(url_for('policies_for_review'))


@app.route("/admin_testing_setup", methods=["GET", "POST"])
@admin_required
@login_required
def admin_testing_setup():
    form = AdminTestingForm()
    if request.method == 'POST':
        if request.args.get('action') == "add":
            c.add_policies_to_user(current_user, form.data["all_policies"])
        elif request.args.get('action') == "remove":
            to_delete = [p for p in form.data["selected_policies"] if not c.is_draft(current_user, p)]
            c.delete_from_user(current_user, policies=to_delete)
    policies = c.get_config()["policies"]
    selected_policies = c.get_policies_for_user(current_user)
    form.all_policies.choices = [(a[0], a[0]) for a in policies if a[0] not in selected_policies]
    form.selected_policies.choices = [(a, a) for a in selected_policies]
    return render_template("admin_testing_setup.html",
                           admin_testing_form=form,
                           elements=static_text,
                           sel={"admin_testing_setup": "selected"},
                           **static_text["admin_testing_setup"])


@app.route("/admin_about", methods=["GET", "POST"])
@admin_required
@login_required
def admin_about():
    users = c.get_users()[:]
    embellished_users = []
    for u in users:
        num_policies = len(u.get("policies", []))
        num_completed = c.questionnaire.find({"username": u['name'],
                                              "state": "completed"}).count()
        u.update(policies_assigned=num_policies,
                 policies_complete=num_completed)
        embellished_users.append(u)
    return render_template("admin_about.html",
                           elements=static_text,
                           config=c.get_config(),
                           sel={"admin_about": "selected"},
                           users=embellished_users)

@app.route("/demosurvey", methods=["GET", "POST"])
@login_required
def demosurvey():
    g.log = {"type": "http"}
    page = build_page(questionnaire["demographics_survey"])
    questionz = c.get_current_questionnaire(current_user, "demosurvey")

    return render_template("demo_survey.html",
                           questions=questionz,
                           elements=static_text,
                           idmap=idmap,
                           page=page,
                           **static_text["demographics_survey"])
						   
@app.route("/detailedInstructions", methods=["GET", "POST"])
@login_required						   
def detailedInstructions():						   
	g.log = {"type": "http"}
	page = build_page(questionnaire["detailed_instructions"])
	questionz = c.get_current_questionnaire(current_user, "detailedInstructions")
	return render_template("detailedInstructions.html",
                           questions=questionz,
                           elements=static_text,
                           idmap=idmap,
                           page=page,
                           **static_text["detailed_instructions"])							   

@app.route("/popupInstructions", methods=["GET", "POST"])
@login_required						   
def popupInstructions():						   
	g.log = {"type": "http"}
	page = build_page(questionnaire["popup_instructions"])
	questionz = c.get_current_questionnaire(current_user, "detailedInstructions")
	return render_template("popupInstructions.html",
                           questions=questionz,
                           elements=static_text,
                           idmap=idmap,
                           page=page,
                           **static_text["popup_instructions"])

@app.route("/policies")
@login_required
def policies_for_review():
    g.log = {"type": "http"}
    policies = c.get_policies_for_user(current_user)
    qs = c.get_questionnaires(current_user)
    draft_qs = filter(lambda x: x["state"] == u'draft', qs)
    new_qs = filter(lambda x: x["state"] == "new", qs)
    completed_qs = filter(lambda x: x["state"] == "completed", qs)

    cur_qs = new_qs[:]
    cur_qs.extend(draft_qs)
    current_policies = [x["policy_name"] for x in cur_qs]

    new_pols = [x["policy_name"] for x in new_qs]
    try:
        draft_pols = sorted([x["policy_name"] for x in draft_qs], key=policy_names_ordered.index)
    except ValueError:
        draft_pols = sorted([x["policy_name"] for x in draft_qs], key=policies.index)

    for policy in policies:
        if policy not in current_policies:
            new_pols.append(policy)

    try:
        new_pols = sorted(new_pols, key=policy_names_ordered.index)
    except ValueError:
        new_pols = sorted(new_pols, key=policies.index)

    return render_template("policies_for_review.html",
                           elements=static_text,
                           new_pols=new_pols,
                           draft_pols=draft_pols,
                           completed_qs=completed_qs,
                           **static_text["policies_for_review"])


@app.route("/general_comments", methods=["GET", "POST"])
def general_comments():
    g.log = {"type": "http"}
    page = build_page(questionnaire["general_comments"])

    if request.method == "POST":
        emails = c.get_config("comments_emails")
        g.log = {"type": "general comment",
                 "context": dict(request.form)}

        msg = Message("General Comment ",
                      sender="michelle.steves@nist.gov",
                      recipients=emails)
        msg.body = pformat(request.form)
        log.info("sending email %s", pformat(request.form))
        session["general_comments_email"] = "success"
        try:
            mail.send(msg)
        except Exception:
            log.error("Could not send message", exc_info=True)
            session["general_comments_email"] = "error"
        if "next" in request.args:
            return redirect(request.args["next"])
        else:
            return redirect(url_for('policies_for_review'))

    return render_template("general_comments.html",
                           elements=static_text,
                           page=page,
                           idmap=idmap,
                           questions=questionnaire,
                           indent_px=questionnaire["indent_px"],
                           **static_text["general_comments"])


@app.route("/trycomplete/<string:policy_name>/<path:section>")
def trycomplete(policy_name, section):
    g.log = {"type": "review_questionnaire"}

    if not policy_name in c.get_policies_for_user(current_user):
        return "Invalid policy name"

    qdoc = c.get_current_questionnaire_document(current_user, policy_name)
    qdoc["tried_to_complete"] = True
    c.questionnaire.save(qdoc)
    qdoc = c.get_current_questionnaire_document(current_user, policy_name)
    responses = qdoc.get("questions", {})
    questions_with_clones = get_questions_from_idmap(idmap)
    invalid_questions = validate_questionnaire(questions_with_clones, responses, idmap)
    session['invalid_questions'] = policy_name
    return render_template("trycomplete.html",
                           elements=static_text,
                           name=policy_name,
                           policy_id=policy_name,  # TODO proper id handling?
                           invalid_qids=invalid_questions,
                           section=section,
                           breadcrumbs="Review and Submit",
                           back_text=static_text["questionnaire"]["back_text"],
                           finish_text=static_text["questionnaire"]["finish_text"],
                           level=qindex["@grouping"],
                           index=qindex,
                           **static_text["completion_page"])


@app.route("/firsterror/<string:policy_name>")
def first_error_page(policy_name):
    resps = c.get_current_questionnaire(current_user, policy_name)

    questions_with_clones = get_questions_from_idmap(idmap)
    invalid_questions = validate_questionnaire(questions_with_clones, resps, idmap)
    for title, page in pages.items():
        for item in page:
            if item[0] == "question" and item[1]["@id"] in invalid_questions:
                first_error_section = title
                return redirect(url_for("policy_questionnaire", policy_name=policy_name, section=first_error_section))
    return redirect(url_for("policy_questionnaire", policy_name=policy_name))


@app.route("/policy/<string:policy_name>")
@app.route("/policy/<string:policy_name>/<path:section>")
@login_required
@nocache
def policy_questionnaire(policy_name, section=None):
    g.log = {"type": "http"}
    qaire = None
    try:
        p_id = ObjectId(policy_name)
        qaire = c.questionnaire.find_one(_id=p_id)
        policy_id = policy_name
        policy_name = qaire["policy_name"]
    except InvalidId:
        policy_id = policy_name

    if not policy_name in c.get_policies_for_user(current_user):
        if not current_user.is_admin():
            return "Invalid policy name"
    if not section:
        section = pages.items()[0][0]
        return redirect(url_for('policy_questionnaire', policy_name=policy_id, section=section))

    if section not in pages:
        section = first_page_name_for_section(section, qindex)
        return redirect(url_for('policy_questionnaire', policy_name=policy_id, section=section))

    page_name = section

    display_titles = parents_for_title(qindex, page_name)

    if display_titles[-1] != page_name:
        display_titles.append(page_name)

    breadcrumb_string = " > ".join(display_titles)

    prev_page_name = "Home"
    next_page_name = None
    for i, (name, pg) in enumerate(pages.items()):
        if name == page_name:
            if len(pages.keys()) > i + 1:
                next_page_name = pages.keys()[i + 1]
            break
        else:
            prev_page_name = name

    qdoc = c.get_current_questionnaire_document(current_user, policy_name)
    tried_to_complete = qdoc.get("tried_to_complete", False)
    invalid_questions = []
    if tried_to_complete:
        resps = qdoc["questions"]

        questions_with_clones = get_questions_from_idmap(idmap)
        invalid_questions = validate_questionnaire(questions_with_clones, resps, idmap)

    current_page_node = treesearch(page_name, index_tree)
    next_link_name = None
    prev_link_name = None
    next_link_node = get_next_child_of_parent(current_page_node)
    prev_link_node = get_prev_child_of_parent(current_page_node)
    if next_link_node != None:
        next_link_name = next_link_node.data
    if prev_link_node != None:
        prev_link_name = prev_link_node.data
    if not qaire:
        questionz = qdoc.get("questions", {})
    else:
        questionz = qaire
    page = pages[page_name]
    page = prepare_clones(page, questionz, idmap, id_to_bnf, clone_map)
    remove_duplicate_titles(page, questionz)

    responses = [r for r in [listify(resp) for resp in questionz.values()]]
    responses = reduce(lambda x, y: x + y, responses, [])

    g.policy_name = policy_name
    strquestions = {unicode(k): unicode(v) for k, v in questionz.items()}
    return render_template("questionnaire_page.html",
                           elements=static_text,
                           index=qindex,
                           breadcrumbs=breadcrumb_string,
                           responses=responses,
                           prev_page_name=prev_page_name,
                           next_page_name=next_page_name,
                           level=qindex["@grouping"],
                           questions=questionz,
                           strquestions=json.dumps(strquestions),
                           tried_to_complete=tried_to_complete,
                           name=policy_name,
                           policy_id=policy_id,
                           next_link_name=next_link_name,
                           prev_link_name=prev_link_name,
                           display=display_titles,
                           page=page,
                           pages=pages.keys(),
                           idmap=idmap,
                           section=section,
                           indent_px=questionnaire["indent_px"],
                           default_insert_text=questionnaire["default_insert_text"],
                           invalid_qids=invalid_questions,
                           **static_text['questionnaire'])


@app.route("/policycomplete/<string:policy_name>")
@login_required
def policy_complete(policy_name):
    g.log = {"type": "complete_questionnaire"}
    # make sure user has this policy
    if policy_name in c.get_policies_for_user(current_user):
        g.policy_name = policy_name
        c.complete_study(current_user, policy_name)
        if "invalid_questions" in session:
            del session["invalid_questions"]
    return redirect(url_for('policies_for_review'))


@app.route("/pdf/<string:filename>")
@login_required
def serve_pdf(filename):
    if not filename.endswith(".pdf"):
        filename = c.get_config()["policy_filenames"].get(filename)
    return render_template("pdf.html",
                           filename=filename)


#### API VIEWS ####
@app.route("/api/questionnaire", methods=["POST"])
@login_required
def question_response():
    data = json.loads(request.get_data())
    data["user"] = current_user.get_id()
    log.info("Data posted:\n" + unicode(data))
    if not data["policy"] in c.get_policies_for_user(current_user) and data["policy"]:
        log.warn("policy does not exist for this user")
        if not current_user.is_admin():
            return "you don't have access to this policy", 400
        else:
            log.warn("admin manually accessing policy")

    g.policy_name = data["policy"]
    c.insert_response(idmap, clone_map, **data)
    if data['question'].startswith("c"):
        log_type = "optional comment"
    else:
        log_type = "response"
    g.log = {"type": log_type,
             "context": {"question": data['question'],
                         "response": data.get('response', None)}}

    ### Regenerate BNF for this policy... maybe not the place to do it
    try:

        #remake the clone array
        remake_clones(clone_map, idmap)
        # print("id to bnf" + str(id_to_bnf))
        qaire = c.get_current_questionnaire_document(current_user, data["policy"])
        oldstmnts = qaire.get('bnf_statements', [])
        bnfs = bnf.get_bnf(qaire, questions, id_to_bnf, idmap)
        stmnts = bnf.generate_bnf_statements(bnfs, qaire['questions'], idmap)
        if oldstmnts != stmnts:
            qaire['bnf_statements'] = stmnts
            c.questionnaire.save(qaire)
            g.bnf_log = {"old": unicode(oldstmnts), "new": unicode(stmnts)}
    except Exception:
        log.error("Exception generating BNF", exc_info=True)

    return ""


@app.route("/api/clear_responses", methods=["POST"])
@login_required
def clear_responses():
    data = json.loads(request.get_data())
    log.info("clearing responses %s", pformat(data))
    try:
        for qid in data["qids"]:
            c.clear_responses(current_user, data["policy"], qid)
    except QuestionnaireNotFoundError:
        return "You don't have access to this policy", 400
    return ""


@app.route("/api/demosurvey", methods=["POST"])
@login_required
def demosurvey_response():
    data = json.loads(request.get_data())
    data["user"] = current_user.get_id()
    g.policy_name = data["policy"]
    c.insert_response(idmap, clone_map, **data)
    g.log = {"type": "demosurvey response",
             "context": {"question": data['question'],
                         "response": data.get('response', None)}}

    return ""


@app.route("/api/demosurvey_complete", methods=["POST"])
@login_required
def demosurvey_complete():
    demo_survey = c.get_current_questionnaire(current_user, "demosurvey")
    if demo_survey:
        c.update_user(current_user,
                      done_demographic_survey=True,
                      demographic_survey=demo_survey)
    else:
        c.update_user(current_user,
                      done_demographic_survey=True)

    return ""


@app.route("/api/general_comments_submit", methods=["POST"])
def general_comments_submit():
    # comment is logged on submit and emailed, this method is only
    # here as an artifact of using the same code as the questionnaire
    # to generate the comments page
    return ""


@app.route("/api/general_comments", methods=["POST"])
def general_comments_response():
    return ""


@app.route("/api/resolve_insert/<string:policy_name>", methods=["POST"])
def resolve_insert(policy_name):
    data = json.loads(request.get_data())
    responses = c.get_current_questionnaire(current_user, policy_name)
    s = bnf.resolve_insert(data, responses, idmap)
    if s == '':
        return questionnaire["default_insert_text"]
    return s


@app.after_request
def do_logging(response):
    if not g.get('log'):
        return response
    glog = g.get('log')
    user_id = glog.get('user_id')
    user_id = user_id if user_id else current_user.get_id()
    new_draft_state = None
    if "policy_name" in g:
        qdoc = c.get_current_questionnaire_document(current_user, g.policy_name)
        new_draft_state = qdoc.get('state')

    utype = glog.get('user_type')
    if not utype:
        if hasattr(current_user, "is_admin"):
            utype = "admin" if current_user.is_admin() else "participant"
        else:
            utype = "logged out"

    log_dict = {
        "xmlversion": questionnaire['xmlversion'],
        "qaversion": questionnaire['qaversion'],
        "bnf_version": questionnaire['BNFversion'],
        "app_version": __version__,
        "timestamp": time.time(),
        "policy_name": g.get("policy_name"),
        "state": new_draft_state,
        "user_agent_os": request.user_agent.platform,
        "user_agent_browser": request.user_agent.browser,
        "user_agent_version": request.user_agent.version,
        "user_agent_language": request.user_agent.language,
        "user_type": utype,
        "user_id": user_id,
        "url": request.url,
    }
    log_dict.update(g.get("log", {}))
    c.insert_log(log_dict)
    if "_id" in log_dict:
        del log_dict["_id"]  # remove mongo added id
    if g.get('bnf_log'):
        bnf_log = deepcopy(log_dict)
        bnf_log.update({"type": "bnf",
                        "context": g.bnf_log,
                        "timestamp": time.time()})

        c.insert_log(bnf_log)

    return response