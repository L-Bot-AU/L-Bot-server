from constants import DO_RESTARTDB, DATABASE_TASKS_TIMEOUT
from database import database
from predictions.getData import getData
from constants import DAYS, TIMES, OPENING_TIMES, CLOSING_TIMES, MAX_CAPS, LIBRARIANS
from sqlalchemy.orm import sessionmaker
import datetime
import os
import csv
import time
from loguru import logger

engine, Base, Data, Count, PastData, LibraryTimes, MaxSeats, Librarians, Events, Alerts = database.genDatabase()
# if a constant is set, restart the database with default, hard-coded values.
# Not recommended for productions since this overrwrites all changes and data collected
if DO_RESTARTDB:
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
    """
    Gets the number of seconds until midnight for the next school day

    :return: The number of seconds until 12:00am on the next school day
    """

    today = datetime.datetime.now()
    public_holidays = []
    term_dates = []

    # Read through the CSV file and collect all starting and ending term dates
    with open("school_day.csv", newline="") as g:
        next(g) # ignores the first line, which is the initialising variables of the CSV
        reader = csv.reader(g,delimiter=',',
                                quotechar='|') # initialise csv reader

        term_dates = [list(map(lambda x:datetime.datetime.strptime(x, "%d-%m-%Y"), [start_date, end_date])) for start_date, end_date in reader]

    # Read through the CSV file and collect all public holiday dates (ignore significance in the second column)
    with open("public_holiday.csv", newline="") as g:
        next(g) # ignores the first line, which is the initialising variables of the CSV
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
        if term_dates[tIndex][1] < nextDay: # if we are not in a term i.e. in holidays
            tIndex += 1
            nextDay = term_dates[tIndex][1]
            while public_holidays[hIndex] < nextDay: # move the hIndex up (represents next holiday)
                hIndex += 1
        elif public_holidays[hIndex] == nextDay: # if we are in a public holiday
            nextDay += datetime.timedelta(days=1)
            hIndex += 1
        elif nextDay.weekday() >= 5: # if we are in the weekends
            nextDay += datetime.timedelta(days=1)
        else:
            found = True
            while public_holidays[hIndex] < nextDay: # move the hIndex up (represents next holiday)
                hIndex += 1

    # return total number of seconds between now and the next day (not using today since time may have elapsed during processing)
    return (datetime.datetime.combine(nextDay, datetime.time.min) - datetime.datetime.now()).total_seconds()

def getWeekAndTerm():
    """
    Returns the school week and term of the current day

    :return: a tuple with the first value being the week and the second being the term
    """

    today = datetime.datetime.now()
    term = 1
    with open("school_day.csv", newline="") as f:
        next(f)
        reader = csv.reader(f,delimiter=',',
                                quotechar='|') # initialise csv reader

        # loop through the start and end dates of each term
        for start_date, end_date in reader:
            if start_date[-2:] == str(today.year)[-2:]: # check only term dates for the current year
                start_date = datetime.datetime.strptime(start_date, "%d-%m-%Y")
                end_date = datetime.datetime.strptime(end_date, "%d-%m-%Y")
                if start_date <= today <= end_date: # if the current date is now in the term we are checking
                    break
                term += 1 # increment to represent the next term

        # get the number of days since the start of the term and use it to calculate the current week
        week = (today - start_date).days // 7 + 1
    return week, term

def getOpeningTime():
    """
    Returns the opening time of the library for today

    :return: A datetime object representing both libraries' opening time today
    """

    return datetime.datetime.now().replace(hour=7, minute=30)

def getClosingTime():
    """
    Returns the closing time of the library for today

    :return: A datetime object representing both libraries' closing time today
    """

    return datetime.datetime.now().replace(hour=15, minute=30)

def libraryOpen():
    """
    Returns whether or not the libraries are currently open

    :return: A boolean value - True if both libraries are open, False if not
    """
    return getOpeningTime() <= datetime.datetime.now() <= getClosingTime()

def get_new_predictions():
    """
    Generates new predicted occupancies of the libraries and stores them in the database
    
    :return:
    """

    Session = sessionmaker(bind=engine)
    session = Session()
    
    # get week and term today
    week, term = getWeekAndTerm()

    # loop through each day of the week and update the predicted value on that day
    for day in range(1, 6):
        predData = getData(term, week, day)
        for i, time in enumerate(TIMES):
            # Get the expected usage record for the provided day and time
            data = session.query(Data).filter_by(day=DAYS[day-1], time=time).first()

            # Update the expected occupancy with the new value
            data.jnr_expected = predData["Jnr"][i]
            data.snr_expected = predData["Snr"][i]

    session.commit()

def update_loop():
    """
    Records the current occupancy of the library as a new record (called every minute)

    :return:
    """

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

logger.info("Reset database")
while True:
    # waits until it's 1am
    time.sleep(secsUntilNextDay())
    
    # get new predictions
    logger.info("Getting new predictions")
    get_new_predictions()
    
    # wait until the library is open
    secsUntilOpening = (getOpeningTime() - datetime.datetime.now()).total_seconds()
    time.sleep(max(0, secsUntilOpening))
    
    # while the library is open, record the occupancy every minute
    while libraryOpen():
        logger.info("Entering update loop")
        update_loop()
        
        time.sleep(DATABASE_TASKS_TIMEOUT)

