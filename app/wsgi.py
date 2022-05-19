#!/usr/bin/python3

from flask import Flask

# from __init__ import setup_metrics
from qcs import app, init
import os
import sys
import logging

# from elasticapm.contrib.flask import ElasticAPM

sys.path.insert(0, os.path.dirname(__file__))
# if "prometheus_multiproc_dir" not in os.environ:
#     os.environ["prometheus_multiproc_dir"] = "/tmp"

class WsgiApp:
    """Wrapper class for flask app"""
    def __init__(self, app):
        self.app = app
        print('loading statistical data')
        init()
        # ElasticAPM(self.app, logging=logging.INFO)
        # attach statsd (dd)
        # try:
        #     setup_metrics()
        # except Exception as ex:
        #     logging.error("Unable to initialize metrics: {}".format(ex))

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)

wsgi = WsgiApp(app)