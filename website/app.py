#Documentation:
#Chart.js documentation: https://www.chartjs.org/docs/latest/
#clearing ad updating graph in chart.js: https://www.chartjs.org/docs/latest/developers/updates.html
#localStorage in js: https://code-maven.com/slides/javascript/local-storage-boolean
#innerHTML updating: https://www.w3schools.com/js/js_htmldom_events.asp
#setInterval for website to automatically call websocket: https://www.w3schools.com/jsref/met_win_setinterval.asp

from flask import Flask, render_template, request, jsonify, session
import requests
from flask_bootstrap import Bootstrap
import urllib.request, json
from datetime import datetime
from website.login_form import LoginForm


app = Flask(__name__)
app.secret_key = "super secret"
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
        return librarian_interface(session["librarian"])
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            required_password = {"Junior": "jlb",
                                 "Senior": "slb"}  # todo put in .env
            # print(dir(form)) # wait umm what does this do?
            library = request.form["library"]
            password = request.form["password"]
            print(library, password)
            if password == required_password[library]:
                session["librarian"] = library
                return librarian_interface(library)
            else:
                return render_template("login.html", form=form, incorrect_password=True)
        else:
            print("login failed")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    session.pop("librarian", None)
    return home()


@app.route("/librarian")
def librarian_interface(library):
    return render_template("librarian.html", library=library)


@app.route("/test")
def test():
    return render_template("testing.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


def __init__():
    app.run(host="0.0.0.0", port=80, debug=True)
