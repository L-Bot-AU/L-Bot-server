#Documentation:
#Chart.js documentation: https://www.chartjs.org/docs/latest/
#clearing ad updating graph in chart.js: https://www.chartjs.org/docs/latest/developers/updates.html
#localStorage in js: https://code-maven.com/slides/javascript/local-storage-boolean
#innerHTML updating: https://www.w3schools.com/js/js_htmldom_events.asp
#setInterval for website to automatically call websocket: https://www.w3schools.com/jsref/met_win_setinterval.asp

from flask import Flask, render_template, request, jsonify, session, redirect, flash
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
    return redirect("/login")


@app.route("/librarian/statistics", methods=["GET", "POST"])
def librarian_statistics():
    if "librarian" not in session:
        return redirect("/")
    form = GraphForm()
    if form.validate_on_submit():
        start_date = form["start_date"] #is a string but verified as a datetime, should turn into datetime object
        end_date = form["end_date"]
        # todo update chart.js
    return render_template("librarian_statistics.html", form=form)


@app.route("/librarian/events", methods=["GET", "POST"])
def librarian_events():
    if "librarian" not in session:
        return redirect("/")
    return render_template("librarian_events.html")


@app.route("/librarian/about", methods=["GET", "POST"])
def librarian_about():
    if "librarian" not in session:
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
