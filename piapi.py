from flask import Flask, request
app = Flask(__name__)


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
