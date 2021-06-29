from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates, sessionmaker
from Crypto.Cipher import AES
from predictions.getData import getData
import websockets
import threading
import datetime
import asyncio
import random
import base64
import socket
import json
import os


os.remove("library_usage.db")
engine = create_engine("sqlite:///library_usage.db", echo=False)
Base = declarative_base()

KEY = b'automate_egggggg'
# two seperate objects are required for decrypting and encrypting (PyCryptoDome weirdness)
aesenc = AES.new(KEY, AES.MODE_ECB)
aesdec = AES.new(KEY, AES.MODE_ECB)

days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
times = ["Morning", "Break 1", "Break 2"]
# weeks = ["A", "B", "C"]
cycledays = days
# cycledays = [day+week for day in days for week in weeks]

CLIENT_PORT = 2910 # for library overview website
JNRCOUNTER_PORT = 9482 # for junior library count updates
SNRCOUNTER_PORT = 11498 # for senior library count updates

# TODO: move these values into data files instead (shouldnt be defined through code)
JNRMAX = 108
SNRMAX = 84


def print(*args):
    logfile = open("serverlog.log", "a")
    logfile.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {' '.join(map(str, args))}\n")
    logfile.close()
print("a")


def getOpeningTime(): # currently a stub
    today = datetime.datetime.now()
    today = today.replace(minute=today.minute+1)
    return today.hour, today.minute


def getClosingTime():
    global clos
    try:
        return clos.hour, clos.minute
    except:
        today = datetime.datetime.now()
        clos = today.replace(minute=today.minute+1)
        return clos.hour, clos.minute


def restartdb():
    Session = sessionmaker(bind=engine)
    begsession = Session()

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    for day in days:
        for time in times:
            d = Data(day=day, time=time)
            begsession.add(d)

    begsession.add(Count())

    begsession.commit()
    print("Reset database")


# TODO: remove this websocket coroutine and replace with socket.io
async def client_help(websocket, path):
    """
    The asynchronous coroutine attached to a websocket which sends the requested data to the library overview website

    websocket: the websocket object which Blair's website will connect to
    path: the path from the socket indicating what information the website wishes to receive (1 of 4 possibilities)
    """
    print(f"Connection received from {websocket} at {path}")
    options = {
        "/home": lambda: json.dumps({
            "jnr": {
                "count": count("jnr"),
                "max": JNRMAX,
                "predictions": None, # TODO
                "trends": get_trends("jnr"),
                "alert": "Junior library overtaken by wild animals, keep out!", # or ""
            },
            "snr": {
                "count": count("snr"),
                "max": SNRMAX,
                "predictions": None, # TODO
                "trends": get_trends("snr"),
                "alert": "", # or "SHOUTING!"
            }
        }),
        
        # TODO: currently the values are hard coded
        "/events": lambda: json.dumps([
            {"text": "Cyril stupid!!!", "impact": "high"},
            {"text": "Cyril stupid!!!", "impact": "high"},
            {"text": "Cyril stupid!!!", "impact": "high"},
            {"text": "Cyril stupid!!", "impact": "moderate"},
            {"text": "Cyril stupid!!", "impact": "moderate"},
            {"text": "Cyril stupid!", "impact": "low"},
            {"text": "Cyril stupid!", "impact": "low"},
            {"text": "Cyril stupid!", "impact": "low"},
            {"text": "Cyril stupid!", "impact": "low"},
        ]),
        
        # TODO: move these values into data files instead (shouldnt be defined through code)
        "/about": lambda: json.dumps({
            "jnr": {
                "mon": "7:30am - 3:30pm",
                "tue": "7:30am - 3:30pm",
                "wed": "7:30am - 3:30pm",
                "thu": "7:30am - 3:30pm",
                "fri": "7:30am - 3:30pm",
                "max": JNRMAX,
                "librarians": ["Ms Crothers"],
            },
            "snr": {
                "mon": "8:00am - 2:30pm",
                "tue": "8:00am - 2:30pm",
                "wed": "8:00am - 12:30pm",
                "thu": "8:00am - 3:15pm",
                "fri": "8:00am - 2:30pm",
                "max": SNRMAX,
                "librarians": ["Mr Wiramhardja", "Ms Meredith"],
            }
        })
    }
    await websocket.send(options.get(path, lambda:"Could not recognise action")())


def jnr_updater():
    print("Starting jnr_updater")
    # start session with database
    Session = sessionmaker(bind=engine)
    session = Session()

    # create socket and listen
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", JNRCOUNTER_PORT))
    sock.listen(10)
    while True:
        # wait for connection
        client, address = sock.accept()

        # timeout the connection if the client takes to long to send a response
        sock.settimeout(6)

        print(f"Connection from {address[0]} on jnr port")

        # TODO: replace this verification system with SSL
        # create random string of bytes for verification        
        plaintext = bytes([random.randint(0, 0xff) for _ in range(16)])

        # send encrypted verification string
        print("Sending verification string")
        client.send(aesenc.encrypt(plaintext) + b"\n")
        try:
            # receive new string and check if the connecting client can decrypt it
            msg = client.recv(16)
            if msg == KEY:
                print("Verification succeeded")
                while True:
                    # once verification has succeeded, no time limit is required
                    sock.settimeout(None)

                    # receive the update to the number of people in the senior library (+x or -x)
                    print("Recieving message")
                    msg = client.recv(1024)
                    print(msg)
                    inc = eval(msg + b"0") # add a "+0" at the end in case the string has a trailing + or - (due to weird bug where requests get merged)
                    print(inc)

                    # update the count in the senior library
                    session.query(Count).first().jnrvalue += inc
                    session.commit()
                    with open("blehjnr.txt", "a") as f:
                        # if verification is failed, raise an error and let the try/except statement catch it
                        f.write(f"{session.query(Count).first().jnrvalue} {datetime.datetime.now()}\n")
            else:
                raise Exception("Verification failed")
        except Exception as e:
            sock.settimeout(None)
            # print the error (due to verification taking too long, verification being unsuccessful, client closing the connection or some other unknown error
            print(repr(e), "(recieved from jnr port)")
        client.close()


def snr_updater():
    print("Starting snr_updater")
    # start session with database
    Session = sessionmaker(bind=engine)
    session = Session()

    # create socket and listen
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", SNRCOUNTER_PORT))
    sock.listen(10)
    while True:
        # wait for connection
        client, address = sock.accept()

        # timeout the connection if the client takes to long to send a response
        sock.settimeout(6)

        print(f"Connection from {address[0]} on snr port")

        # TODO: replace this verification system with SSL
        # create random string of bytes for verification        
        plaintext = bytes([random.randint(0, 0xff) for _ in range(16)])

        # send encrypted verification string
        print("Sending verification string")
        client.send(aesenc.encrypt(plaintext) + b"\n")
        try:
            # receive new string and check if the connecting client can decrypt it
            msg = client.recv(16)
            if msg == KEY:
                print("Verification succeeded")
                while True:
                    # once verification has succeeded, no time limit is required
                    sock.settimeout(None)

                    # receive the update to the number of people in the senior library (+x or -x)
                    print("Recieving message")
                    msg = client.recv(1024)
                    print(msg)
                    inc = eval(msg + b"0") # add a "+0" at the end in case the string has a trailing + or - (due to weird bug where requests get merged)
                    print(inc)

                    # update the count in the senior library
                    session.query(Count).first().snrvalue += inc
                    session.commit()
                    with open("bleh.txt", "a") as f:
                        # if verification is failed, raise an error and let the try/except statement catch it
                        f.write(f"{session.query(Count).first().snrvalue} {datetime.datetime.now()}\n")
            else:
                raise Exception("Verification failed")
        except Exception as e:
            sock.settimeout(None)
            # print the error (due to verification taking too long, verification being unsuccessful, client closing the connection or some other unknown error
            print(repr(e), "(recieved from snr port)")
        client.close()

# waits until it's 1am
def wait_for_morning():
    # get number of seconds until midnight
    # code from https://stackoverflow.com/questions/45986035/seconds-until-end-of-day-in-python (takes into account daylight savings as well)
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    secs = (datetime.datetime.combine(tomorrow, datetime.time.min) - today).total_seconds()

    # call function that gets predictions after that many seconds
    # threading.Timer(secs, get_new_predictions)
    print("getting new predictions")
    threading.Timer(0, get_new_predictions).start()

# called once every day
def get_new_predictions():
    print("got predictions")
    # start session with database
    Session = sessionmaker(bind=engine)
    session = Session()

    week = 1 # TODO: find way of getting week of term from date
    term = 1 # TODO: find way of getting term today

    # loop through each day of the week and update the predicted value on that day
    for day in range(1, 6):
        predData = getData(term, week, day)
        for i, time in enumerate(times):
            data = session.query(Data).filter_by(day=days[day-1], time=time).first()
            # for now, update with the average of the minumum and maximum
            data.jnr_expected = predData["Jnr"][i]
            data.snr_expected = predData["Snr"][i]

    session.commit()

    # get number of seconds until library opens
    today = datetime.datetime.now()
    opening_hour, opening_minute = getOpeningTime()
    opening = today.replace(hour=opening_hour, minute=opening_minute)
    secs = (opening - today).total_seconds()
    print("opening time:", opening)
    # call function that updates past data every minute
    threading.Timer(secs, update_loop).start()


def update_loop():
    print("entering update loop")
    # start session with database
    Session = sessionmaker(bind=engine)
    session = Session()

    # get information today
    today = datetime.datetime.now()
    term = 1 # TODO: find way of getting week of term from date
    week = 1 # TODO: find way of getting term today

    # add new record to past data
    new_data = PastData(
        day=today.day,
        month=today.month,
        year=today.year,
        term=term,
        week=week,
        time=today.strftime("%H:%M"),
        jnrcount=session.query(Count).first().jnrvalue,
        snrcount=session.query(Count).first().snrvalue
    )
    session.add(new_data)
    session.commit()

    # check if library has closed
    print("getting closing time")
    closing_hour, closing_minute = getClosingTime()
    if today.hour >= closing_hour and today.minute >= closing_minute: # if the library is closed, wait until morning to start loop again
        print("waiting for morning")
        t = threading.Timer(0, wait_for_morning)
    else: # otherwise, run update_loop again after another minute
        print("looping for another  minute")
        today = datetime.datetime.now()
        if today.minute == 59:
            nextTime = today.replace(hour=today.hour + 1, minute=0, second=0)
        else:
            print(today.minute)
            nextTime = today.replace(minute = today.minute + 1, second=0)
        secs = (nextTime - today).total_seconds()
        t = threading.Timer(secs, update_loop)
    t.start()


class Data(Base):
    __tablename__ = "data"

    id = Column(Integer, primary_key=True)
    day = Column(String(10), nullable=False)
    time = Column(String(10), nullable=False)
    jnr_expected = Column(Integer, default=0)
    snr_expected = Column(Integer, default=0)


    @validates("jnr_expected")
    def validate_jnrexpected(self, key, count):
        if count < 0:
            return 0
        return count


    @validates("snr_expected")
    def validate_snrexpected(self, key, count):
        if count < 0:
            return 0
        return count


class Count(Base):
    __tablename__ = "count"

    id = Column(Integer, primary_key=True)
    snrvalue = Column(Integer, default=0)
    jnrvalue = Column(Integer, default=0)


    @validates("snrvalue")
    def valid_snrvalue(self, key, count):
        if count < 0:
            return 0
        return count


    @validates("jnrvalue")
    def valid_jnrvalue(self, key, count):
        if count < 0:
            return 0
        return count


class PastData(Base):
    __tablename__ = "pastdata"

    id = Column(Integer, primary_key=True)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    term = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    time = Column(String(10), nullable=False)
    jnrcount = Column(Integer, nullable=False)
    snrcount = Column(Integer, nullable=False)


def count(lib):
    Session = sessionmaker(bind=engine)
    session = Session()
    if lib == "snr":
        return session.query(Count).first().snrvalue
    else:
        return session.query(Count).first().jnrvalue


def get_trends(lib):
    Session = sessionmaker(bind=engine)
    session = Session()
    trends = {}
    trends["labels"] = times
    trends["data"] = [] 
    for day in days:
        day_trends = []
        for time in times:
            data = session.query(Data).filter_by(day=day, time=time).first()
            if lib == "snr":
                pred = data.snr_expected
            else:
                pred = data.jnr_expected
            day_trends.append(pred)
        trends["data"].append(day_trends)
    return trends

"""
@app.route("/<lib>Events")
def events(lib):
    return None


@app.route("/<lib>PastData")
def pastData(lib):
    return "114"


@app.route("/<lib>Noise")
def noise(lib):
    return "114"


@app.route("/<lib>Scanner")
def scanner(lib):
    return "scan"


@app.route("/<lib>CompUse")
def compUse(lib):
    return "5"


@app.route("/<lib>Money")
def money(lib):
    return "WE ARE NOT CRIMINAKLS!!!!!"
"""

restartdb()

threading.Timer(0, wait_for_morning).start()
"""
threading.Timer(5, plot_data).start()
"""

# TODO: instead of creating a websocket, use socket.io
start_server = websockets.serve(client_help, "0.0.0.0", CLIENT_PORT)

#loop = asyncio.get_event_loop()
#loop.run_until_complete(main())loop.close()
#asyncio.ensure_future(snr_updater())

threading.Thread(target=snr_updater).start()
threading.Thread(target=jnr_updater).start()

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
