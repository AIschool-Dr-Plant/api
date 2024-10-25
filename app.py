from flask import Flask, jsonify, render_template, request, redirect, url_for
from module.db_module import Database  # 모듈 import
from datetime import datetime

import pandas as pd
import os





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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
