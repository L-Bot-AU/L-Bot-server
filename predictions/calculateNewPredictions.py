def generatePrediction(data):
    for day in range(1,6):
        for time in data["Times"]:
            jnr_calc_list = data["Days"][str(day)][time]["Jnr"]
            snr_calc_list = data["Days"][str(day)][time]["Snr"]
            jnr_average = sum(jnr_calc_list)/len(jnr_calc_list)
            snr_average = sum(snr_calc_list)/len(snr_calc_list)
            data["Days"][str(day)][time]["Jnr"] = jnr_average
            data["Days"][str(day)][time]["Snr"] = snr_average
    return data

if __name__ == "__main__":
    #For testing different imports based on run condition
    
    import getPastData

    data = getPastData.getPastData()
    print(generatePrediction(data))