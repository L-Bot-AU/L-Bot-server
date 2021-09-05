#Documentation:
#Chart.js documentation: https://www.chartjs.org/docs/latest/
#clearing ad updating graph in chart.js: https://www.chartjs.org/docs/latest/developers/updates.html
#localStorage in js: https://code-maven.com/slides/javascript/local-storage-boolean
#innerHTML updating: https://www.w3schools.com/js/js_htmldom_events.asp
#setInterval for website to automatically call websocket: https://www.w3schools.com/jsref/met_win_setinterval.asp

from flask import Flask, render_template, request, jsonify, session, redirect, flash, send_file, send_from_directory
from constants import WEBSITE_HOST, WEBSITE_PORT, WEBSITE_DEBUG, DAYS
from database import database
from sqlalchemy.orm import sessionmaker
from website.login_form import LoginForm
from website.graph_form import GraphForm
from website.librarian_data import get_data, create_excel_spreadsheet
from flask_bootstrap import Bootstrap
from datetime import date, datetime
import urllib.request, json


app = Flask(__name__)
app.secret_key = "super secret" #TODO: Store secret key in .env
bootstrap = Bootstrap(app)
engine, Base, Data, Count, PastData, LibraryTimes, MaxSeats, Librarians, Events, Alerts = database.genDatabase()


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
    graphData = {"dates": [],
                 "values": []}
    if form.validate_on_submit():
        start_date = form["start_date"].data #is a datetime.date object
        end_date = form["end_date"].data
        data_frequency = form["data_frequency"].data #is a string
        preview = form["preview"].data
        download = form["download"].data
        # Verify dates are valid
        valid_dates = True
        if start_date >= date.today():
            form.start_date.errors.append("Start date must be before current date.")
            valid_dates = False
        if end_date >= date.today():
            form.end_date.errors.append("End date must be before current date.")
            valid_dates = False
        if start_date >= end_date:
            form.end_date.errors.append("End date must be after Start date.")
            form.end_date.errors.append("blah blah blah etc.") # For testing purposes
            form.end_date.errors.append("blah blah blah etc.")
            valid_dates = False

        # Apply necessary action
        if valid_dates and preview:
            data = get_data(start_date, end_date, data_frequency, session["librarian"], "preview")
            graphData = data
        elif valid_dates and download:
            data = get_data(start_date, end_date, data_frequency, session["librarian"], "download")
            directory = "/Downloads"
            create_excel_spreadsheet(data)
            #todo use send_file to somehow download the file
            # return send_file(download_excel_spreadsheet(data), attachment_filename="spreadsheet.xlsx")
    return render_template("librarian_statistics.html", form=form, graphData=graphData)


@app.route("/librarian/edit", methods=["GET", "POST"])
def librarian_edit():
    if "librarian" not in session:
        return redirect("/")
    Session = sessionmaker(bind=engine)
    dbsession = Session()
    library = {"Junior": "jnr", "Senior": "snr"}[session["librarian"]]
    
    if request.method == "POST":
        tab = request.json.get("tab")
        if tab == "general":
            opening_times = request.json.get("opening_times")
            closing_times = request.json.get("closing_times")
            max_seats = request.json.get("max_seats")
            librarians = request.json.get("librarians")
            for timesRecord in dbsession.query(LibraryTimes).filter_by(library=library):
                day = timesRecord.day
                timesRecord.openinghour, timesRecord.openingminute = opening_times[day]
                timesRecord.closinghour, timesRecord.closingminute = closing_times[day]
            dbsession.query(MaxSeats).first().seats = max_seats
            dbsession.query(Librarians).delete()
            for name in librarians:
                librarianRecord = Librarians(
                    library=library,
                    name=name
                )
                dbsession.add(librarianRecord)
        elif tab == "events":
            events = request.json.get("events")
        elif tab == "alerts":
            alerts = request.json.get("alerts")
        else:
            return "Invalid tab", 404
        
        dbsession.commit()
        
        return "Your changes have been saved!"

    opening_times = {}
    closing_times = {}
    for day in DAYS:
        timesRecord = dbsession.query(LibraryTimes).filter_by(library=library, day=day).first()
        opening_times[day] = [timesRecord.openinghour, timesRecord.openingminute]
        closing_times[day] = [timesRecord.closinghour, timesRecord.closingminute]
    
    events = list(dbsession.query(Events).filter_by(library=library).all())
    alerts = list(dbsession.query(Alerts).filter_by(library=library).all())
    events.sort(key=lambda x:["high", "moderate", "low"].index(x))
    alerts.sort(key=lambda x:["high", "moderate", "low"].index(x))

    return render_template("librarian_edit.html",
        opening_times=str(opening_times),
        closing_times=str(closing_times),
        max_seats=str(dbsession.query(MaxSeats).filter_by(library=library).first().seats),
        librarians=dbsession.query(Librarians).filter_by(library=library).all(),
        events=events,
        alerts=alerts
    )


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
    engine, Base, Data, Count, PastData, LibraryTimes, MaxSeats, Librarians, Events, Alerts = database.genDatabase()
    app.run(host=WEBSITE_HOST, port=WEBSITE_PORT, debug=WEBSITE_DEBUG)
