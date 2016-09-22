from base import MainHandler
from lib import form_validation as v
from models import user as u

class Signup(MainHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username,
                      email=self.email)

        if not v.valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not v.valid_password(self.password):
            params['error_password'] = "That's not a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not v.valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        usr = u.User.by_name(self.username)
        if usr:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            usr = u.User.register(self.username, self.password, self.email)
            usr.put()

            self.login(usr)
            self.redirect('/welcome')

class Login(MainHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        usr = u.User.login(username, password)
        if usr:
            self.login(usr)
            self.redirect('/welcome')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(MainHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')

class Welcome(MainHandler):
    def get(self):
        if self.user:
            self.render('welcome.html', username=self.user.name)
        else:
            self.redirect('/signup')