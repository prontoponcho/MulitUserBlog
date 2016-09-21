import re

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

CONTENT_RE = re.compile(r"^[\W\sa-zA-Z0-9_-]{10,1000}$")
def valid_content(content):
	return content and CONTENT_RE.match(content)

SUBJECT_RE = re.compile(r"^[a-zA-Z0-9_-]{3,30}$")
def valid_subject(subject):
	return subject and SUBJECT_RE.match(subject)

def valid_comment(content):
	l = len(content)
	return l >= 2 and l <= 140