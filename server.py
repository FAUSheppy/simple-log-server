#!/usr/bin/python3

import flask
import requests
import argparse
import datetime
import json
import os
import sys
import random
import secrets
import hashlib

from sqlalchemy import Column, Integer, String, Boolean, or_, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy

import datatable

app = flask.Flask('Simple Log Server')
db = SQLAlchemy(app)

class SearchHelper(db.Model):
    __tablename__ = "search_helper"
    uid = Column(String, primary_key=True)
    fullstring = Column(String)

class LogLine(db.Model):
    __tablename__ = "log_line"
    uid         = Column(String, primary_key=True)
    timestamp   = Column(String)
    service     = Column(String)
    host        = Column(String)
    contentType = Column(String)
    content     = Column(String)
    severity    = Column(Integer)

@app.route('/', methods=["GET", "POST"])
def main():
    if flask.request.method == "POST":
        dt = datatable.DataTable(flask.request.form.to_dict(), db,
                                    LogLine, SearchHelper, truncateUid=True)
        return flask.Response(json.dumps(dt.get()), 200, mimetype='application/json')
    else:
        return flask.render_template("index.html", 
                        headerRow=datatable.DataTable.staticGetCols(LogLine))


@app.route('/submit', methods=["PUT"])
def submitt():

    d = flask.request.json

    service     = d.get("service")
    host        = d.get("host")
    contentType = d.get("contentType")
    content     = d.get("content")
    severity    = d.get("severity")

    # service #
    if not service:
        return ("Missing Service filed", 405)
    elif not content:
        return ("Missing Content or Content Empty", 405)

    # parse content type #
    if not contentType:
        contentType = "simple"

    # parse severity #
    if not severity:
        severity = -1
    try:
        severity = int(severity)
    except ValueError:
        severity = severityStringToInt(severity)

    # parse host #
    if not host:
        host = "undefined"

    timestamp = datetime.datetime.now().timestamp()
    uid = hashlib.sha512((str(timestamp) + str(service) + str(host)).encode("UTF-8")).hexdigest()
    ll = LogLine(uid=uid, timestamp=timestamp, service=service, host=host,
                    contentType=contentType, content=content, severity=severity)

    fullstring = "{uid} {timestamp} {service} {host} {contentType} {content} {severity}".format(
                        uid=uid, timestamp=timestamp, service=service, host=host, 
                        contentType=contentType, content=content, severity=severity)

    sh = SearchHelper(uid=uid, fullstring=fullstring)
    
    db.session.add(ll)
    db.session.add(sh)

    db.session.commit()

    return ("", 204)


@app.route('/static/<path:path>')
def staticDir(path):
    return send_from_directory('static', path)

@app.before_first_request
def init():

    if os.path.isfile("config.py"):
        app.config.from_object("config")
    else:
        print("Config not found!", file=sys.stderr)

    app.config["DB"] = db
    db.create_all()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start Simple Log Server Debug Mode')
    parser.add_argument('--interface', default="localhost")
    parser.add_argument('--port', default="5002")
    args = parser.parse_args()

    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(host=args.interface, port=args.port)
