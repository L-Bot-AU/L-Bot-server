from constants import WEBSITE_CLIENT_PORT, WEBSITE_UPDATE_TIMEOUT, DAYS, TIMES
from database import database
from sqlalchemy.orm import sessionmaker
import kill_port
import socketio
import datetime
import eventlet
import platform

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    """
    Called when a client (the website) connects to the server, and will send data to it
    
    :param sid: The session ID of the connecting client
    :param environ: A dictionary representing information from the WSGI environment
    :return:
    """

    print(__name__, "Connected", sid)
    sendStaticData() # send static data which doesn't update
    sendDynamicData() # send dynamic data which regularly updates
    
@sio.event
def disconnect(sid):
    """
    Called when a client (the website) disconnects from the server, and will print a message to the console
    :return:
    """

    print(__name__, "Disconnected", sid)

def update():
    """
    Regularly sends dynamic data to all connected clients every 10 seconds

    :return:
    """

    while True:
        sendDynamicData()
        sio.sleep(WEBSITE_UPDATE_TIMEOUT) # wait for 10 seconds before sending again

def sendStaticData():
    """
    Sends static data (unchanging) when a client connects

    :return:
    """

    sio.emit("events", get_events()) # send all events
    
    for lib in ["jnr", "snr"]:
        sio.emit(lib + "Opening", get_opening(lib)) # send opening and closing times for each library
        sio.emit(lib + "Max", get_max(lib)) # send maximum number of seats for each library
        sio.emit(lib + "Librarians", get_librarians(lib)) # send list librarains

def sendDynamicData():
    """
    Sends dynamic data (new data sent every 10 seconds) while a client remains connected

    :return:
    """

    for lib in ["jnr", "snr"]:
        sio.emit(lib + "Periods", get_periods(lib)) # send predicted usage of each period today
        sio.emit(lib + "Alert", get_alert(lib)) # send all alerts
        sio.emit(lib + "Remaining", get_max(lib) - get_count(lib)) # send remaining number of seats
        sio.emit(lib + "Fullness", round(get_count(lib)/get_max(lib)*100)) # send percentage fullness
        sio.emit(lib + "Trends", get_trends(lib)) # send predicted usages for each weekday
    
def get_count(lib):
    """
    Gets the current occupancy for a given library

    :param lib: The library requested for
    :return: An integer which is the provided library's current occupancy
    """

    Session = sessionmaker(bind=engine)
    session = Session()
    if lib == "jnr":
        return session.query(Count).first().jnrvalue
    elif lib == "snr":
        return session.query(Count).first().snrvalue

def get_trends(lib):
    """
    Returns the predicted occupancies for each of the 5 weekdays over time

    :param lib: The library requested for
    :return: A dictionary with a "labels" key mapping to a list of times and a "data" key mapping to a
             list of 5 lists. The first list represents the data over time for Monday, the second for
             Tuesday and so on up until Friday
    """

    Session = sessionmaker(bind=engine)
    session = Session()
    trends = {
        "labels": TIMES,
        "data": []
    }
    # loop through each weekday
    for day in DAYS:
        day_trends = []
        # loop through each time
        for time in TIMES:
            # get the record with the provided day and time
            data = session.query(Data).filter_by(day=day, time=time).first()
            if lib == "jnr":
                pred = data.jnr_expected
            elif lib == "snr":
                pred = data.snr_expected
            day_trends.append(pred)
        trends["data"].append(day_trends)
    return trends

def get_opening(lib):
    """
    Returns the opening and closing times for a given library

    :param lib: The library requested for
    :return: A dictionary with an "opening" key mapping to a list of opening times for each weekday and a
             "closing" key mapping to a list of closing times for each weekday
    """

    Session = sessionmaker(bind=engine)
    session = Session()
    library_times = {}

    # loop through each weekday
    for day in DAYS:
        # get the opening time with the provided library and day
        timeRecord = session.query(LibraryTimes).filter_by(library=lib, day=day).first()

        # create datetime objects of the opening and closing times (must do so to convert to 12-hour time)
        openingtime = datetime.time(hour=timeRecord.openinghour, minute=timeRecord.openingminute)
        closingtime = datetime.time(hour=timeRecord.closinghour, minute=timeRecord.closingminute)

        # return the dictionary of opening and closing times
        library_times[day] = {
            "opening": openingtime.strftime('%I:%M%p').lstrip("0").lower(),
            "closing": closingtime.strftime('%I:%M%p').lstrip("0").lower()
        }
    return library_times

def get_max(lib):
    """
    Returns the maximum number of seats in the library

    :param lib: The library requested for
    :return: The maximum number of seats in the provided library as an integer
    """

    Session = sessionmaker(bind=engine)
    session = Session()
    return session.query(MaxSeats).filter_by(library=lib).first().seats

def get_librarians(lib):
    """
    Returns a list of librarians of a library

    :param lib: The library requested for
    :return: An array of librarian names for the provided library
    """

    Session = sessionmaker(bind=engine)
    session = Session()
    librarians = session.query(Librarians).filter_by(library=lib).all()
    return [librarian.name for librarian in librarians]

def get_alert(lib):
    """
    Returns a list of alerts for a library

    :param lib: The library requested for
    :return: An array of 2-length arrays, each representing a different alert. The first index is the
             alert text and the second is the "type" of alert (as "warning" or "information")
    """

    Session = sessionmaker(bind=engine)
    session = Session()
    alerts = session.query(Alerts).filter_by(library=lib).all()
    return [[alert.alert, alert.type] for alert in alerts]

def get_events():
    """
    Returns a list of events

    :return: A list of dictionaries of all library events. Each dictionary has 3 keys:
                - "text" which maps to the event text
                - "impact" which maps to the impact of the event ("low", "moderate" or "high")
                - "library" which maps to the library which the event impacts
    """

    Session = sessionmaker(bind=engine)
    session = Session()
    events = []
    for event in session.query(Events).all():
        events.append(
            {"text": event.event, "impact": event.impact, "library": event.library}
        )
    events.sort(key=lambda x:["high", "moderate", "low"].index(x["impact"]))
    return events

def get_periods(lib):
    # Currently this function returns hard-coded data as we don't have enough occupancy data to create
    # predictions across every time (mainly due to COVID-19 preventing us from running the system at
    # school for a whole day)
    """
    Returns a period-by-period breakdown of the expected library usage

    :param lib: The library requested for
    :return: A dictionary with each library mapping to a list of lists, each list's first index being
             the period and the second being the average expected occupancy during that period
    """
    return {
        "jnr": [
            ["1", 5],
            ["2", 4],
            ["Recess", 46],
            ["3", 12],
            ["Lunch", 56],
            ["4", 14],
            ["5", 1],
        ],
        "snr": [
            ["1", 5],
            ["2", 4],
            ["Recess", 46],
            ["3", 12],
            ["Lunch", 56],
            ["4", 14],
            ["5", 1],
        ],
    }[lib] # index required library from hard-coded values

# Kill the process (if any) currently on this server-client interface port
kill_port.kill_port(WEBSITE_CLIENT_PORT)

# Generate the database tables for usage
engine, Base, Data, Count, PastData, LibraryTimes, MaxSeats, Librarians, Events, Alerts = database.genDatabase()

# Start this server component (which interfaces with the website client)
task = sio.start_background_task(update)
eventlet.wsgi.server(eventlet.listen(('', WEBSITE_CLIENT_PORT)), app)

