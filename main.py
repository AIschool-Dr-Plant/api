# main.py

from module.db_module import get_db_session
from module.crud import (
    select_sensor_data, insert_sensor_data, update_sensor_data, delete_sensor_data
)
from module.db_table_class import SensorData
from datetime import datetime

def main():
    # INSERT 예제: 새로운 센서 데이터 삽입
    # with get_db_session() as db:
    #     new_sensor = SensorData(
    #         AP="1013", HUM="50", TEMP="25", WS="5", WD="N", RF="0",
    #         MEAS_DT=datetime.utcnow(), REG_ID="admin", DEV_ID="DEV001"
    #     )
    #     inserted_sensor = insert_sensor_data(db, new_sensor)
    #     print(f"Inserted Sensor Data: {inserted_sensor}")

    # SELECT 예제: 센서 데이터 조회
    with get_db_session() as db:
        sensors = select_sensor_data(db)
        print("Sensor Data:", sensors)

    # UPDATE 예제: 센서 데이터 수정
    # with get_db_session() as db:
    #     updated_sensor = update_sensor_data(db, inserted_sensor.DATA_ID, {"TEMP": "30"})
    #     print(f"Updated Sensor Data: {updated_sensor}")

    # DELETE 예제: 센서 데이터 삭제
    # with get_db_session() as db:
    #     deleted_sensor = delete_sensor_data(db, inserted_sensor.DATA_ID)
    #     print(f"Deleted Sensor Data: {deleted_sensor}")

if __name__ == "__main__":
    main()
