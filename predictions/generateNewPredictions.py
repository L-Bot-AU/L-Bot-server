import getPastData as get
import calculateNewPredictions as calculate
import writeNewPredictions as write

def generate():
    data = get.getPastData()
    predictions = calculate.genereatePrediction(data)
    write.write(predictions)

    return predictions


if __name__ == "__name__":
    print(generate)
