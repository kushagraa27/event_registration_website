import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ssyzzehptu",  # change this
        database="event_db"
    )
