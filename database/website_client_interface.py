from sqlalchemy.orm import sessionmaker
import socketio
import datetime
import eventlet

# for library overview website
CLIENT_PORT = 2910

# number of seconds before each dynamic data update
TIMEOUT = 2.0

# TODO: move these values into data files instead (shouldnt be defined through code)
JNR_MAX = 108
SNR_MAX = 84
JNR_OPENING = {
    "mon": "7:30am - 3:30pm",
    "tue": "7:30am - 3:30pm",
    "wed": "7:30am - 3:30pm",
    "thu": "7:30am - 3:30pm",
    "fri": "7:30am - 3:30pm",
}
SNR_OPENING = {
    "mon": "8:00am - 2:30pm",
    "tue": "8:00am - 2:30pm",
    "wed": "8:00am - 12:30pm",
    "thu": "8:00am - 3:15pm",
    "fri": "8:00am - 2:30pm",
}
JNR_LIBRARIANS = ["Ms Crothers"]
SNR_LIBRARIANS = ["Mr Wiramhardja", "Ms Meredith"]

days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
times = ["Morning", "Break 1", "Break 2"]


sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)
    
@sio.event
def connect(sid, environ):
    """static data, called when a user loads the website"""
    print(__name__, "Connected", sid)
    
    # TODO: events should have dynamic data
    sio.emit("events", get_events())
    
    sio.emit("jnrOpening", JNR_OPENING)
    sio.emit("jnrMax", JNR_MAX)
    sio.emit("jnrLibrarians", JNR_LIBRARIANS)
    
    sio.emit("snrOpening", SNR_OPENING)
    sio.emit("snrMax", SNR_MAX)
    sio.emit("snrLibrarians", SNR_LIBRARIANS)

@sio.event
def disconnect(sid):
    print(__name__, "Disconnected", sid)

def update(engine, Base, Data, Count, PastData):
    """dynamic data (e.g. current availability of website), sent to all users every regular interval"""
    while True:
        sio.emit("jnrAlert", get_alert(engine, "jnr"))
        sio.emit("jnrRemaining", JNR_MAX - get_count(engine, Count, "jnr"))
        sio.emit("jnrFullness", round(get_count(engine, Count, "jnr")/JNR_MAX, 1))
        #sio.emit("jnrTrends", get_trends(engine, Data, "jnr"))
        
        sio.emit("snrAlert", get_alert(engine, "snr"))
        sio.emit("snrRemaining", SNR_MAX - get_count(engine, Count, "snr"))
        sio.emit("snrFullness", round(get_count(engine, Count, "snr")/SNR_MAX, 1))
        #sio.emit("snrTrends", get_trends(engine, Data, "snr"))
        
        sio.sleep(TIMEOUT)

def get_count(engine, Count, lib):
    Session = sessionmaker(bind=engine)
    session = Session()
    if lib == "jnr":
        return session.query(Count).first().jnrvalue
    elif lib == "snr":
        return session.query(Count).first().snrvalue

def get_trends(engine, Data, lib):
    Session = sessionmaker(bind=engine)
    session = Session()
    trends = {}
    trends["labels"] = times
    trends["data"] = []
    for day in days:
        day_trends = []
        for time in times:
            data = session.query(Data).filter_by(day=day, time=time).first()
            if lib == "jnr":
                pred = data.jnr_expected
            elif lib == "snr":
                pred = data.snr_expected
            day_trends.append(pred)
        trends["data"].append(day_trends)
    return trends

def get_alert(engine, lib):
    # TODO
    if lib == "jnr":
        #return "Junior library overtaken by wild animals, keep out!"
        return ""
    else:
        return "Senior library overtaken by wild animals, keep out!" or ""
        #return ""

def get_events():
    # TODO
    return [
        {"text": "Cyril stupid!!!", "impact": "high"},
        {"text": "Cyril stupid!!!", "impact": "high"},
        {"text": "Cyril stupid!!!", "impact": "high"},
        {"text": "Cyril stupid!!", "impact": "moderate"},
        {"text": "Cyril stupid!!", "impact": "moderate"},
        {"text": "Cyril stupid!", "impact": "low"},
        {"text": "Cyril stupid!", "impact": "low"},
        {"text": "Cyril stupid!", "impact": "low"},
        {"text": "Cyril stupid!", "impact": "low"},
    ]

def __init__(engine, Base, Data, Count, PastData):
    task = sio.start_background_task(update, engine, Base, Data, Count, PastData)
    eventlet.wsgi.server(eventlet.listen(('', CLIENT_PORT)), app)

