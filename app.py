import os
import secrets
import peewee
from flask import Flask, json, request
from playhouse.flask_utils import FlaskDB


# Database definitions.
db_url = os.environ.get("db_url")
# "postgresql://restapi:" + os.envrion.get("db_passwd") + "@localhost:5432/" + os.environ.get("database")
app = Flask(__name__)
db_wrapper = FlaskDB(app, db_url)
peewee_db = db_wrapper.database


class RestClient(db_wrapper.Model):
    # uuid = peewee.UUIDField()
    uuid = peewee.CharField()
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

# TODO: Need to make this so we can post with just /readings
@app.route("/readings", methods=["GET", "POST"])
@app.route("/readings/<string:reading>",
           defaults={"reading": None},
           methods=["GET", "POST"])
def readings(reading):
    """POST: Save reading to database.
    GET: Return a list of readings, or details of <reading>."""
    if request.method == "POST":
        js_data = request.get_json()
        return json.jsonify(js_data)
    elif request.method == "GET":
        if reading:
            return "reading " + reading
        else:
            return "List of readings."


@app.route("/authentication/<string:uuid>",
           methods=["GET", "POST"])
def authentication(uuid):
    """Allow a client to request/recieve an authentication key."""
    if request.method == "POST":
        with peewee_db.atomic():
            query = RestClient.select().where(RestClient.uuid == uuid)
            if len(query) > 0:
                return json.jsonify("UUID already exits."), 409
            else:
                authk = secrets.token_urlsafe()
                x = RestClient(uuid=uuid, authkey=authk)
                x.save()
                return json.jsonify({"msg": "RestClient saved.",
                                     "url": "/authentication/" + uuid}), 201
    elif request.method == "GET":
        with peewee_db.atomic():
            query = RestClient.select().where(RestClient.uuid == uuid)
            if len(query) > 0:
                return json.jsonify({"authkey": query[0].authkey})
            else:
                return json.jsonify({"msg": "UUID not registered."}), 404
