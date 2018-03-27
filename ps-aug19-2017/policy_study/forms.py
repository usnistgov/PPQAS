from flask_wtf import Form
from wtforms import (TextField, RadioField, SelectField, SelectMultipleField,
                     IntegerField, PasswordField, TextAreaField)
from wtforms.validators import Required, EqualTo, NumberRange, Email, Optional

class LoginForm(Form):
    loginid = TextField('login',
                       validators=[])
    signupid = TextField('signup',
                       validators=[])
class SignupForm(Form):
    userid = TextField('userid',
                       validators=[])

class AdminPasswordForm(Form):
    password = PasswordField('Password',
                         validators=[Required(message="Password Required")])

class AdminAccountDeletionForm(Form):
        accounts = SelectMultipleField('accounts')

class AdminAccountCreationForm(Form):
    username = TextField('Username',
                         validators=[Required()])
    password = PasswordField('Password',
                         validators=[Required(),
                                     EqualTo('reenter',
                                             message='Passwords must match')])
    reenter = PasswordField('Re-Enter',
                        validators=[Required()])

class AdminAccountChangePasswordForm(Form):
    user = TextField('Username', validators=[Required()])
    newpassword = PasswordField('New Password',
                            validators=[Required(),
                                        EqualTo('again',
                                                message='Passwords must match')])

    again = PasswordField('Re-Enter', validators=[Required()])

class PoliciesPerUserForm(Form):
    policies_per_user = IntegerField("Policies per user", [ NumberRange(min=1) ])

class CommentsEmailsForm(Form):
    comments_emails = SelectMultipleField("Comments/Help Email Addresses")

class CommentsAddEmailForm(Form):
    add_address = TextField('add_address', validators=[Email(message="Must be valid email address")],)

    # class DemographicForm(Form):
#     gender = RadioField('Gender',
#                          choices=[('male', 'Male'),
#                                   ('female', 'Female'),
#                                   ('no answer', 'Prefer not to answer'),
#                                   ('other', 'Other'),
#                               ],
#                         validators=[Optional()])

#     age = RadioField('Age',
#                      choices=[('<20', 'Less than 20'),
#                               ('20-29', '20-29'),
#                               ('30-39', '30-39'),
#                               ('40-49', '40-49'),
#                               ('50-59', '50-59'),
#                               ('60-69', '60-69'),
#                               ('70+', '70+')],
#                      validators=[Optional()])

#     education = RadioField('Highest Education',
#                             choices=[('high school', 'High School'),
#                                      ('some college', 'Some College'),
#                                      ('undergraduate degree',
#                                       'Undergraduate Degree'),
#                                      ("master's degrees or equivalent",
#                                       "Master's Degrees or Equivalent"),
#                                      ('phd, md', 'PhD, MD'),],
#                            validators=[Optional()])

#     job_title = TextField('Job Title',
#                           validators=[Optional()])

#     department = RadioField('Department',
#                             choices=[('information technology lab',
#                                       'Information Technology Lab'),
#                                      ('other', 'Other')],
#                             validators=[Optional()])

#     supervisory_status = RadioField('Supervisory Status',
#                                     choices=[
#                                         ('non-supervisor', 'Non-supervisor'),
#                                         ('team leader', 'Team Leader'),
#                                         ('supervisor', 'Supervisor'),
#                                         ('manager', 'Manager'),
#                                         ('executive', 'Executive')],
#                                     validators=[Optional()])

#     years_service = RadioField('Years of Service',
#                                choices=[
#                                    ('less than 1 year', 'Less than 1 year'),
#                                    ('1 to 3 years', '1 to 3 years'),
#                                    ('4 to 5 years', '4 to 5 years'),
#                                    ('6 to 10 years', '6 to 10 years'),
#                                    ('11 to 14 years', '11 to 14 years'),
#                                    ('15 to 20 years', '15 to 20 years'),
#                                    ('more than 20 years',
#                                     'More than 20 years'),],
#                                validators=[Optional()])

class AdminTestingForm(Form):
    all_policies = SelectMultipleField("All Policies")
    selected_policies = SelectMultipleField("Selected Policies")

class CommentsForm(Form):
    nature = RadioField('What is the nature of your comment?',
                        choices=[
                            ('question', 'Question'),
                            ('feedback', 'Feedback'),
                            ('technical_problem', 'Technical Problem'),
                        ])
    describe = TextAreaField('Please Describe')
