import json

def write(data):
    days = ["Mon","Tue","Wed","Thu","Fri"]
    f = open("calcData.json")
    calcData = {}
    calcData = json.load(f)
    f.close()

    term_base={"Mon":{},"Tue":{},"Wed":{},"Thu":{},"Fri":{}}
    times = data["Times"]

    calcData["Jnr"][data["Year"]] = {}
    calcData["Jnr"][data["Year"]]["time_periods"] = data["Times"]


    #jnr
    calcData["Jnr"][data["Year"]] = {}
    calcData["Jnr"][data["Year"]]["time_periods"] = data["Times"]
    calcData["Jnr"][data["Year"]]["Term"+str(data["Term"])]=term_base
    for day in range(1,6):
        for time in times:
            calcData["Jnr"][data["Year"]]["Term"+str(data["Term"])][days[day-1]][time]={}
            calcData["Jnr"][data["Year"]]["Term"+str(data["Term"])][days[day-1]][time]["b"]=data["Days"][str(day)][time]["Jnr"]
            calcData["Jnr"][data["Year"]]["Term"+str(data["Term"])][days[day-1]][time]["m"]=0

    #snr
    calcData["Snr"][data["Year"]] = {}
    calcData["Snr"][data["Year"]]["time_periods"] = data["Times"]
    calcData["Snr"][data["Year"]]["Term"+str(data["Term"])]=term_base
    for day in range(1,6):
        for time in times:
            calcData["Snr"][data["Year"]]["Term"+str(data["Term"])][days[day-1]][time]={}
            calcData["Snr"][data["Year"]]["Term"+str(data["Term"])][days[day-1]][time]["b"]=data["Days"][str(day)][time]["Jnr"]
            calcData["Snr"][data["Year"]]["Term"+str(data["Term"])][days[day-1]][time]["m"]=0

    print(calcData)
    with open("calcData.json", "w") as f:
        json.dump(calcData, f)

if __name__ == "__main__":
    import getPastData as get
    import calculateNewPredictions as calc

    data = get.getPastData()
    data = calc.generatePrediction(data)
    print(data)
    write(data)