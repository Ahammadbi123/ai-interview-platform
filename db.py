import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ahammadbi@39",
        database="ai_interview_platform"
    )
