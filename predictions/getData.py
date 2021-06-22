import predictor
import json

time_interval_count = 3

def getData(term, week, day):
    """
    :param term: the term (1-4)
    :param week: the week (of each term)
    :param day: the weekday represented as an integer( 1 for Monday)
    :return: an array in the format: `[before school , break 1, break 2]`
    """

    #Makes sure bad data is not given (probably not needed)
    if term > 4 or day > 5 or week > 13:
         raise Exception("Data provided out of range")
    
    #Obtains prediction
    prediction = predictor.callData(term, week, day)
    prediction = weightData(prediction)
    return prediction

def weightData(initial_prediction):
     # Weights previous years data based on relevance to current year to improve accuracy of prediction
     # Example
     # For T3 W3 Mon Lunch
     #  ________________________________________
     # | year       | 2018 | 2019 | 2020 | 2021 |
     # | prediction |  23  |  18  |  43  |  36  |
     # | weight     |  3   |  2   |  0   |  4   |
     # |________________________________________|
     # From there each prediction will be multiplied by its weight value and summed
     # 23*4 + 18*2 + 43*0 + 36*4 = 272
     # This result will be divided by the summ of all the weight values
     # 3 + 2 + 4 = 9
     # 272/9 = 30.22 
     # Therefore predicted value will be 30

     new = {"Jnr":[0,0,0], "Snr":[0,0,0]}

     #Jnr
     weights = getWeights("Jnr")
     count = 0
     #Sums up each (weight*year) for each time period
     for year in weights:
          for i in range(0,time_interval_count):
               new["Jnr"][i] += initial_prediction["Jnr"][year][i]*weights[year]
          count += weights[year]

     #Divides each summed value for each time period
     for i in range(0,time_interval_count-1):
               new["Jnr"][i] = round((new["Jnr"][i]/count))

     #Snr
     weights = getWeights("Snr")
     count = 0
     #Sums up each (weight*year) for each time period
     for year in weights:
          for i in range(0,time_interval_count):
               new["Snr"][i] += initial_prediction["Snr"][year][i]*weights[year]
          count += weights[year]

     #Divides each summed value for each time period
     for i in range(0,time_interval_count-1):
               new["Snr"][i] = round((new["Snr"][i]/count))

     return new


#Stub
def getWeights(library):
     if library == "Jnr":
          return {2018:1,2019:1}
     elif library == "Snr":
          return {2019:1}
     else:
          raise Exception("Incorrect library provided")
