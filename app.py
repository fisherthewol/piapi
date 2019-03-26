import os
import secrets
import peewee
from flask import Flask, json, request, render_template
from playhouse.flask_utils import FlaskDB


# Database definitions.
db_url = os.environ.get("db_url")
app = Flask(__name__)
db_wrapper = FlaskDB(app, db_url)
peewee_db = db_wrapper.database


class RestClient(db_wrapper.Model):
    uuid = peewee.UUIDField()
    authkey = peewee.CharField()


class Sensor(db_wrapper.Model):
    serial = peewee.FixedCharField(max_length=15)
    name = peewee.CharField()


class Reading(db_wrapper.Model):
    timestamp = peewee.DateTimeField()
    sensor = peewee.ForeignKeyField(Sensor, backref="readings")
    # sensor = peewee.FixedCharField(max_length=15)
    temperature = peewee.FloatField()


# Route definitions.
@app.route("/readings", methods=["GET", "POST"])
@app.route("/readings/<string:reading>",
           methods=["GET"])
def readings(reading=None):
    """POST: Save reading to database.
    GET: Return a list of latest 100 readings, or details of <reading>."""
    if request.method == "POST":
        js_data = request.get_json()
        with peewee_db.atomic():
            sensor = Sensor.get_or_none(Sensor.name == js_data["sensor"])
            if sensor:
                x = Reading(sensor=sensor,
                            timestamp=js_data["timestamp"],
                            temperature=float(js_data["temperature"]))
            x.save()
        return json.jsonify({"msg": "Reading saved.",
                             "url": "/readings/" + str(x.id)}), 201
    elif request.method == "GET":
        if reading:
            with peewee_db.atomic():
                query = Reading.get_or_none(Reading.id == int(reading))
            if query:
                return json.jsonify({"timestamp": query.timestamp,
                                     "sensor": query.sensor,
                                     "temperature": query.temperature})
            else:
                return json.jsonify({"msg": "Reading does not exist."}), 404
        else:
            with peewee_db.atomic():
                d = [reading.id for reading in Reading.select(Reading.id).order_by(Reading.id.desc()).limit(100)]
            return json.jsonify(d)


@app.route("/sensors", methods=["GET", "POST"])
@app.route("/sensors/<string:sensor>",
           methods=["GET"])
def sensors(sensor=None):
    """POST: Add a sensor. GET: Retrieve a sensor or list of sensors."""
    if request.method == "POST":
        js_data = request.get_json()
        with peewee_db.atomic():
            x = Sensor(serial=js_data["serial"],
                       name=js_data["name"])
            x.save()
        return json.jsonify({"msg": "Sensor saved.",
                             "url": "/sensors/" + str(x.id)}), 201
    elif request.method == "GET":
        if sensor:
            with peewee_db.atomic():
                query = Sensor.get_or_none(Sensor.name == sensor)
                if query:
                    return json.jsonify({"serial": query.serial,
                                         "name": query.name})
                else:
                    return json.jsonify({"msg": "Sensor does not exist."}), 404
        else:
            with peewee_db.atomic():
                d = [{"serial": s.serial, "name": s.name} for s in Sensor.select().order_by(Sensor.id.desc()).limit(100)]
            return json.jsonify(d)


@app.route("/authentication/<string:uuid>",
           methods=["GET", "POST"])
def authentication(uuid):
    """Allow a client to request/recieve an authentication key."""
    if request.method == "POST":
        with peewee_db.atomic():
            if RestClient.get_or_none(RestClient.uuid == uuid):
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


@app.route("/")
def index():
    read = []
    with peewee_db.atomic():
        q = Sensor.select()
    for sensor in q:
        with peewee_db.atomic():
            q = Reading.get_or_none(Reading.sensor == sensor).order_by(Reading.timestamp.desc())
        read.append(q)
    return render_template("webui.html", readings=read)
