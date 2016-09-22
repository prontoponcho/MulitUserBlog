from google.appengine.ext import db

from lib import security as sec

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