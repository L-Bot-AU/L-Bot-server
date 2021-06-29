import predictions.predictor as p
import json

def getData(term, week, day):
    """
    :param term: the term (1-4)
    :param week: the week (of each term)
    :param day: the weekday represented as an integer( 1 for Monday)
    :return: an array in the format: `[before school max, before school min, break 1 max, break 1 min, break 2 max, break 2 min]`
    """

    #First trys to get data from file, if not found calls generator function
    #Makes sure bad data is not given (probably not needed)
    if term > 4 or day > 5:
         raise Exception("Data provided out of range")
    dayID = str(term)+'-'+str(week)+'-'+str(day)
    #This will get the data
    return p.callData(term, week, day)

if __name__ == "__main__":
    print(getData(1,1,1))
