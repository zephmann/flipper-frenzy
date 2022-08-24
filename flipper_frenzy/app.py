from flask import Flask, request, session, render_template, redirect, url_for

import flipper_frenzy.main

app = Flask(__name__)
app.secret_key = "give the golden goose a gander"


@app.route("/")
def index():
    message = request.args.get("message")
    print(f"Message {message}")
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
        message = "Player added!"
    else:
        message = "Name can't be empty!"
    return redirect(url_for("index", message=message))


@app.route("/add-machine", methods=["POST"])
def add_machine():
    machine_name = request.form.get("name")
    if machine_name:
        data = session["tournament"]
        t = flipper_frenzy.main.Tournament()
        t.restore(data)
        t.add_machine(machine_name)
        session["tournament"] = t.serialize()
        message = "Machine added!"
    else:
        message = "Name can't be empty!"
    return redirect(url_for("index", message=message))


@app.route("/next-match", methods=["GET", "POST"])
def next_match():
    data = session["tournament"]
    t = flipper_frenzy.main.Tournament()
    t.restore(data)
    message = t.next_match()
    session["tournament"] = t.serialize()
    return redirect(url_for("index", message=message))


@app.route("/match-winner", methods=["GET", "POST"])
def match_winner():
    data = session["tournament"]
    t = flipper_frenzy.main.Tournament()
    t.restore(data)
    t.complete_match(int(request.args["match_id"]), request.args["player_name"])
    session["tournament"] = t.serialize()
    return redirect(url_for("index", message="Match finished!"))


# TODO revert back to post only
@app.route("/reset", methods=["GET", "POST"])
def reset():
    session.pop("tournament", None)
    return redirect(url_for("index", message="Tournament reset!"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
