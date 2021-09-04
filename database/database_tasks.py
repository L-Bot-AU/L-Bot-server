from constants import DO_RESTARTDB, DATABASE_TASKS_TIMEOUT
from database import database
from predictions.getData import getData
from constants import DAYS, TIMES, OPENING_TIMES, CLOSING_TIMES, MAX_CAPS, LIBRARIANS
from sqlalchemy.orm import sessionmaker
import datetime
import os
import time


engine, Base, Data, Count, PastData, LibraryTimes, MaxSeats, Librarians, Events, Alerts = database.genDatabase()
if DO_RESTARTDB:
    # restarts the database with new values (default, hard-coded ones). not recommended for production since all information is lost
    # remove the database file if it exists
    try:
        os.remove("library_usage.db")
    except FileNotFoundError:
        pass
        
    # create opening session
    Session = sessionmaker(bind=engine)
    begsession = Session()

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    
    # loop through each time of each day and add a data record for it (the predicted usage for that day and time)
    for day in DAYS:
        for t in TIMES:
            predictedUsage = Data(day=day, time=t)
            begsession.add(predictedUsage)
       
    # add a count record representing the occupancy of each library (set to 0)
    begsession.add(Count())
    
    # loop through each day and library and set the opening/closing times as the hard-coded values
    for day in DAYS:
        for library in ["jnr", "snr"]:
            openinghour, openingminute = OPENING_TIMES[library][day]
            closinghour, closingminute = CLOSING_TIMES[library][day]
            newTimes = LibraryTimes(
                library=library,
                day=day,
                openinghour=openinghour,
                openingminute=openingminute,
                closinghour=closinghour,
                closingminute=closingminute
            )
            begsession.add(newTimes)
    
    # set the maximum capacity of each library to the hard-coded value (counted on the 2nd of February 2021 and the 5th of February 2021 for the junior and senior libraries respectively)
    begsession.add(MaxSeats(library="jnr", seats=MAX_CAPS["jnr"]))
    begsession.add(MaxSeats(library="snr", seats=MAX_CAPS["snr"]))
    
    # loop through each librarian's name and create a record of it
    for library in ["jnr", "snr"]:
        for name in LIBRARIANS[library]:
            librarian = Librarians(
                library=library,
                name=name
            )
            begsession.add(librarian)
    
    # commit the session to the database
    begsession.commit()

def secsUntilNextDay():
    # get number of seconds until midnight
    # code from https://stackoverflow.com/questions/45986035/seconds-until-end-of-day-in-python (takes into account daylight savings as well)
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    secs = (datetime.datetime.combine(tomorrow, datetime.time.min) - today).total_seconds()
    return secs

def getOpeningTime(): # TODO: currently a stub
    """return the opening time of the library for today, as a datetime object"""
    return datetime.datetime.now()

def getClosingTime(): # TODO: currently a stub
    """return the closing time of the library for today, as a datetime object"""
    return datetime.datetime.max # haha it never closes

def libraryOpen(): # TODO: currently a stub
    return getOpeningTime() <= datetime.datetime.now() <= getClosingTime()

def get_new_predictions():
    """called once every day"""
    # start session with database
    Session = sessionmaker(bind=engine)
    session = Session()

    week = 1 # TODO: find way of getting week of term from date
    term = 1 # TODO: find way of getting term today

    # loop through each day of the week and update the predicted value on that day
    for day in range(1, 6):
        predData = getData(term, week, day)
        for i, time in enumerate(TIMES):
            data = session.query(Data).filter_by(day=DAYS[day-1], time=time).first()
            # for now, update with the average of the minumum and maximum
            data.jnr_expected = predData["Jnr"][i]
            data.snr_expected = predData["Snr"][i]

    session.commit()

def update_loop():
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

print(__name__, "Reset database")
while True:
    # waits until it's 1am
    #time.sleep(secsUntilNextDay())
    
    print(__name__, "Getting new predictions")
    get_new_predictions()
    
    # wait until the library is open
    secsUntilOpening = (getOpeningTime() - datetime.datetime.now()).total_seconds()
    time.sleep(max(0, secsUntilOpening))
    
    while libraryOpen():
        print(__name__, "Entering update loop")
        update_loop()
        
        time.sleep(DATABASE_TASKS_TIMEOUT)

