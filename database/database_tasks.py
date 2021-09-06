from constants import DO_RESTARTDB, DATABASE_TASKS_TIMEOUT
from database import database
from predictions.getData import getData
from constants import DAYS, TIMES, OPENING_TIMES, CLOSING_TIMES, MAX_CAPS, LIBRARIANS
from sqlalchemy.orm import sessionmaker
import datetime
import os
import csv
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
    # get number of seconds until midnight for next school day
    today = datetime.datetime.now()
    public_holidays = []
    term_dates = []
    with open("school_day.csv", newline="") as g:
        next(g)
        reader = csv.reader(g,delimiter=',',
                                quotechar='|') # initialise csv reader

        term_dates = [list(map(lambda x:datetime.datetime.strptime(x, "%d-%m-%Y"), [start_date, end_date])) for start_date, end_date in reader]

    with open("public_holiday.csv", newline="") as g:
        next(g)
        reader = csv.reader(g,delimiter=',',
                                quotechar='|') # initialise csv reader

        public_holidays = [datetime.datetime.strptime(date, "%d-%m-%Y") for date, _ in reader]

    tIndex = 0
    hIndex = 0
    # binary search for the last starting term date
    r = len(term_dates)
    while tIndex < r:
        m = (tIndex + r) // 2
        if term_dates[m][0] < today:
            tIndex = m + 1
        else:
            r = m

    # binary search for the last holiday
    r = len(public_holidays)
    while hIndex < r:
        m = (hIndex + r) // 2
        if public_holidays[m] < today:
            hIndex = m + 1
        else:
            r = m

    # increment to find the next holiday coming up
    hIndex += 1

    # get date of tomorrow midnight. code from https://stackoverflow.com/questions/45986035/seconds-until-end-of-day-in-python (takes into account daylight savings as well)
    tomorrow = today + datetime.timedelta(days=1)
    tomorrow = datetime.datetime.combine(tomorrow, datetime.time.min)

    # repeatedly move up a term (if we are currently in the holidays) or a day (if we are on a holiday) until
    found = False
    nextDay = today + datetime.timedelta(days=1)
    while not found:
        if term_dates[tIndex][1] < nextDay:
            tIndex += 1
            nextDay = term_dates[tIndex][1]
            while public_holidays[hIndex] < nextDay:
                hIndex += 1
        elif public_holidays[hIndex] == nextDay:
            nextDay += datetime.timedelta(days=1)
            hIndex += 1
        elif nextDay.weekday() >= 5:
            nextDay += datetime.timedelta(days=1)
        else:
            found = True

    # return total number of seconds between now and the next day (not using today since time may have elapsed during processing)
    return (datetime.datetime.combine(nextDay, datetime.time.min) - datetime.datetime.now()).total_seconds()

def getWeekAndTerm():
    today = datetime.datetime.now()
    term = 1
    with open("school_day.csv", newline="") as f:
        next(f)
        reader = csv.reader(f,delimiter=',',
                                quotechar='|') # initialise csv reader

        for start_date, end_date in reader: # loop through the start and end dates of each term
            if start_date[-2:] == str(today.year)[-2:]: # check only term dates for the current year
                start_date = datetime.datetime.strptime(start_date, "%d-%m-%Y")
                end_date = datetime.datetime.strptime(end_date, "%d-%m-%Y")
                if start_date <= today <= end_date: # if the current date is now in the term we are checking
                    break
                term += 1 # increment to represent the next term

        print(today, start_date)
        week = (today - start_date).days // 7 + 1
    return week, term

def getOpeningTime():
    """return the opening time of the library for today, as a datetime object"""
    return datetime.datetime.now().replace(hour=7, minute=30)

def getClosingTime():
    """return the closing time of the library for today, as a datetime object"""
    return datetime.datetime.now().replace(hour=15, minute=30)

def libraryOpen():

    return getOpeningTime() <= datetime.datetime.now() <= getClosingTime()

def get_new_predictions():
    """called once every day"""
    # start session with database
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # get week and term today
    week, term = getWeekAndTerm()

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

    # get week and term today
    today = datetime.datetime.now()
    week, term = getWeekAndTerm()

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
    print(secsUntilNextDay())
    time.sleep(secsUntilNextDay())
    
    print(__name__, "Getting new predictions")
    get_new_predictions()
    
    # wait until the library is open
    secsUntilOpening = (getOpeningTime() - datetime.datetime.now()).total_seconds()
    print(secsUntilOpening)
    time.sleep(max(0, secsUntilOpening))
    
    while libraryOpen():
        print(__name__, "Entering update loop")
        update_loop()
        
        time.sleep(DATABASE_TASKS_TIMEOUT)

