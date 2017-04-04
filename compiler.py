# Code to render content to be hosted on google app engine

import os
import webapp2
import jinja2
import datetime

import time # for delay

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

    todos_date = ndb.DateProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


def populate():
    """populate db with some days"""
    days = [[0,0,0,"2017-03-29"],
            [190,6,0,"2017-03-30"],
            [19,17,0,"2017-03-31"],
            [57,12,0,"2017-04-01"]]

    for day in days:
        day_instance = Todo_day( new = day[0], done = day[1], retired = day[2],
            todos_date = datetime.datetime.strptime(day[3], "%Y-%m-%d"))
        day_instance.put()

    time.sleep(.1)

def get_tot():
    entries = Todo_day.query().order(Todo_day.date).fetch()

    if not entries:
        # if DB empty create some entries
        populate()
        entries = Todo_day.query().order(Todo_day.date).fetch()

    total, new, done, retired = 0, 0, 0, 0

    for entry in entries:
        total += entry.new - entry.done - entry.retired
        entry.tot_on_day = total
        if entry.todos_date == datetime.date.today():
            new += entry.new
            done += entry.done
            retired += entry.retired

    template_values = {
        "today" : str(datetime.date.today()),
        "total" : total,
        "new" : new,
        "done" : done,
        "retired" : retired,
        "entries" : entries
    }

    return template_values

def get_template_values(template):

    get_values_function_mapper = {
        "todocounter" : get_tot,
        "chart": get_tot,
    }

    if template in get_values_function_mapper:
        return get_values_function_mapper[template]()

    return {}


class Page(webapp2.RequestHandler):

    def get(self, reg_input="index"):


        template_values = get_template_values(reg_input)
        html_template = reg_input + ".html"

        template = JINJA_ENVIRONMENT.get_template(html_template)
        self.response.write(template.render(template_values))


    def post(self, reg_input="index"):

        todo_new = int(self.request.get('new'))
        todo_done = int(self.request.get('done'))
        todo_retired = int(self.request.get('retired'))
        todo_date = datetime.datetime.strptime(
                        self.request.get('date'), "%Y-%m-%d"
                    )

        todo_day = Todo_day(
            new = todo_new,
            done = todo_done,
            retired = todo_retired,
            todos_date = todo_date
        )

        todo_day.put()
        time.sleep(.1)

        self.redirect('/' + reg_input)


app = webapp2.WSGIApplication([(r'/', Page), ('/(\w+)', Page)], debug = True)
