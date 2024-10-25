import mysql.connector
from mysql.connector import Error
import json
import os

class Database:
    def __init__(self, config_path='module/db_config.json'):
        
        # JSON 파일에서 설정 불러오기
        with open(config_path, 'r') as file:
            config = json.load(file)

        self.host = config['host']
        self.user = config['user']
        self.password = config['password']
        self.database = config['database']

    def connect(self):
        """데이터베이스에 연결합니다."""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error while connecting to MariaDB: {e}")
            return None

    def execute_query(self, query, params=None):
        """쿼리를 실행하고 결과를 반환합니다."""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params)
                result = cursor.fetchall()
                cursor.close()
            except Error as e:
                print(f"Error executing query: {e}")
                result = None
            finally:
                connection.close()
        return result
                

    def execute_commit(self, query, params=None):
        """INSERT, UPDATE, DELETE 같은 쿼리 실행 후 커밋합니다."""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(query, params)
                connection.commit()
                cursor.close()
            except Error as e:
                print(f"Error executing query: {e}")
            finally:
                connection.close()
            
    def select_query(self, query, params=None):
        return self.execute_query(self,query,params)
            
    def insert_query(self, query, params=None):
        self.execute_commit(self, query, params)
        
    def update_query(self, query, params=None):
        self.execute_commit(self, query, params)
            
    def delete_query(self, query, params=None):
        self.execute_commit(self, query, params)
