# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

import atexit

from datetime import date
import tornado.escape
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from apscheduler.schedulers.tornado import TornadoScheduler


# https://stackoverflow.com/questions/21214270/scheduling-a-function-to-run-every-hour-on-flask
# garbage collection scheduler
def garbage_collect():
    print('le gc')

class VersionHandler(RequestHandler):
    def get(self):
        response = { 'version': '3.5.1',
                     'last_build':  date.today().isoformat() }
        self.write(response)

class GetGameByIdHandler(RequestHandler):
    def get(self, id):
        response = { 'id': int(id),
                     'name': 'Crazy Game',
                     'release_date': date.today().isoformat() }
        self.write(response)

app = Application([
    (r"/getgamebyid/([0-9]+)", GetGameByIdHandler),
    (r"/version", VersionHandler)
])

if __name__ == "__main__":
    gc_scheduler = TornadoScheduler()
    gc_scheduler.add_job(garbage_collect, 'interval', seconds=3)
    gc_scheduler.start()

    app.listen(10100)
    try:
        IOLoop.instance().start()
    except (KeyboardInterrupt, SystemExit):
        pass