from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_cors import CORS
from module.db_module import Database  # 모듈 import
from datetime import datetime, timedelta
from module.pear_infection_model import DiseasePredictionModel

import json
import pandas as pd
import os




infectionModel = DiseasePredictionModel();

# CSV 파일의 경로 설정
csv_path = os.path.join(os.path.dirname(__file__), 'module', 'sensor_data_key.csv')

# CSV 파일을 읽고 JSON 응답 생성
df = pd.read_csv(csv_path)  # Pandas로 CSV 읽기

sensor_key_dict = dict(zip(df['COLUMN'], df['KEY']))

def sensor_data_parse(data):
    query_string = "INSERT INTO SNSR_DATA_TB("+",".join(sensor_key_dict.keys())+",REG_ID) VALUES('" +"','".join(data.values()) + "','SYSTEM');"
    print(query_string)
    db.execute_commit(query_string)
    result = db.execute_query("SELECT * FROM SNSR_DATA_TB")
    print(result)
    # print(query_string)
    return result  # DataFrame을 딕셔너리 리스트로 변환

#Database 객체 생성
db = Database()

app = Flask(__name__)

CORS(app, resources={
    r"/api/data": {"origins": "*"},
    r"/api/predict":{"origins": "https://localhost:8443"}
})

# Load environment variables from .env
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def api_data():
    # 쿼리 파라미터를 딕셔너리 형태로 변환
    data = dict(request.args)
    # JSON 응답으로 반환
    return jsonify({"response": "Received", "data": data})

@app.route('/api/test', methods=['GET'])
def api_test():
    # 쿼리 파라미터를 딕셔너리 형태로 변환
    # data = sensor_data_parse(dict(request.args))
    
    # JSON 응답으로 반환
    json_data = sensor_data_parse(dict(request.args))
    return render_template('sensor_data.html', data=json_data)

@app.route('/api/predict',methods=['POST'])
def predict():
    data = dict(request.get_json());
    # 기본값은 오늘 날짜로 설정
    date_obj = datetime.today()

    # 'date' 키가 있는 경우 처리
    if 'date' in data:
        try:
            # 'date' 값을 날짜 형식으로 변환 시도
            date_obj = datetime.strptime(data['date'], '%Y-%m-%d')
            after_1 = date_obj + timedelta(days=1)
            after_2 = after_1 + timedelta(days=1)
            after_3 = after_2 + timedelta(days=1)
        except (ValueError, TypeError):
            # 날짜 형식이 비정상적인 경우 오늘 날짜를 유지
            pass
    #sampleData
    rain_predict = {
        "target_date":{"date":date_obj,"rp":1,"temp":26.12},
        "after_1":{"date":after_1,"rp":0,"temp":17.58},
        "after_2":{"date":after_2,"rp":1,"temp":10.17},
        "after_3":{"date":after_3,"rp":0,"temp":36.86},
    }
    result=[]
    for item in rain_predict:
        infect_predict = infectionModel.predict_infection_rates(rain_predict[item])
        temp_data = dict({'date':rain_predict[item]['date'].strftime('%Y-%m-%d'),'rain':rain_predict[item]['rp'],'predict':infect_predict})
        result.append(temp_data)
    # 유효한 날짜를 반환
    return jsonify(result),200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
