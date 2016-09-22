import time

from base import MainHandler
from models import post as p
from models import comment as c
from lib import form_validation as v

class BlogFront(MainHandler):
    def get(self):
        posts = p.Post.all().order('-created')
        self.render('front.html', posts=posts, user=self.user)

class PostPage(MainHandler):
    def get(self, post_id):
        post = p.Post.by_id(int(post_id))

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

        if v.valid_subject(subject) and v.valid_content(content):
            post = p.Post(parent=p.blog_key(),
                creator=str(self.user.key().id()), 
                subject=subject, 
                content=content)
            post.put()
            self.redirect('/blog/{}'.format(str(post.key().id())))
        else:
            error = "Subject (3 to 30 chars) and Content (10 to 1000 chars) required."
            self.render("newpost.html", 
                subject=subject, 
                content=content, 
                error=error)

class DeletePost(MainHandler):

    def get(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        post = p.Post.by_id(int(post_id))
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

        post = p.Post.by_id(int(post_id))
        if not self.post:
            self.error(404)
            return

        if not post.authored_by(self.user):
            error = "You can only delete posts you created!"
            self.render("permalink.html", 
                user=self.user,
                post=post, 
                error=error)
            return

        confirmation = self.request.get('delete')
        if confirmation == 'yes':
            comments = post.get_comments()
            for comment in comments:
                c.Comment.delete(comment)

            p.Post.delete(post)

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

        post = p.Post.by_id(int(post_id))
        if not post:
            self.error(404)
            return

        if post.authored_by(self.user):
            self.render("editpost.html", 
                user=self.user,
                post=post)
            return
            
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

        post = p.Post.by_id(int(post_id))
        if not self.post:
            self.error(404)
            return

        if not post.authored_by(self.user):
            error = "You can only edit posts you created!"
            self.render("permalink.html", 
                user=self.user,
                post=post, 
                error=error)
            return

        confirmation = self.request.get('edit')
        if confirmation == 'cancel':
            self.render("permalink.html", 
                user=self.user, 
                post=post)
            return

        subject = self.request.get('subject')
        content = self.request.get('content')

        if v.valid_subject(subject) and v.valid_content(content):
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

        post = p.Post.by_id(int(post_id))
        if not post:
            self.error(404)
            return

        error = self.user.like_post(post)
        if error:
            self.render("permalink.html", 
                user=self.user,
                post=post, 
                error=error)
            return
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

        post = p.Post.by_id(int(post_id))
        if not post:
            self.error(404)
            return

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