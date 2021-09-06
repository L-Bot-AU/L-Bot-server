from constants import WEBSITE_CLIENT_PORT, WEBSITE_UPDATE_TIMEOUT, DAYS, TIMES
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
    """static data, called when a user loads the website"""
    print(__name__, "Connected", sid)
    sendStaticData()
    sendDynamicData()
    
@sio.event
def disconnect(sid):
    print(__name__, "Disconnected", sid)

def update():
    """dynamic data (e.g. current availability of website), sent to all users every regular interval"""
    while True:
        sendDynamicData()
        sio.sleep(WEBSITE_UPDATE_TIMEOUT)

def sendStaticData():
    sio.emit("events", get_events())
    
    for lib in ["jnr", "snr"]:
        sio.emit(lib + "Opening", get_opening(lib))
        sio.emit(lib + "Max", get_max(lib))
        sio.emit(lib + "Librarians", get_librarians(lib))

def sendDynamicData():
    for lib in ["jnr", "snr"]:
        sio.emit(lib + "Periods", get_periods(lib))
        sio.emit(lib + "Alert", get_alert(lib))
        sio.emit(lib + "Remaining", get_max(lib) - get_count(lib))
        sio.emit(lib + "Fullness", round(get_count(lib)/get_max(lib)*100))
        sio.emit(lib + "Trends", get_trends(lib))
    
def get_count(lib):
    Session = sessionmaker(bind=engine)
    session = Session()
    if lib == "jnr":
        return session.query(Count).first().jnrvalue
    elif lib == "snr":
        return session.query(Count).first().snrvalue

def get_trends(lib):
    Session = sessionmaker(bind=engine)
    session = Session()
    trends = {
        "labels": TIMES,
        "data": []
    }
    for day in DAYS:
        day_trends = []
        for time in TIMES:
            data = session.query(Data).filter_by(day=day, time=time).first()
            if lib == "jnr":
                pred = data.jnr_expected
            elif lib == "snr":
                pred = data.snr_expected
            day_trends.append(pred)
        trends["data"].append(day_trends)
    return trends

def get_opening(lib):
    Session = sessionmaker(bind=engine)
    session = Session()
    library_times = {}
    for day in DAYS:
        timeRecord = session.query(LibraryTimes).filter_by(library=lib, day=day).first()
        openingtime = datetime.time(hour=timeRecord.openinghour, minute=timeRecord.openingminute)
        closingtime = datetime.time(hour=timeRecord.closinghour, minute=timeRecord.closingminute)
        library_times[day] = f"{openingtime.strftime('%#I:%M%p' if platform.system() == 'Windows' else '%-I:%M%p').lower()} - {closingtime.strftime('%#I:%M%p').lower()}"
    return library_times

def get_max(lib):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session.query(MaxSeats).filter_by(library=lib).first().seats

def get_librarians(lib):
    Session = sessionmaker(bind=engine)
    session = Session()
    librarians = session.query(Librarians).filter_by(library=lib).all()
    return [librarian.name for librarian in librarians]

def get_alert(lib):
    Session = sessionmaker(bind=engine)
    session = Session()
    alerts = session.query(Alerts).filter_by(library=lib).all()
    return [[alert.alert, alert.type] for alert in alerts]

def get_events():
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
    # TODO: MAKE WORK NICE BETTER THANK!!!!!!!!!!
    # order is indicative of order of periods for that day
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
    }[lib]

kill_port.kill_port(WEBSITE_CLIENT_PORT)

engine, Base, Data, Count, PastData, LibraryTimes, MaxSeats, Librarians, Events, Alerts = database.genDatabase()
task = sio.start_background_task(update)
eventlet.wsgi.server(eventlet.listen(('', WEBSITE_CLIENT_PORT)), app)

