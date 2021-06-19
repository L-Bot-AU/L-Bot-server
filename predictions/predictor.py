import json

def callData(term, week, day):
    min_year_jnr = 2018
    max_year_jnr = 2019
    min_year_snr = 2019
    max_year_snr = 2019

    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    f = open("calcData.json")
    calcData = {}
    calcData = json.load(f)
    f.close()
    
    return_dict = {"Jnr":{}, "Snr":{}}

    jnr_count = 0
    jnr_bs = 0
    jnr_b1 = 0
    jnr_b2 = 0
    for year in range(min_year_jnr,max_year_jnr+1):
        working = calcData["Jnr"][str(year)]["Term"+str(term)][days[day-1]]
        jnr_bs = working["bs"]["m"]*week + working["bs"]["b"]
        jnr_b1 = working["b1"]["m"]*week + working["b1"]["b"]
        jnr_b2 = working["b2"]["m"]*week + working["b2"]["b"]
        jnr_count +=1
        return_dict["Jnr"][year] = [jnr_bs,jnr_b1,jnr_b2]
    # jnr_bs = jnr_bs/jnr_count
    # jnr_b1 = jnr_b1/jnr_count
    # jnr_b2 = jnr_b2/jnr_count

    snr_count = 0
    snr_bs = 0
    snr_b1 = 0
    snr_b2 = 0
    for year in range(min_year_snr,max_year_snr+1):
        working = calcData["Snr"][str(year)]["Term"+str(term)][days[day-1]]
        snr_bs = working["bs"]["m"]*week + working["bs"]["b"]
        snr_b1 = working["b1"]["m"]*week + working["b1"]["b"]
        snr_b2 = working["b2"]["m"]*week + working["b2"]["b"]
        snr_count +=1
        return_dict["Snr"][year] = [snr_bs,snr_b1,snr_b2]
    # snr_bs = snr_bs/snr_count
    # snr_b1 = snr_b1/snr_count
    # snr_b2 = snr_b2/snr_count

    
    return return_dict