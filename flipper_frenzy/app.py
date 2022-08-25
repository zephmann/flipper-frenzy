from flask import Flask, request, session, render_template, redirect, url_for

import flipper_frenzy.main

app = Flask(__name__)
app.secret_key = "give the golden goose a gander"


@app.route("/")
def index():
    message = session.pop("message", None)
    t = flipper_frenzy.main.Tournament()
    data = session.get("tournament")
    if data is not None:
        t.restore(data)
    session["tournament"] = t.serialize()
    return render_template("index.html", message=message, **t.serialize())


@app.route("/add-player", methods=["POST"])
def add_player():
    player_name = request.form.get("name")
    if player_name:
        data = session["tournament"]
        t = flipper_frenzy.main.Tournament()
        t.restore(data)
        t.add_player(player_name)
        session["tournament"] = t.serialize()
        session["message"] = "Player added!"
    else:
        session["message"] = "Name can't be empty!"
    return redirect(url_for("index"))


@app.route("/remove-player/<player_name>", methods=["GET"])
def remove_player(player_name):
    # player_name = request.args.get("name")
    data = session["tournament"]
    t = flipper_frenzy.main.Tournament()
    t.restore(data)
    session["message"] = t.remove_player(player_name)
    session["tournament"] = t.serialize()
    return redirect(url_for("index"))


@app.route("/add-machine", methods=["POST"])
def add_machine():
    machine_name = request.form.get("name")
    if machine_name:
        data = session["tournament"]
        t = flipper_frenzy.main.Tournament()
        t.restore(data)
        t.add_machine(machine_name)
        session["tournament"] = t.serialize()
        session["message"] = "Machine added!"
    else:
        session["message"] = "Name can't be empty!"
    return redirect(url_for("index"))


@app.route("/remove-machine/<machine_name>", methods=["GET"])
def remove_machine(machine_name):
    data = session["tournament"]
    t = flipper_frenzy.main.Tournament()
    t.restore(data)
    session["message"] = t.remove_machine(machine_name)
    session["tournament"] = t.serialize()
    return redirect(url_for("index"))


@app.route("/next-match", methods=["GET", "POST"])
def next_match():
    data = session["tournament"]
    t = flipper_frenzy.main.Tournament()
    t.restore(data)
    session["message"] = t.next_match()
    session["tournament"] = t.serialize()
    return redirect(url_for("index"))


@app.route("/match-winner", methods=["GET", "POST"])
def match_winner():
    data = session["tournament"]
    t = flipper_frenzy.main.Tournament()
    t.restore(data)
    t.complete_match(int(request.args["match_id"]), request.args["player_name"])
    session["tournament"] = t.serialize()
    session["message"] = "Match finished!"
    return redirect(url_for("index"))


# TODO revert back to post only
@app.route("/reset", methods=["GET", "POST"])
def reset():
    session.pop("tournament", None)
    session["message"] = "Tournament reset!"
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
