# prediction-engine
This is what predicts the fullness of each library at the specific times of the day.

## Currently Implemented
* Junior Library
* Interface for server to get data
* Senior Library
* Testing output

## Useage Instructions
* Place this with the server code and import the file "getData.py"
* addData.cpp requires an external json library which can be found here: https://github.com/nlohmann/json
* Download the single header useage of it, and place that into the appropriate directory.

## Prediction Weighting


|  |  |  |  |  |
|--|--|--|--|--|
| year  | 2018 | 2019 | 2020 | 2021 |
| prediction | 23 | 18 | 43 | 36 |
| weight | 3 | 2 | 0 | 4 | 

From this each prediction will be multiplied by its value and summed

23\*4 + 18\*2 +43\*0 + 36\*4 = 272

This result will be divided by the sum of all the weight values

3 + 2 + 4 = 9

272/9 = 30.22

Therefore the predicted value will be 30
