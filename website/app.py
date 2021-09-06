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
    """
    Returns the home page (front page of student interface)

    :return: HTML of the home page
    """

    session["interface_last_page"] = "/home"
    return render_template("home.html")


@app.route("/about")
def about():
    """
    Returns the about page (detailing information about opening and closing times, maximum seats and
    librarians)

    :return: HTML of the about page
    """

    session["interface_last_page"] = "/about"
    return render_template("about.html")


@app.route("/events")
def events():
    """
    Returns the events page (details events affecting library usage)

    :return: HTML of the events page
    """

    session["interface_last_page"] = "/events"
    return render_template("events.html")


@app.route("/main_page")
def main_page():
    """
    Returns the main page (i.e. the last page the user was on for the student or librarian interface)
    e.g. if the user's last page was the about page, they clicked on the librarian interface and 
    navigated back to the student interface, they would reach this endpoint and be redirected to the
    about page

    :return: A redirect to the last page of the respective interface the user was one
    """

    return redirect(session["interface_last_page"])


@app.route("/login", methods=["GET", "POST"])
def librarian_login():
    """
    Returns the login page (allows librarian to access the librarian interface) and logs them in
    if their password is correct

    :return: HTML of login page
    """

    # If the librarian is logged in already, redirect them to either their last page or the statistics page
    if "librarian" in session:
        if "librarian_last_page" in session:
            return redirect(session["librarian_last_page"])
        return redirect("/librarian/statistics")
    form = LoginForm()

    # If the Flask.WTForms form is valid (including if its a POST request)
    if form.validate_on_submit():
        required_password = {"Junior": "jlb",
                             "Senior": "slb"}
        librarian = request.form["librarian"]
        password = request.form["password"]

        # If their password matches the correct password, redirect them to the statistics page
        if password == required_password[librarian]:
            session["librarian"] = librarian # adds the librarian field to the session cookie
            return redirect("/librarian/statistics")

        # Otherwise, display an error
        else:
            form.password.errors.append("Incorrect password")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """
    Logs the user out and redirects them to the login page

    :return: A redirect to the login page
    """

    # Remove the librarian attribute from the session cookie, as well as the last page from
    # the librarian interface
    session.pop("librarian", None)
    session.pop("librarian_last_page", None)
    return redirect("/login")


@app.route("/librarian/statistics", methods=["GET", "POST"])
def librarian_statistics():
    """
    Returns the statistics page from the librarian and provides them with either a JSON of past data
    (if preview is selected) or an Excel spreadsheet (if download is selected)

    :return: HTML of the statistics page
    """

    if "librarian" not in session:
        return redirect("/")
    session["librarian_last_page"] = "/librarian/statistics"
    
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
        if start_date > date.today():
            form.start_date.errors.append("Start date must be before current date.")
            valid_dates = False
        if end_date > date.today():
            form.end_date.errors.append("End date must be before current date.")
            valid_dates = False
        if start_date > end_date:
            form.end_date.errors.append("End date must be after Start date.")
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
    """
    Returns the edit information page and saves any changes that the librarian has made to the
    database

    :return: HTML of edit information page
    """

    # If the user is not authorized as a librarian, redirect them away
    if "librarian" not in session:
        return redirect("/")
    session["librarian_last_page"] = "/librarian/edit"

    Session = sessionmaker(bind=engine)
    dbsession = Session()
    library = {"Junior": "jnr", "Senior": "snr"}[session["librarian"]]
    
    if request.method == "POST": # if the request method is POST, then changes are to be saved
        print(request.json)
        tab = request.json.get("tab")
        if tab == "general":
            opening_times = request.json.get("opening_times")
            closing_times = request.json.get("closing_times")
            max_seats = request.json.get("max_seats")
            librarians = request.json.get("librarians")

            # Loop through each record for each weekday and save the new opening/closing times
            for timesRecord in dbsession.query(LibraryTimes).filter_by(library=library):
                day = timesRecord.day
                timesRecord.openinghour, timesRecord.openingminute = opening_times[day]
                timesRecord.closinghour, timesRecord.closingminute = closing_times[day]

            # Save the new maximum number of seats
            dbsession.query(MaxSeats).filter_by(library=library).first().seats = max_seats

            # Delete the existing list of librarian names
            dbsession.query(Librarians).filter_by(library=library).delete()

            # Populate the Librarians table with the new names of librarians
            for name in librarians:
                librarianRecord = Librarians(
                    library=library,
                    name=name
                )
                dbsession.add(librarianRecord)

        elif tab == "events":
            events = request.json.get("events")

            # Delete the existing list of events
            dbsession.query(Events).filter_by(library=library).delete()

            # Populate the events table with the new events
            for event in events:
                eventRecord = Events(
                    library=library,
                    impact=event.get("impact"),
                    event=event.get("event")
                )
                dbsession.add(eventRecord)

        elif tab == "alerts":
            alerts = request.json.get("alerts")

            # Delete the existing list of alerts
            dbsession.query(Alerts).filter_by(library=library).delete()

            # Populate the alerts table with the new alerts
            for alert in alerts:
                alertRecord = Alerts(
                    library=library,
                    type=alert["importance"],
                    alert=alert["alert"]
                )
                dbsession.add(alertRecord)
        else:
            return "Invalid tab", 404
        
        dbsession.commit()
        
        return "Success!"

    opening_times = {}
    closing_times = {}

    # Get the opening/closing times for each day
    for day in DAYS:
        timesRecord = dbsession.query(LibraryTimes).filter_by(library=library, day=day).first()
        opening_times[day] = [timesRecord.openinghour, timesRecord.openingminute]
        closing_times[day] = [timesRecord.closinghour, timesRecord.closingminute]
    
    # Get the events and alerts and sort them by their impact and importance type respectively
    events = list(dbsession.query(Events).filter_by(library=library).all())
    alerts = list(dbsession.query(Alerts).filter_by(library=library).all())
    events.sort(key=lambda x:["high", "moderate", "low"].index(x.impact))
    alerts.sort(key=lambda x:["warning", "information"].index(x.type))


    # Return the edit information page's HTML as well as the existing information that may be changed
    return render_template("librarian_edit.html",
        opening_times=str(opening_times),
        closing_times=str(closing_times),
        max_seats=str(dbsession.query(MaxSeats).filter_by(library=library).first().seats),
        librarians=dbsession.query(Librarians).filter_by(library=library).all(),
        events=events,
        alerts=alerts
    )


@app.route("/test")
def test():
    return render_template("testing.html")


@app.errorhandler(404)
def page_not_found(e):
    """
    Returns an error page in case an error of status code 404 has occured (page not found)

    :return: HTML of 404 error page
    """

    return render_template("404.html")


def __init__():
    engine, Base, Data, Count, PastData, LibraryTimes, MaxSeats, Librarians, Events, Alerts = database.genDatabase()
    app.run(host=WEBSITE_HOST, port=WEBSITE_PORT, debug=WEBSITE_DEBUG)
