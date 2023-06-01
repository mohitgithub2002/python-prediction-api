from flask import Flask,jsonify, render_template, request, redirect
from pymongo import MongoClient
import time
from keras.models import load_model
import requests
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from flask_cors import CORS, cross_origin
import json

app = Flask(__name__)
cors = CORS(app)



cross_origin(
origins = '*',
methods = ['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT']
)



# MongoDB connection
client = MongoClient('mongodb+srv://rahul:rahul@cluster0.r1xuwdr.mongodb.net/')
db = client['text_db']
collection = db['text_collection']



### fit transfer the scaler
df_d = pd.read_csv("data.csv", index_col="datetime")
scaler2 = MinMaxScaler(feature_range=(0,1))
df_d = scaler2.fit_transform(np.array(df_d).reshape(-1,1))
modll = load_model("BTC_Model.h5")


## fetch data from mongo
x = list(db.graph.find())
DateTime = []
Actual = []
Train = []
Test = []
for i in x:
  DateTime.append(i["DateTime"])
  Actual.append(i["Actual"])
  Train.append(i["Train"])
  Test.append(i["Test"])
  
# def getLast5DaysData():
    
 
  
@app.route('/last5days', methods=['GET'])
def last5days():
    try:
        from_symbol = 'BTC'
        to_symbol = 'USD'
        exchange = 'Bitstamp'
        url = "https://min-api.cryptocompare.com/data/histoday"
        params = {'fsym': from_symbol, 'tsym': to_symbol,
                    'limit': 2000, 'aggregate': 1,
                    'e': exchange}
        request = requests.get(url, params=params)
        data = request.json()
        d = {}
        for x in range(5):
            d[x] = data['Data'][-5:][x]['high']
        print("data is : ", d)
        # data['Data'][0]['high'], data['Data'][1]['high'], data['Data'][2]['high'], data['Data'][3]['high'], data['Data'][4]['high'], data['Data'][5]['high']
        return jsonify({"status" : True,"error" : "", "data": d})
    except Exception as e:
        return jsonify({"status" : False,"error" : "Internal server error: {e}"})
        


@app.route('/graph-list', methods=['GET'])
def graph_list():
    try:
        return jsonify({"Date": DateTime, "Actual": Actual, "Train": Train, "Test": Test})
    except:
        return jsonify({"status" : False,"error" : "Internal server error"})




@app.route('/register1', methods=['POST'])
def register1():
    try:
        wallet = request.form['wallet']
        user  = collection.find_one({'wallet': wallet, 'status1': True})
        if not user:
            collection.insert_one({'wallet': wallet, 'status1': True, 'created_at_1': int(time.time())})
            return jsonify({"status" : True,"error" : None})
        else:
            return jsonify({ "status" : False, "error" : "Already burn"})
    except:
        return jsonify({"status" : False,"error" : "Internal server error"})



@app.route('/register2', methods=['POST'])
def register2():
    try:
        wallet = request.form['wallet']
        user  = collection.find_one({'wallet': wallet, 'status2': True})
        if not user:
            collection.insert_one({'wallet': wallet, 'status2': True, 'created_at_2': int(time.time())})
            return jsonify({"status" : True,"error" : None})
        else:
            return jsonify({ "status" : False, "error" : "Already burn"})
    except:
        return jsonify({"status" : False,"error" : "Internal server error"})
        


@app.route('/check_user/<wallet>')
def check_user(wallet):
    try:
        user = collection.find_one({'wallet': wallet})
        if user:
            print("IF Called")
            status1 = False
            status2 = False
            if (collection.find_one({'wallet': wallet, "status1" : True})):
                status1 = True
            if (collection.find_one({'wallet': wallet, "status2" : True})):
                status2 = True
            
            return jsonify({ "status" : True, "error" : None, "data": {"status1" : status1, "status2": status2}})
        else:
            print("Else Called")
            return jsonify({ "status" : True, "error" : None, "data": {"status1" : False, "status2": False}})
    except:
        return jsonify({"status" : False,"error" : "Internal server error"})
        


@app.route('/next/', methods=['GET'])
@cross_origin()
def getnext():
    try:
      
#         d1 = float(request.args.get("d1"))
#         d2 = float(request.args.get("d2"))
#         d3 = float(request.args.get("d3"))
#         d4 = float(request.args.get("d4"))
#         d5 = float(request.args.get("d5"))
        from_symbol = 'BTC'
        to_symbol = 'USD'
        exchange = 'Bitstamp'
        url = "https://min-api.cryptocompare.com/data/histoday"
        params = {'fsym': from_symbol, 'tsym': to_symbol,
                    'limit': 2000, 'aggregate': 1,
                    'e': exchange}
        request = requests.get(url, params=params)
        data = request.json()
        d1 = data['Data'][-5:][0]['high']
        d2 = data['Data'][-5:][1]['high']
        d3 = data['Data'][-5:][2]['high']
        d4 = data['Data'][-5:][3]['high']
        d5 = data['Data'][-5:][4]['high']
        print(d1, d2, d3, d4, d5)
            
        x = np.array([[d1, d2, d3, d4, d5]]).reshape(-1,1)
        x = scaler2.transform(x)
        x = (np.array(x))
        x = x[:,np.newaxis]
        x = x.reshape(1,5,1)
        output = scaler2.inverse_transform(modll.predict(x))
        print("Output is : ",float(output.flatten()[0]), type(output.flatten()))
        # return str(float(output.flatten()[0]))
        
        return jsonify({"status" : True,"error" : "", "data":float(output.flatten()[0])})
    except Exception as e:
        print("Exception : ",e)
        return jsonify({"status" : False,"error" : "Internal server error", "data":""})

@app.route('/next-10/', methods=['GET'])
@cross_origin()
def getnext_10():
    try:
        from_symbol = 'BTC'
        to_symbol = 'USD'
        exchange = 'Bitstamp'
        url = "https://min-api.cryptocompare.com/data/histoday"
        params = {'fsym': from_symbol, 'tsym': to_symbol,
                    'limit': 2000, 'aggregate': 1,
                    'e': exchange}
        request = requests.get(url, params=params)
        data = request.json()
        d1 = data['Data'][-5:][0]['high']
        d2 = data['Data'][-5:][1]['high']
        d3 = data['Data'][-5:][2]['high']
        d4 = data['Data'][-5:][3]['high']
        d5 = data['Data'][-5:][4]['high']
        print(d1, d2, d3, d4, d5)
        
        x = np.array([d1,d2,d3,d4,d5]).reshape(-1,1)
        x_input =  scaler2.transform(x) 
        temp_input = list(x_input.flatten())
        lst_output=[]
        n_steps=5
        i=0
        while(i<10):
            if(len(temp_input)>5):
                #print(temp_input)
                x_input=np.array(temp_input[1:])
                x_input=x_input.reshape(1,-1)
                x_input = x_input.reshape((1, n_steps, 1))
                #print(x_input)
                yhat = modll.predict(x_input, verbose=0)
                # print("{} day output {}".format(i,yhat))
                temp_input.extend(yhat[0].tolist())
                temp_input=temp_input[1:]
                #print(temp_input)
                lst_output.extend(yhat.tolist())
                i=i+1
            else:
                x_input = x_input.reshape((1, n_steps,1))
                yhat = modll.predict(x_input, verbose=0)
                # print(yhat[0])
                temp_input.extend(yhat[0].tolist())
                # print(len(temp_input))
                lst_output.extend(yhat.tolist())
                i=i+1
        output = scaler2.inverse_transform(lst_output)
        print(output)
        print("Output is : ",float(output.flatten()[0]), type(output.flatten()))
        d = {}
        for x in range(10):
            d[x] = float(output.flatten()[x])
        print("D is : ", d)
        return jsonify({"status" : True,"error" : None, "data":d})
    except Exception as e:
        print("e : ", e)
        return jsonify({"status" : False,"error" : "Internal server error", "data":""})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
