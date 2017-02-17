import os
import webapp2
import jinja2
import cgi

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def get_posts(limit, offset):
    posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT {} OFFSET {}".format(limit, offset))
    return posts

class Index(webapp2.RequestHandler):
    def get(self):
        t = jinja_env.get_template("base.html")
        content = t.render()
        self.response.write(content)

class Blog(db.Model):
    # creates the Blog database with title, body, and created fields
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class BlogHandler(webapp2.RequestHandler):
    # handles requests coming in to /blog
    def get(self):
        # page = self.request.get("page")

        blogs = get_posts(5, 0)

        t = jinja_env.get_template("blog.html")
        content = t.render(blogs=blogs)
        self.response.write(content)

class PostHandler(webapp2.RequestHandler):
    # handles requests coming in to /newpost
    def get(self):
        t = jinja_env.get_template("newpost.html")
        content = t.render()
        self.response.write(content)

    # writes the title, body, and created date/time to blog DB,
    # redirects to detail of blog entry
    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if not title or not body:
            error = "Please include both a title and body text for your blog entry."
            t = jinja_env.get_template("newpost.html")
            content = t.render(title=title, body=body, error=error)
            self.response.write(content)
        else:
            b = Blog(title = title, body = body)
            b.put()

            t = jinja_env.get_template("blog_detail.html")
            content = t.render(blog = b)
            self.response.write(content)

class BlogDetail(webapp2.RequestHandler):
    # handles requests for individual blog entries
    def get(self, blog_id):
        blog = Blog.get_by_id(int(blog_id))
        if not blog:
            self.renderError(404)
        t = jinja_env.get_template("blog_detail.html")
        content = t.render(blog = blog)
        self.response.write(content)


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/blog', BlogHandler),
    ('/newpost', PostHandler),
    webapp2.Route('/blog/<blog_id:\d+>', BlogDetail),
], debug=True)
