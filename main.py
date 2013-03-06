#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re
import india
from string import letters
import json
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = False)
class Cache(db.Model):
    trip=db.StringProperty(required=True)
    date=db.StringProperty(required=True)
    info=db.TextProperty(required=True)

class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self,template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(BaseHandler):
    def get(self):
        self.response.out.write('Welcome to the indian trains RESTful API.')
class Trains(BaseHandler):
    def get(self):
        cached="true"
        query=self.request.get("query")
        if query=="planner":
            origin=self.request.get("origin")
            destination=self.request.get("destination")
            date=self.request.get("date")
            try:
                result=json.loads(db.GqlQuery("SELECT * FROM Cache WHERE trip=:tr and date=:da ORDER BY date desc",tr=origin+"-"+destination,da=date)[0].info)
            except IndexError:
                cached="false"
                result=india.india(origin,destination,date)
        if result=="deperror":
            self.write("Your departing station is not correct")
        elif result=="arrerror":
            self.write("Your arriving station is not correct")
        elif result=="direrror":
            self.write("Interchanges are not supported yet")
        else:
            self.response.headers['Content-Type']='text/xml'
            self.render("planner.xml",result=result,o=origin,d=destination,cached=cached)
            info=json.dumps(result)
            a=Cache(trip=origin+"-"+destination,date=date,info=info)
            a.put()
app = webapp2.WSGIApplication([('/', MainHandler),('/trains', Trains)],
                              debug=True)
