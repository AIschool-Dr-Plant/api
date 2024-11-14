import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
import json

class DiseasePredictionModel:
    def __init__(self):
        # 데이터 생성
        temperature_data = np.round(np.linspace(0, 50, 500), 2)

        # 감염률 계산 함수 정의 (각 함수식 적용)
        infection_rate1 = np.piecewise(
            temperature_data,
            [temperature_data >= 7, (temperature_data >= 7) & (temperature_data <= 25), (temperature_data > 25) & (temperature_data <= 30)],
            [0, lambda x: (x / 18 - 7 / 18) ** 2, lambda x: 1 - (x / 5 - 5) ** 2]
        )
        infection_rate2 = np.piecewise(
            temperature_data,
            [temperature_data >= 8, (temperature_data >= 8) & (temperature_data < 17.5), (temperature_data >= 17.5) & (temperature_data <= 25)],
            [0, lambda x: ((x - 8) ** 2) / (9.5 ** 2), lambda x: 1 - ((x - 17.5) ** 2) / (7.5 ** 2)]
        )
        infection_rate3 = np.piecewise(
            temperature_data,
            [temperature_data >= 10, (temperature_data >= 10) & (temperature_data < 26), (temperature_data >= 26) & (temperature_data <= 40)],
            [0, lambda x: ((x - 10) / (26 - 10)) ** 2, lambda x: 1 - ((x - 26) / (40 - 26)) ** 2]
        )

        # 데이터프레임 생성 및 퍼센티지로 변환
        infection_rate1 = np.round(infection_rate1 * 100, 2)
        infection_rate2 = np.round(infection_rate2 * 100, 2)
        infection_rate3 = np.round(infection_rate3 * 100, 2)

        combined_data = pd.DataFrame({
            'Temperature (°C)': temperature_data,
            'Infection Rate A (%)': infection_rate1,
            'Infection Rate B (%)': infection_rate2,
            'Infection Rate C (%)': infection_rate3
        })

        # 독립 변수(X)와 종속 변수(y) 설정
        X = combined_data[['Temperature (°C)']].values
        y1 = combined_data['Infection Rate A (%)'].values
        y2 = combined_data['Infection Rate B (%)'].values
        y3 = combined_data['Infection Rate C (%)'].values

        # 결정 트리 모델 생성 및 학습
        self.tree_model_A = DecisionTreeRegressor(random_state=42)
        self.tree_model_B = DecisionTreeRegressor(random_state=42)
        self.tree_model_C = DecisionTreeRegressor(random_state=42)

        self.tree_model_A.fit(X, y1)
        self.tree_model_B.fit(X, y2)
        self.tree_model_C.fit(X, y3)

    def predict_infection_rates(self, temperature):
        temperature_input = np.array([[temperature]])
        predicted_rate_A = self.tree_model_A.predict(temperature_input)[0]
        predicted_rate_B = self.tree_model_B.predict(temperature_input)[0]
        predicted_rate_C = self.tree_model_C.predict(temperature_input)[0]

        result = {
            "Temp": temperature,
            "A": round(predicted_rate_A, 2),
            "B": round(predicted_rate_B, 2),
            "C": round(predicted_rate_C, 2)
        }

        return json.dumps(result, indent=4)