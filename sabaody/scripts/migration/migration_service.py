# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

from sabaody.migration_central import create_central_migration_service

import tornado.escape
from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.escape import json_decode
from apscheduler.schedulers.tornado import TornadoScheduler

import atexit
from datetime import date

# https://stackoverflow.com/questions/21214270/scheduling-a-function-to-run-every-hour-on-flask
# garbage collection scheduler
def garbage_collect():
    print('le gc')

if __name__ == "__main__":
    gc_scheduler = TornadoScheduler()
    gc_scheduler.add_job(garbage_collect, 'interval', seconds=3)
    gc_scheduler.start()

    create_central_migration_service().listen(10100)
    try:
        IOLoop.instance().start()
    except (KeyboardInterrupt, SystemExit):
        pass