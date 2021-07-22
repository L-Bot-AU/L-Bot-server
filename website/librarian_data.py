from database import database
from flask import send_file
import xlsxwriter


def get_data(start_date, end_date, data_frequency):
    # connect to database
    # get data straight from database, don't need socket.io
    # []
    data = {"dates": [str(i) + "/7" for i in range(1, 11)],
            "values": [i for i in range(10, 101, 10)]}
    return data


def download_excel_spreadsheet(data):
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

    print("hello?")
    return wb

engine, Base, Data, Count, PastData = database.genDatabase()