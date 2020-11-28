import mysql.connector, requests, json, schedule
from mysql.connector import Error, MySQLConnection

def askQuery(connection : MySQLConnection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Query successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return cursor.fetchall()

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection