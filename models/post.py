
import datetime

from google.appengine.ext import db

from models import comment as c
from models import user as u

from fixpath import jinja_env

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
        q = c.Comment.all()
        return q.filter("post_id = ", str(self.key().id())).order('-created')
    
    def creator_name(self):
        user = u.User.by_id(int(self.creator))
        return user.name