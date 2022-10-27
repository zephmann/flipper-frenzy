
import json

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
    print(t._avail_players)
    return render_template("index.html", message=message, **t.serialize())


@app.route("/player/<player_name>")
def player_detail(player_name):
    t = flipper_frenzy.main.Tournament()
    data = session.get("tournament")
    if data is None:
        session["message"] = "No tournament data found in current session!"
        return redirect(url_for("index"))
    t.restore(data)
    player_data = t.get_player_data(player_name)
    return render_template("player.html", **player_data)


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


@app.route("/enable-player/", methods=["GET"])
def enable_player():
    player_name = request.args.get("player_name")
    enable = request.args.get("enable") == "True"
    data = session["tournament"]
    t = flipper_frenzy.main.Tournament()
    t.restore(data)
    session["message"] = t.enable_player(player_name, enable)
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


@app.route("/remove-machine/", methods=["GET"])
def enable_machine():
    machine_name = request.args.get("machine_name")
    enable = request.args.get("enable") == "True"
    data = session["tournament"]
    t = flipper_frenzy.main.Tournament()
    t.restore(data)
    session["message"] = t.enable_machine(machine_name, enable)
    session["tournament"] = t.serialize()
    return redirect(url_for("index"))


@app.route("/sort/", methods=["GET"])
def sort_by():
    by_rank = request.args.get("by_rank") == "True"
    data = session["tournament"]
    t = flipper_frenzy.main.Tournament()
    t.restore(data)
    t.sort_by(by_rank)
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


@app.route("/shuffle", methods=["GET", "POST"])
def shuffle():
    data = session["tournament"]
    t = flipper_frenzy.main.Tournament()
    t.restore(data)
    t.shuffle()
    session["message"] = "Queue shuffled!"
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
@app.route("/reset-all", methods=["GET", "POST"])
def reset_all():
    session.pop("tournament", None)
    session["message"] = "All data cleared!"
    return redirect(url_for("index"))


# TODO revert back to post only
@app.route("/reset-tournament", methods=["GET", "POST"])
def reset_tournament():
    data = session["tournament"]
    del data["avail_players"]
    del data["players"]
    del data["matches"]
    t = flipper_frenzy.main.Tournament()
    t.restore(data)
    session["message"] = "Tournament reset!"
    return redirect(url_for("index"))


@app.route("/debug")
def debug():
    t = flipper_frenzy.main.Tournament()
    data = session.get("tournament")
    if data is not None:
        t.restore(data)
    message = session.pop("message", None)
    data = json.dumps(t.serialize(), indent=2)
    return render_template("debug.html", data=data, message=message)


@app.route("/debug-update", methods=["POST"])
def debug_post():
    data = request.form.get("data")
    t = flipper_frenzy.main.Tournament()
    try:
        data = json.loads(data)
        t.restore(data)
    except:
        session["message"] = "Could not decode JSON data!"
        return redirect(url_for("debug"))

    session["tournament"] = t.serialize()
    session["message"] = "Tournament data updated!"
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
