# Code to render content to be hosted on google app engine

import os
import webapp2
import jinja2
import time
import datetime

from google.appengine.ext import ndb


template_dir = os.path.join(os.path.dirname(__file__), "templates")
JINJA_ENVIRONMENT  = jinja2.Environment(
                loader = jinja2.FileSystemLoader(template_dir),
                autoescape = True)

class Todo_day(ndb.Model):
    """date with contents"""
    new = ndb.IntegerProperty()
    done = ndb.IntegerProperty()
    retired = ndb.IntegerProperty()
    tot_day = ndb.IntegerProperty()

    todos_date = ndb.DateProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


class Page(webapp2.RequestHandler):

    def get(self, reg_input=""):
        page_dictionary = {"": "index.html"}
        html_template = page_dictionary[reg_input]

        entries = Todo_day.query().order(-Todo_day.date).fetch()

        total, new, done, retired = 0, 0, 0, 0

        for entry in entries:
            total += entry.tot_day
            if entry.todos_date == datetime.date.today():
                new = entry.new
                done = entry.done
                retired = entry.retired

        template_values = {
            "today" : time.strftime("%Y-%m-%d"),
            "total" : total,
            "new" : new,
            "done" : done,
            "retired" : retired
        }

        template = JINJA_ENVIRONMENT.get_template(html_template)
        self.response.write(template.render(template_values))


    def post(self):

        todo_new = int(self.request.get('new'))
        todo_done = int(self.request.get('done'))
        todo_retired = int(self.request.get('retired'))
        tot_day = todo_new - todo_done - todo_retired
        todo_date = datetime.datetime.strptime(
                        self.request.get('date'), "%Y-%m-%d"
                    )

        todo_day = Todo_day(
            new = todo_new,
            done = todo_done,
            retired = todo_retired,
            tot_day = tot_day,
            todos_date = todo_date
        )

        todo_day.put()
        time.sleep(.1)

        self.redirect('/')


app = webapp2.WSGIApplication([(r'/', Page)], debug = True)
