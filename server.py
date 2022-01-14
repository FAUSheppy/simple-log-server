#!/usr/bin/python3

import flask
import requests
import argparse
import datetime
import json
import os
import random
import secrets

app = flask.Flask('Simple Log Server')

@app.route('/')
def main():

@app.route('/submitt', methods=["PUT"])
def submitt():

    d = flask.request.json

    service     = d["service"]
    host        = d["host"]
    contentType = d["contentType"]
    content     = d["content"]


@app.route('/static/<path:path>')
def static(path):
    return send_from_directory('static', path)

@app.before_first_request
def init():

    if os.path.isfile("config.py"):
        app.config.from_object("config")
    else:
        print("Config not found!", file=sys.stderr)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start Simple Log Server Debug Mode')
    parser.add_argument('--interface', default="localhost")
    parser.add_argument('--port', default="5002")
    args = parser.parse_args()

    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(host=args.interface, port=args.port)
