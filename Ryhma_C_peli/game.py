import random
import Story
from geopy import distance

import mysql.connector

conn = mysql.connector.connect (
    host='localhost',
    port='3306',
    database='flight_game',
    user=config.user,
    pwd=config.pwd,
)


# 30 random lentokenttää EU alueelta
def get_airports():
    sql = """SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
FROM airport
WHERE continent = 'EU' 
AND type='large_airport'
ORDER by RAND()
LIMIT 30;"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

