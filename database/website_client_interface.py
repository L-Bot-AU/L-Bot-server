from constants import WEBSITE_CLIENT_PORT, WEBSITE_UPDATE_TIMEOUT, DAYS, TIMES
from database import database
from sqlalchemy.orm import sessionmaker
import kill_port
import socketio
import datetime
import eventlet

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
    return {
        "jnr": {
            "mon": "7:30am - 3:30pm",
            "tue": "7:30am - 3:30pm",
            "wed": "7:30am - 3:30pm",
            "thu": "7:30am - 3:30pm",
            "fri": "7:30am - 3:30pm",
        },
        "snr": {
            "mon": "8:00am - 2:30pm",
            "tue": "8:00am - 2:30pm",
            "wed": "8:00am - 12:30pm",
            "thu": "8:00am - 3:15pm",
            "fri": "8:00am - 2:30pm",
        }
    }[lib]

def get_max(lib):
    # TODO: get data from librarian interface
    return {
        "jnr": 108,
        "snr": 84
    }[lib]

def get_librarians(lib):
    # TODO: get data from librarian interface
    return {
        "jnr": ["Ms Crothers"],
        "snr": ["Mr Wiramhardja", "Ms Meredith"]
    }[lib]

def get_alert(lib):
    # TODO: get data from librarian interface
    return {
        "jnr": "", # "Junior library overtaken by wild animals, keep out!"
        "snr": "Senior library overtaken by wild animals, keep out!" or ""
    }[lib]

def get_events():
    # TODO: get data from librarian interface
    return [
        {"text": "Too Bar Baz!!!", "impact": "moderate", "library":"jnr"},
        {"text": "Wild animals have taken over the junior library!!!", "impact": "high","library":"jnr"},
		{"text": "Make sure you clean up after you play chess", "impact": "moderate","library":"jnr"},
        {"text": "Have you seen my glasses?", "impact": "high","library":"snr"},
        {"text": "Remember to tuck in your chairs.", "impact": "low","library":"snr"},
    ]

def get_periods(lib):
    # TODO: get data from librarian interface
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

engine, Base, Data, Count, PastData = database.genDatabase()
task = sio.start_background_task(update)
eventlet.wsgi.server(eventlet.listen(('', WEBSITE_CLIENT_PORT)), app)

