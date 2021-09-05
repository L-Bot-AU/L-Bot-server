from constants import TIMES
from database import database
from sqlalchemy.orm import sessionmaker
from flask import send_file, send_from_directory
from datetime import timedelta
import xlsxwriter


def normalise_day(date):
    # Documentation from https://www.dataquest.io/blog/python-datetime-tutorial/
    weekday = date.weekday()
    if weekday > 4:
        date = date - timedelta(3)
    return date


def gen_days(start_date, end_date, data_frequency, mode):
    numDays = (end_date - start_date).days + 1
    print("days:", numDays)
    days = [] # Documentation from https://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
    if mode == "preview":
        if numDays <= 5:
            data_frequency = "period"
            for single_date in (start_date + timedelta(n) for n in range(numDays)):
                for time in TIMES:
                    date_value = (single_date, time)
                    days.append(date_value)
        elif numDays <= 68: # simple way to find term length in days, should edit later on to be more rigorous
            data_frequency = "day"
            for single_date in (start_date + timedelta(n) for n in range(numDays)):
                days.append(single_date)
        else:
            data_frequency = "week"
            start_date = normalise_day(start_date)
            end_date = normalise_day(end_date)
            days = [start_date, end_date]
    return days, data_frequency


def collate_periods(DAYS, lib):
    print("PERIOD")
    dates = []
    values = []
    # connect to database
    Session = sessionmaker(bind=engine)
    session = Session()

    for day in DAYS:
        data = session.query(PastData).filter_by(day=day[0].day, month=day[0].month, year=day[0].year, time=day[1]).first()
        print(data)
        if data is not None:
            print("okay")
            if lib == "Junior":
                pred = data.jnrcount
            elif lib == "Senior":
                pred = data.snrcount
            dates.append(f'{day[1]} {day.day}/{day.month}/{day.year}')
            values.append(pred)
        else:
            print("no datetime?")
            dates.append(f'{day[0].day}/{day[0].month}/{day[0].year}')
            values.append(0)

    return dates, values


def collate_days(DAYS, lib):
    print("DAY")
    dates = []
    values = []
    # connect to database
    Session = sessionmaker(bind=engine)
    session = Session()

    for day in DAYS:
        data = session.query(PastData).filter_by(day=day.day, month=day.month, year=day.year).all()
        dates.append(f'{day.day}/{day.month}/{day.year}')
        if len(data):
            day_values = []
            for time in data:
                if lib == "Junior":
                    pred = time.jnrcount
                elif lib == "Senior":
                    pred = time.snrcount
                day_values.append(pred)
            values.append(sum(day_values)//len(day_values))
        else:
            values.append(0)
    return dates, values


def valid_weeks(week, term, year, end_week, end_term, end_year):
    valid = False
    if year <= end_year:
        if term <= end_term:
            if week <= end_week:
                valid = True
    return valid

def collate_weeks(WEEKS, lib): #will miss a week(s) if start/ end date is a holiday
    print("WEEK")
    dates = []
    values = []
    # connect to database
    Session = sessionmaker(bind=engine)
    session = Session()

    #find first week
    start_week = session.query(PastData).filter_by(day=WEEKS[0].day, month=WEEKS[0].month, year=WEEKS[0].year).first()
    while start_week is None and WEEKS[0] <= WEEKS[1]:
        WEEKS[0] += timedelta(weeks=1)
        start_week = session.query(PastData).filter_by(day=WEEKS[0].day, month=WEEKS[0].month, year=WEEKS[0].year).first()
    if start_week is None:
        print("bad parameters")
        return ["Couldn't find values"], [0]
    week, term, year = start_week.week, start_week.term, start_week.year
    print("start:", week, term, year)

    #find last week
    end_week = session.query(PastData).filter_by(day=WEEKS[1].day, month=WEEKS[1].month, year=WEEKS[1].year).first()
    while end_week is None and WEEKS[0] <= WEEKS[1]:
        WEEKS[1] -= timedelta(weeks=1)
        end_week = session.query(PastData).filter_by(day=WEEKS[1].day, month=WEEKS[1].month, year=WEEKS[1].year).first()
    if end_week is None:
        print("bad parameters")
        return ["Couldn't find values"], [0]
    end_week, end_term, end_year = end_week.week, end_week.term, end_week.year
    print("end:", end_week, end_term, end_year)

    while valid_weeks(week, term, year, end_week, end_term, end_year):
        data = session.query(PastData).filter_by(year=year, term=term, week=week).all()
        if len(data):
            week_values = []
            for time in data:
                if lib == "Junior":
                    pred = time.jnrcount
                elif lib == "Senior":
                    pred = time.snrcount
                week_values.append(pred)
            dates.append(f'Term {term} week {week}, {year}')
            values.append(sum(week_values)//len(week_values))
        else:
            dates.append("No School")
            values.append(0)
        week += 1
        if week > 12:
            week = 1
            term += 1
            if term > 4:
                term = 1
                year += 1

    return dates, values


def get_data(start_date, end_date, data_frequency, lib, mode):
    DAYS, data_frqeuency = gen_days(start_date, end_date, data_frequency, mode)
    data = {
        "dates": [],
        "values": []
    }

    if data_frqeuency == "period":
        data["dates"], data["values"] = collate_periods(DAYS, lib)
    elif data_frqeuency == "day":
        data["dates"], data["values"] = collate_days(DAYS, lib)
    elif data_frqeuency == "week":
        data["dates"], data["values"] = collate_weeks(DAYS, lib)
    print(data)
    return data


def create_excel_spreadsheet(data):
    # All documentaton from https://xlsxwriter.readthedocs.io/

    # .Workbook creates a workbook with given name
    wb = xlsxwriter.Workbook("output.xlsx")
    # .add_worksheet() adds a sheet
    # there's probably an optional argument to name the sheet
    ws = wb.add_worksheet()

    # excel spreadsheets are 0-indexed
    row = 1
    # col = 0

    # Writing: use .write(row, col, value)
    # You can do stuff like .write(row, col, "=SUM(B1:B4)")
    #   i.e. commands u would actually write into the excel text box
    for col, key in enumerate(data.keys()):
        ws.write(0, col, key)

    for col, lst in enumerate(data.values()):
        row = 1
        for val in lst:
            ws.write(row, col, val)
            row += 1
    #    for row, val in enumerate(lst, start=1): #nicer code but uses a temporary variable for row, so it can't be used later in graph.add_series
    #       ws.write(row, col, val)

    # adding a series to a chart:
    # Or using a list of values instead of category/value formulas
    #     [sheetname, first_row, first_col, last_row, last_col]
    """chart.add_series({
        'categories': ['Sheet1', 0, 0, 4, 0], #x-axis values
        'values':     ['Sheet1', 0, 1, 4, 1], #y-axis values
        'line':       {'color': 'red'}, #who knows
    })"""
    graph = wb.add_chart({'type': 'line'})
    graph.add_series({
        'name': "Data",
        'categories': ["Sheet1", 1, 0, len(data["dates"]), 0],
        'values': ['Sheet1', 1, 1, len(data["values"]), 1]
    })

    ws.insert_chart('C1', graph)
    wb.close()

    print("complete")

engine, Base, Data, Count, PastData, LibraryTimes, MaxSeats, Librarians, Events, Alerts = database.genDatabase()