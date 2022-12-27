import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
import pickle
import datetime
import os


class Logger:
    def __init__(self):
        pass

    # Obtain date and time in the given format and log the message in the opened file
    def log(self, log_message):
        self.now = datetime.datetime.now()
        self.date = self.now.date()
        self.current_time = self.now.strftime("%H:%M:%S")
        self.file_object = open('Logs/logs.txt', 'a+')
        self.file_object.write(str(self.date) + "/" + str(self.current_time) + "\t\t" + log_message + "\n")


log = Logger()

app = Flask(__name__)

try:
    log.log('Loading model...')

    with open('Model/xgb_model.sav', 'rb') as f:
        model = pickle.load(f)
        feature_names = model.get_booster().feature_names

    log.log('Model loaded successfully')
except Exception as e:
    log.log('Error: ' + str(e))

try:
    log.log('Loading scalar')

    with open('Std_scalar/std_scalar.pkl', 'rb') as f:
        std_scalar = pickle.load(f)

    log.log('Scalar loaded sucessfully')
except Exception as e:
    log.log('Error: ' + str(e))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    '''
    for rendering results on HTML
    '''
    try:
        log.log('Expecting input')

        features = [int(x) for x in request.form.values()]

        log.log('Valid input received')
    except Exception as e:
        log.log('Error: ' + str(e))
        return str(e)

    try:
        # re-arranging the list as per data set
        log.log('Rearranging features')

        feature_list = [features[4]] + features[:4] + features[5:11][::-1] + features[11:17][::-1] + features[17:][::-1]
        features_arr = np.array(feature_list).reshape(1, -1)

        log.log('Rearranging sucessful' + '\t' + str(features_arr))
    except Exception as e:
        log.log('Error: ' + str(e))
        return str(e)

    try:
        log.log('Scaling the input')

        scaled_arr = std_scalar.transform(features_arr)

        log.log('Input scaled:')

    except Exception as e:
        log.log('Error: ' + str(e))
        return str(e)

    try:
        log.log('Generating input')

        input = pd.DataFrame(list(scaled_arr), columns=feature_names)

        log.log('Input generated successfully')

    except Exception as e:
        log.log('Error: ' + str(e))
        return str(e)

    try:
        log.log('Prediction started')

        prediction = model.predict(input)

        log.log('Prediction successful:' + '\t' + str(scaled_arr) + '\t' + str(prediction))

    except Exception as e:
        log.log('Error: ' + str(e))
        return str(e)

    result = ""
    if prediction == 1:
        result = "DEFAULT ALERT: Credit Card holder will default on next month payment"
    else:
        result = "NO DEAULT: Credit Card holder will not default on next month payment"

    return render_template('index.html', prediction_text=result)


if __name__ == "__main__":
    app.run(port=8088, debug=True)