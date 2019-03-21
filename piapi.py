from flask import Flask, request
app = Flask(__name__)


@app.route("/days/", defaults={"day": None}, methods=["GET"])
@app.route("/days/<string:day>", methods=["GET"])
def days(day):
    if day:
        return day
    else:
        return "List of days."


@app.route("/records/", defaults={"record": None}, methods=["GET", "POST"])
@app.route("/records/<string:record>", methods=["GET"])
def records(record):
    if request.method == "POST":
        # Get JSON and save.
        pass
    elif request.method == "GET":
        if record:
            return "Record " + record
        else:
            return "List of records."
