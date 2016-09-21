# python "/Applications/google_appengine/dev_appserver.py" "/Users/Kale/Google Drive/Udacity/03.IntroToBackend/08.project"
# python "/Applications/google_appengine/appcfg.py" update "/Users/Kale/Google Drive/Udacity/03.IntroToBackend/08.project"

import os
import time
import datetime

import webapp2
import jinja2

import security as sec
import form_validation as val

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

#################
# User database #
#################

def users_key(group='default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()
    liked_posts = db.ListProperty(int)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = sec.make_pw_hash(name, pw)
        return User(parent=users_key(),
                    name=name,
                    pw_hash=pw_hash,
                    email=email)

    @classmethod
    def login(cls, name, pw):
        u = User.by_name(name)
        if u and sec.valid_pw(name, pw, u.pw_hash):
            return u

    def like_post(self, post):
        error = None
        if not post.authored_by(self):
            post_id = int(post.key().id())
            if post_id not in self.liked_posts:
                self.liked_posts.append(post_id)
                self.put()
                post.increment_likes()
            else:
                error = "You can only like a post once!"
        else:
            error = "You can only like other user's posts!"

        return error

    def unlike_post(self, post):
        error = None
        if not post.authored_by(self):
            post_id = post.key().id()
            if post_id in self.liked_posts:
                self.liked_posts.remove(post_id)
                self.put()
                post.decrement_likes()
                return None
            else:
                error = "You can only unlike posts you previously liked!"
        else:
            error = "You can't unlike your own posts!" 

        return error 

####################
# Comment Database #
####################

class Comment(db.Model):
    creator = db.StringProperty(required=True)
    post_id = db.StringProperty(required=True)
    content = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def authored_by(self, user):
        return self.creator == str(user.key().id())

    def edit(self, content):
        self.content = content
        self.put()

    def to_string(self):
        user = User.by_id(int(self.creator))
        return "{} submitted by {}".format(self.content, user.name)

    @classmethod
    def by_id(cls, cid):
        return Comment.get_by_id(cid)   

######################
# Blog Post Database #
######################

def blog_key(group='default'):
    return db.Key.from_path('blogs', group)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Post(db.Model):
    creator = db.StringProperty(required=True)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now_add=True)
    likes = db.IntegerProperty(default=0)

    @classmethod
    def by_id(cls, pid):
        return Post.get_by_id(pid, parent=blog_key())

    @classmethod
    def by_creator(cls, uid):
        posts = Post.all().filter('creator =', uid)
        return posts

    def render(self):
        self._render_text = self.render_text()
        return render_str("post.html", post=self)

    def render_text(self):
        return self.content.replace('\n', '<br>')

    def authored_by(self, user):
        return self.creator == str(user.key().id()) 

    def is_modified(self): 
        tdelta =  self.last_modified - self.created 
        return tdelta.total_seconds() > 1

    def increment_likes(self):
        self.likes = self.likes + 1
        self.put()

    def decrement_likes(self):
        self.likes = self.likes - 1
        self.put()

    def edit(self, subject, content):
        self.subject = subject
        self.content = content
        self.last_modified = datetime.datetime.now()
        self.put()

    def get_comments(self):
        q = Comment.all()
        return q.filter("post_id = ", str(self.key().id())).order('-created')
    
    def creator_name(self):
        user = User.by_id(int(self.creator))
        return user.name

################
# Main Handler #
################

class MainHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = sec.make_secure_val(val)
        self.response.headers.add_header('Set-Cookie','{}={}; Path=/'.format(name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and sec.check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and uid != '' and User.by_id(int(uid))

######################
# Blog Post Handlers #
######################

class BlogFront(MainHandler):
    def get(self):
        posts = Post.all().order('-created')
        self.render('front.html', posts=posts, user=self.user)

class PostPage(MainHandler):
    def get(self, post_id):
        post = Post.by_id(int(post_id))

        if not post:
            self.error(404)
            return

        self.render("permalink.html", 
            user=self.user,
            post=post)

class NewPost(MainHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if val.valid_subject(subject) and val.valid_content(content):
            p = Post(parent=blog_key(),
                creator=str(self.user.key().id()), 
                subject=subject, 
                content=content)
            p.put()
            self.redirect('/blog/{}'.format(str(p.key().id())))
        else:
            error = "Subject (3 to 37 chars) and Content (10 to 1000 chars) required."
            self.render("newpost.html", 
                subject=subject, 
                content=content, 
                error=error)

class DeletePost(MainHandler):

    def get(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        post = Post.by_id(int(post_id))
        if not self.post:
            self.error(404)
            return
        if post.authored_by(self.user):
            self.render("confirm-delete.html", 
                user=self.user,
                post=post, 
                entity="post")
        else:
            error = "You can only delete posts you created!"
            self.render("permalink.html", 
                user=self.user,
                post=post, 
                error=error)

    def post(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        confirmation = self.request.get('delete')
        post = Post.by_id(int(post_id))
        if confirmation == 'yes' and post:
            Post.delete(post)

            # delay for datastore consistency
            time.sleep(2)

            self.redirect("/blog")
        elif confirmation == 'no' and post:
            self.render("permalink.html", 
                user=self.user,
                post=post)
        else:
            self.redirect("/blog")
        

class EditPost(MainHandler):

    def get(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        post = Post.by_id(int(post_id))
        if not post:
            self.error(404)
            return
        if post.authored_by(self.user):
            self.render("editpost.html", 
                user=self.user,
                post=post)
        else:
            error = "You can only edit posts you created!"
            self.render("permalink.html", 
                user=self.user,
                post=post, 
                error=error) 

    def post(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        post = Post.by_id(int(post_id))
        confirmation = self.request.get('edit')
        if confirmation == 'cancel':
            self.render("permalink.html", 
                            user=self.user,
                            post=post)
            return

        subject = self.request.get('subject')
        content = self.request.get('content')

        if val.valid_subject(subject) and val.valid_content(content):
            post.edit(subject=subject, content=content)
            self.redirect('/blog/{}'.format(str(post.key().id())))
        else:
            error = "Please submit both Subject and Content"
            self.render("editpost.html", 
                user=self.user,
                post=post, 
                subject=subject, 
                content=content, 
                error=error)

class LikePost(MainHandler):

    def get(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        post = Post.by_id(int(post_id))
        if not post:
            self.error(404)
            return

        error = self.user.like_post(post)
        if error:
            self.render("permalink.html", 
                user=self.user,
                post=post, 
                error=error)
        else:
            msg = "You liked this post!"
            self.render("permalink.html", 
                user=self.user,
                post=post, 
                message=msg)

class UnlikePost(MainHandler):

    def get(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        post = Post.by_id(int(post_id))
        if not post:
            self.error(404)
            return

        error = None
        error = self.user.unlike_post(post)
        if error:
            self.render("permalink.html", 
                user=self.user,
                post=post, 
                error=error) 
            return
        else:
            msg = "You unliked this post!"
            self.render("permalink.html", 
                user=self.user,
                post=post, 
                message=msg)

####################
# Comment Handlers #
####################

class NewComment(MainHandler):

    def get(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        post = Post.by_id(int(post_id))
        if not post:
            self.error(404)
            return

        self.render("commentpost.html", user=self.user, post=post)     

    def post(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        post = Post.by_id(int(post_id))
        confirmation = self.request.get('edit')
        
        if confirmation == 'cancel':
            self.render("permalink.html", 
                            user=self.user,
                            post=post)
            return

        content = self.request.get('content')

        if val.valid_comment(content):
            comment = Comment(
            creator=str(self.user.key().id()), 
            post_id=str(post.key().id()),
            content=content
            )
            comment.put()
            time.sleep(2)            
            self.redirect('/blog/{}'.format(str(post.key().id())))

        else:
            error = "Please submit a comment no longer than 140 characters."
            self.render("commentpost.html", 
                user=self.user,
                post=post, 
                error=error)   

class DeleteComment(MainHandler):

    def get(self, comment_id):
        if not self.user:
            self.redirect('/login')
            return

        comment = Comment.by_id(int(comment_id))
        if not comment:
            self.error(404)
            return

        post = Post.by_id(int(comment.post_id))

        if comment.authored_by(self.user):
            self.render("confirm-delete.html",
                user=self.user, 
                post=post, 
                entity="comment")
        else:
            error = "You can only delete comments you created!"
            self.render("permalink.html",
                user=self.user, 
                post=post, 
                error=error)

    def post(self, comment_id):
        if not self.user:
            self.redirect('/login')
            return

        confirmation = self.request.get('delete')
        comment = Comment.by_id(int(comment_id))
        if confirmation == 'yes' and comment:
            Comment.delete(comment)

            # delay for datastore consistency
            time.sleep(2)

            self.redirect("/blog")
        elif confirmation == 'no' and comment:
            post = Post.by_id(int(comment.post_id))
            self.render("permalink.html",
                user=self.user, 
                post=post)
        else:
            self.redirect("/blog")
        

class EditComment(MainHandler):

    def get(self, comment_id):
        if not self.user:
            self.redirect('/login')
            return

        comment = Comment.by_id(int(comment_id))
        if not comment:
            self.error(404)
            return

        post = Post.by_id(int(comment.post_id))

        if comment.authored_by(self.user):
            self.render("commentpost.html", 
                user=self.user, 
                post=post, 
                content=comment.content
                )
        else:
            error = "You can only edit comments you created!"
            self.render("permalink.html", 
                user=self.user,
                post=post, 
                error=error) 

    def post(self, comment_id):
        if not self.user:
            self.redirect('/login')
            return

        comment = Comment.by_id(int(comment_id))
        post = Post.by_id(int(comment.post_id))
        confirmation = self.request.get('edit')

        if confirmation == 'cancel':
            self.render("permalink.html", 
                            user=self.user,
                            post=post)
            return

        content = self.request.get('content')

        if val.valid_content(content):
            comment.edit(content=content)
            time.sleep(2)
            msg = "Your comment was edited"
            self.render("permalink.html",
                user=self.user, 
                post=post, 
                message=msg) 
        else:
            error = "Cannot submit empty comment"
            self.render("commentpost.html",
                user=self.user, 
                post=post, 
                error=error)           


#########################
# Signup/Login Handlers #
#########################

class Signup(MainHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not val.valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not val.valid_password(self.password):
            params['error_password'] = "That's not a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not val.valid_email(self.email):
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
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/welcome')

class Login(MainHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
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

####################
# Blog Application #
####################

app = webapp2.WSGIApplication([('/blog', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/delete-post/([0-9]+)', DeletePost),
                               ('/blog/edit-post/([0-9]+)', EditPost),
                               ('/blog/like-post/([0-9]+)', LikePost),
                               ('/blog/unlike-post/([0-9]+)', UnlikePost),
                               ('/blog/comment-post/([0-9]+)', NewComment),
                               ('/blog/delete-comment/([0-9]+)', DeleteComment),
                               ('/blog/edit-comment/([0-9]+)', EditComment),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/welcome', Welcome),
                               ],
                              debug=True)

