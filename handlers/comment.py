import time

from base import MainHandler
from models import post as p
from models import comment as c
from models import user as u
from lib import form_validation as v

class NewComment(MainHandler):

    def get(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        post = p.Post.by_id(int(post_id))
        if not post:
            self.error(404)
            return

        self.render("commentpost.html", user=self.user, post=post)     

    def post(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        post = p.Post.by_id(int(post_id))
        confirmation = self.request.get('edit')
        
        if confirmation == 'cancel':
            self.render("permalink.html", 
                user=self.user, 
                post=post)
            return

        content = self.request.get('content')

        if v.valid_comment(content):
            comment = c.Comment(
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

        comment = c.Comment.by_id(int(comment_id))
        if not comment:
            self.error(404)
            return

        post = p.Post.by_id(int(comment.post_id))

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

        comment = c.Comment.by_id(int(comment_id))
        if not comment:
            self.error(404)
            return

        post = p.Post.by_id(int(comment.post_id))
        if not comment.authored_by(self.user):
            error = "You can only delete comments you created!"
            self.render("permalink.html",
                user=self.user, 
                post=post, 
                error=error)
            return

        confirmation = self.request.get('delete') 
        if confirmation == 'yes':
            c.Comment.delete(comment)

            # delay for datastore consistency
            time.sleep(2)

            self.redirect("/blog")
        elif confirmation == 'no' and comment:
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

        comment = c.Comment.by_id(int(comment_id))
        if not comment:
            self.error(404)
            return

        post = p.Post.by_id(int(comment.post_id))

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

        comment = c.Comment.by_id(int(comment_id))
        if not comment:
            self.error(404)
            return

        post = p.Post.by_id(int(comment.post_id))
        if not comment.authored_by(self.user):
            error = "You can only edit comments you created!"
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

        content = self.request.get('content')
        if v.valid_content(content):
            comment.edit(content=content)
            # wait for datastore consistency
            time.sleep(2)
            msg = "Your comment was edited"
            self.render("permalink.html",
                user=self.user, 
                post=post, 
                message=msg) 
            return
        else:
            error = "Cannot submit empty comment"
            self.render("commentpost.html",
                user=self.user, 
                post=post, 
                error=error)           

