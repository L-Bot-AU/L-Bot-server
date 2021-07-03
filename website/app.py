#Documentation:
#Chart.js documentation: https://www.chartjs.org/docs/latest/
#clearing ad updating graph in chart.js: https://www.chartjs.org/docs/latest/developers/updates.html
#localStorage in js: https://code-maven.com/slides/javascript/local-storage-boolean
#innerHTML updating: https://www.w3schools.com/js/js_htmldom_events.asp
#setInterval for website to automatically call websocket: https://www.w3schools.com/jsref/met_win_setinterval.asp

from flask import Flask, render_template, request, jsonify, session, redirect, flash
import requests
from flask_bootstrap import Bootstrap
import urllib.request, json
from datetime import datetime
from website.login_form import LoginForm
from website.graph_form import GraphForm


app = Flask(__name__)
app.secret_key = "super secret" #TOOD: Store secret key in .env
bootstrap = Bootstrap(app)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/events")
def events():
    return render_template("events.html")


@app.route("/login", methods=["GET", "POST"])
def librarian_login():
    if "librarian" in session:
        return redirect("/librarian/statistics")
    form = LoginForm()
    if form.validate_on_submit():
        required_password = {"Junior": "jlb",
                             "Senior": "slb"}   #TODO: put passwords in .env
                                                #TODO: consider functionality to reset passwords (or just have them verify with their email e.g. OAuth)
        librarian = request.form["librarian"]
        password = request.form["password"]
        if password == required_password[librarian]:
            session["librarian"] = librarian
            return redirect("/librarian/statistics")
        else:
            form.password.errors.append("Incorrect password")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    session.pop("librarian", None)
    return redirect("/")


@app.route("/librarian/statistics", methods=["GET", "POST"])
def librarian_statistics():
    if session.get("librarian") is None:
        return redirect("/")
    form = GraphForm()
    if form.validate_on_submit():
        start_date = request.form["start_date"] #is a string, should turn into datetime object
        end_date = request.form["end_date"]
        selection = [option for option in ["periods", "morning", "lunch", "recess"] if request.form.get(option)]
        print(start_date, end_date, selection)
        if not selection:
            form.periods.errors.append("Please select at least one option")
        # todo update chart.js
    return render_template("librarian_statistics.html", form=form)


@app.route("/librarian/events", methods=["GET", "POST"])
def librarian_events():
    if session.get("librarian") is None:
        return redirect("/")
    return render_template("librarian_events.html")


@app.route("/librarian/about", methods=["GET", "POST"])
def librarian_about():
    if session.get("librarian") is None:
        return redirect("/")
    return render_template("librarian_about.html")


@app.route("/test")
def test():
    return render_template("testing.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


def __init__():
    app.run(host="0.0.0.0", port=80, debug=True)
