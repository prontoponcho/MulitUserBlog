# MultiUserBlog
###Blog application with account signup, user authentication, posting, commenting, and likes. 
####Contents:
<ul>
  <li>handlers/ divides the meat of the application into four scripts: base, account, blogpost, and comment.
  <li>lib/ contains scripts for form validation, password hashing, and cookie authentication
  <li>models/ contains scripts for google datastore entities User, Post, and Comment
  <li>static/ contains the application's static resources like javascript and css
  <li>templates/ contains the html and forms that inherit from base.html using jinja2 templating
  <li>the remaining files are google appengine boilerplate
</ul>
####To deploy the local developer version, install google appengine and from the command line enter:
```
> python "/PATH/TO/google_appengine/dev_appserver.py "/PATH/TO/MultiUserBlog"
```
Then open a browser and go to http://localhost:8080/blog

####To visit the live application, go to: http://blog-144100.appspot.com/blog
