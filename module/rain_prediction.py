import pymysql
import pandas as pd
import numpy as np
import json
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import os

class RainPrediction:
    # JSON 파일에서 DB 연결 설정 로드
    with open(os.path.join(os.path.dirname(__file__), 'db_config.json'), 'r') as file:
        DB_CONFIG = json.load(file)
    
    def __init__(self):
        self.data = None
        self.data2 = None
        self.model_1 = RandomForestRegressor(random_state=42, n_estimators=100)
        self.model_2 = RandomForestRegressor(random_state=42, n_estimators=100)
        self.model_3 = RandomForestRegressor(random_state=42, n_estimators=100)
        
    def load_data(self, date):
        conn = pymysql.connect(**self.DB_CONFIG)
        try:
            print(date,type(date))
            self.data = pd.read_sql('SELECT * FROM NAJU_WEATHER_TB', conn)
            
            self.data2 = pd.read_sql('SELECT CAST(MEAS_DT AS DATE) AS MEAS_DT, ROUND(AVG(AP), 2) AS AP, ROUND(AVG(HUM), 2) AS HUM, ROUND(AVG(TEMP), 2) AS TEMP, ROUND(AVG(WS), 2) AS WS, ROUND(AVG(WD), 2) AS WD, ROUND(AVG(RF), 2) AS RF FROM NAJU_WEATHER_TB GROUP BY CAST(MEAS_DT AS DATE) HAVING MEAS_DT = %s', conn, params=[date])
        finally:
            conn.close()

        
    def preprocess_data(self):
        hour_day = 24
        self.data[['RF', 'HUM']] = self.data[['RF', 'HUM']].astype('float')
        self.data2[['RF', 'HUM']] = self.data2[['RF', 'HUM']].astype('float')
        self.data['RFp'] = np.where((self.data['RF'] > 1) & (self.data['HUM'] > 90), 1, 0)
        self.data2['RFp'] = np.where((self.data2['RF'] > 1) & (self.data2['HUM'] > 90), 1, 0).astype("int")

        self.data['MEAS_DT'] = pd.to_datetime(self.data['MEAS_DT'])
        self.data = self.data.sort_values('MEAS_DT')

        for idx in range(3):
            i = idx + 1
            self.data[f'AP_{i}'] = self.data['AP'].shift(-hour_day * i)
            self.data[f'TEMP_{i}'] = self.data['TEMP'].shift(-hour_day * i)
            self.data[f'HUM_{i}'] = self.data['HUM'].shift(-hour_day * i)
            self.data[f'WS_{i}'] = self.data['WS'].shift(-hour_day * i)
            self.data[f'WD_{i}'] = self.data['WD'].shift(-hour_day * i)
            self.data[f'RF_{i}'] = self.data['RF'].shift(-hour_day * i)
            self.data[f'RFp_{i}'] = self.data['RFp'].shift(-hour_day * i)
        
        self.data = self.data.dropna()
        self.data2 = self.data2.dropna()
        
    def train_models(self):
        lable_target_index = [['AP', 'HUM', 'TEMP', 'WS', 'WD', 'RF', 'RFp']]
        
        for idx in range(3):
            lable_arr = []
            for item in lable_target_index[0]:
                lable_arr.append(f'{item}_{idx + 1}')
            lable_target_index.append(lable_arr)
        
        X = self.data[lable_target_index[0]]
        y_1 = self.data[lable_target_index[1]]
        y_2 = self.data[lable_target_index[2]]
        y_3 = self.data[lable_target_index[3]]
        
        self.model_1.fit(X, y_1)
        self.model_2.fit(X, y_2)
        self.model_3.fit(X, y_3)
        
    def predict(self):
        test_X = self.data2[['AP', 'HUM', 'TEMP', 'WS', 'WD', 'RF', 'RFp']]
        last_meas_date = self.data2['MEAS_DT'].iloc[0]
    
        # 예측 수행
        predicted_1 = self.model_1.predict(test_X)
        predicted_2 = self.model_2.predict(test_X)
        predicted_3 = self.model_3.predict(test_X)
    
        # 강우 1mm 이하 처리
        predicted_1[0][5] = predicted_1[0][5] if predicted_1[0][5] > 1 else 0
        predicted_2[0][5] = predicted_2[0][5] if predicted_2[0][5] > 1 else 0
        predicted_3[0][5] = predicted_3[0][5] if predicted_3[0][5] > 1 else 0
    
        # 예측 날짜 계산
        after_1 = (last_meas_date + timedelta(days=1)).strftime("%Y-%m-%d")
        after_2 = (last_meas_date + timedelta(days=2)).strftime("%Y-%m-%d")
        after_3 = (last_meas_date + timedelta(days=3)).strftime("%Y-%m-%d")
    
        # 예측 결과 출력
        rain_predict = {
            "target_date": {
                "date": last_meas_date.strftime("%Y-%m-%d"),
                "rp": bool(self.data2['RFp'].iloc[0]),
                "temp": self.data2["TEMP"].iloc[0]
            },
            "after_1": {
                "date": after_1,
                "rp": bool(predicted_1[0][5]),
                "temp": float(round(predicted_1[0][2], 2))
            },
            "after_2": {
                "date": after_2,
                "rp": bool(predicted_2[0][5]),
                "temp": float(round(predicted_2[0][2], 2))
            },
            "after_3": {
                "date": after_3,
                "rp": bool(predicted_3[0][5]),
                "temp": float(round(predicted_3[0][2], 2))
            }
        }
        
        return rain_predict


# 외부에서 호출할 함수
def get_rain_predictor(date):
    if date:
        try:
            rain_pred = RainPrediction()
            rain_pred.load_data(date)
            rain_pred.preprocess_data()
            rain_pred.train_models()
            return rain_pred
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    else:
        print("Date parameter is missing.")
        return None