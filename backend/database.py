import mysql.connector


def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Loka1234567!",
        database="schoolai"
    )

    return connection