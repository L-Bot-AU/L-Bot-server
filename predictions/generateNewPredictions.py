import predictions.getPastData as get
import predictions.calculateNewPredictions as calculate

def generate():
    data = get.getPastData()
    predictions = calculate.genereatePrediction(data)

    return predictions


if __name__ == "__name__":
    print(generate)
