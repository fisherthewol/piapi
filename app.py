from flask import Flask, request
import peewee
import os
from playhouse.flask_utils import FlaskDB


# Database definitions.
db_url = ("postgresql://restapi:"
          + os.envrion.get("db_passwd")
          + "@localhost:5432/"
          + os.environ.get("database"))
app = Flask(__name__)
db_wrapper = FlaskDB(app, db_url)
peewee_db = db_wrapper.database


class RestClient(db_wrapper.Model):
    uuid = peewee.UUIDField()
    authkey = peewee.CharField()


class Sensor(db_wrapper.Model):
    client = peewee.ForeignKeyField(RestClient, backref="sensors")
    name = peewee.FixedCharField(max_length=15)


class Reading(db_wrapper.Model):
    sensor = peewee.ForeignKeyField(Sensor, backref="readings")
    timestamp = peewee.DateTimeField()
    temperature = peewee.FloatField()


# Route definitions.
@app.route("/days/<string:day>",
           defaults={"day": None},
           methods=["GET"])
def days(day):
    """Return a list of days with records, or all records for <day>."""
    if day:
        return day
    else:
        return "List of days."


@app.route("/records/<string:record>",
           defaults={"record": None},
           methods=["GET", "POST"])
def records(record):
    """POST: Save record to database.
    GET: Return a list of records, or details of <record>."""
    if request.method == "POST":
        # Parse String into JSON.
        return "Record saved."
    elif request.method == "GET":
        if record:
            return "Record " + record
        else:
            return "List of records."


@app.route("/authentication/<string:uuid>",
           defaults={"uuid": None},
           methods=["GET", "POST"])
def authentication(uuid):
    """Allow a client to recieve an authentication key."""
    if request.method == "POST":
        return "UUID" + uuid + "Recorded"
    elif request.method == "GET":
        return uuid
