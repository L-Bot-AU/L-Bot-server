import json

def callData(term, week, day):
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    f = open("calcData.json")
    calcData = {}
    calcData = json.load(f)
    f.close()
    
    min_year_jnr = calcData["Jnr"]["min_year"]
    max_year_jnr = calcData["Jnr"]["max_year"]
    min_year_snr = calcData["Snr"]["min_year"]
    max_year_snr = calcData["Snr"]["max_year"]

    return_dict = {"Jnr":{}, "Snr":{}}

    for year in range(min_year_jnr,max_year_jnr+1):
        try:
            working = calcData["Jnr"][str(year)]["Term"+str(term)][days[day-1]]
            time_periods = calcData["Jnr"][str(year)]["time_periods"]
            return_dict["Jnr"][year]=[]
            for time_peiod in time_periods:
                prediction = working[str(time_peiod)]["m"]*week + working[str(time_peiod)]["b"]
                return_dict["Jnr"][year].append(prediction)
        except:
            print(year)

    for year in range(min_year_snr,max_year_snr+1):
        try:
            working = calcData["Snr"][str(year)]["Term"+str(term)][days[day-1]]
            time_periods = calcData["Snr"][str(year)]["time_periods"]
            return_dict["Snr"][year]=[]
            for time_peiod in time_periods:
                prediction = working[str(time_peiod)]["m"]*week + working[str(time_peiod)]["b"]
                return_dict["Snr"][year].append(prediction)
        except:
            print(year)
    
    return return_dict

if __name__ == "__main__":
    print(callData(1,1,1))