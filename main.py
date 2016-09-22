# python "/Applications/google_appengine/dev_appserver.py" "/Users/Kale/Google Drive/Udacity/03.IntroToBackend/08.project"
# python "/Applications/google_appengine/appcfg.py" update "/Users/Kale/Google Drive/Udacity/03.IntroToBackend/08.project"

import webapp2

from handlers import blogpost as bp
from handlers import comment as cm
from handlers import account as ac

app = webapp2.WSGIApplication([('/blog', bp.BlogFront),
                               ('/blog/([0-9]+)', bp.PostPage),
                               ('/blog/newpost', bp.NewPost),
                               ('/blog/delete-post/([0-9]+)', bp.DeletePost),
                               ('/blog/edit-post/([0-9]+)', bp.EditPost),
                               ('/blog/like-post/([0-9]+)', bp.LikePost),
                               ('/blog/unlike-post/([0-9]+)', bp.UnlikePost),
                               ('/blog/comment-post/([0-9]+)', cm.NewComment),
                               ('/blog/delete-comment/([0-9]+)', cm.DeleteComment),
                               ('/blog/edit-comment/([0-9]+)', cm.EditComment),
                               ('/signup', ac.Register),
                               ('/login', ac.Login),
                               ('/logout', ac.Logout),
                               ('/welcome', ac.Welcome),
                               ],
                              debug=True)


