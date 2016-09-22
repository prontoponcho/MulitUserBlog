from google.appengine.ext import db

from models import user as u

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
        user = u.User.by_id(int(self.creator))
        return "{} submitted by {}".format(self.content, user.name)

    @classmethod
    def by_id(cls, cid):
        return Comment.get_by_id(cid)  