from flask import Flask, request, jsonify
import peewee
import os
from playhouse.flask_utils import FlaskDB
from random import randint


# Database definitions.
db_url = os.environ.get("db_url")
# "postgresql://restapi:" + os.envrion.get("db_passwd") + "@localhost:5432/" + os.environ.get("database")
app = Flask(__name__)
db_wrapper = FlaskDB(app, db_url)
peewee_db = db_wrapper.database


class RestClient(db_wrapper.Model):
    uuid = peewee.UUIDField()
    authkey = peewee.CharField()


class Reading(db_wrapper.Model):
    sensor = peewee.FixedCharField(max_length=15)
    timestamp = peewee.DateTimeField()
    temperature = peewee.FloatField()


# Route definitions.
@app.route("/days/<string:day>",
           defaults={"day": None},
           methods=["GET"])
def days(day):
    """Return a list of days with readings, or all readings for <day>."""
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
    """Allow a client to request/recieve an authentication key."""
    if request.method == "POST":
        with peewee_db.atomic():
            query = RestClient.select().where(RestClient.uuid == uuid)
            if len(query) > 0:
                return jsonify("UUID already exits."), 409
            else:
                authk = "testauthkey" + randint(1, 155)  # TODO: Replace with os.secret.
                x = RestClient(uuid=uuid, authkey=authk)
                x.save()
                return jsonify({"msg": "RestClient saved.",
                                "url": "/authentication/" + uuid}), 201
    elif request.method == "GET":
        with peewee_db.atomic():
            query = RestClient.select().where(RestClient.uuid == uuid)
            if len(query) > 0:
                return jsonify({"authkey": query[0].authkey})
            else:
                return jsonify({"msg": "UUID not prior registration."}), 404
