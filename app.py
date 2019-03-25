import os
import secrets
import peewee
from flask import Flask, json, request
from playhouse.flask_utils import FlaskDB


# Database definitions.
db_url = os.environ.get("db_url")
# "postgresql://restapi:" + os.envrion.get("db_passwd") +
# "@localhost:5432/" + os.environ.get("database")
app = Flask(__name__)
db_wrapper = FlaskDB(app, db_url)
peewee_db = db_wrapper.database


class RestClient(db_wrapper.Model):
    # uuid = peewee.UUIDField()
    uuid = peewee.CharField()
    authkey = peewee.CharField()


class Reading(db_wrapper.Model):
    timestamp = peewee.DateTimeField()
    sensor = peewee.FixedCharField(max_length=15)
    temperature = peewee.FloatField()


# Route definitions.
# TODO: Need to make this so we can post with just /readings
@app.route("/readings", methods=["GET", "POST"])
@app.route("/readings/<string:reading>",
           defaults={"reading": None},
           methods=["GET", "POST"])
def readings(reading):
    """POST: Save reading to database.
    GET: Return a list of latest 100 readings, or details of <reading>."""
    if request.method == "POST":
        js_data = request.get_json()
        x = Reading(sensor=js_data["sensor"],
                    timestamp=js_data["timestamp"],
                    temperature=float(js_data["temperature"]))
        ind = x.save()
        return json.jsonify({"msg": "Reading saved.",
                             "url": "/reading/" + str(ind)}), 201
    elif request.method == "GET":
        if reading:
            query = Reading.select().where(Reading.id == reading)
            if len(query) > 0:
                return json.jsonify({"timestamp": query[0].timestamp,
                                     "sensor": query[0].sensor,
                                     "temperature": query[0].temperature})
            else:
                return json.jsonify({"msg": "Reading does not exist."}), 404
        else:
            query = Reading.select(Reading.id).order_by(Reading.id.desc()).limit(100)
            d = [(reading.id, reading.timestamp) for reading in query]
            return json.jsonify(d)


@app.route("/authentication/<string:uuid>",
           methods=["GET", "POST"])
def authentication(uuid):
    """Allow a client to request/recieve an authentication key."""
    if request.method == "POST":
        with peewee_db.atomic():
            query = RestClient.select().where(RestClient.uuid == uuid)
            if len(query) > 0:
                return json.jsonify({"msg": "UUID already exits."}), 409
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
