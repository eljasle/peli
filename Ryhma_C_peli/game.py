import random
import Story
from geopy import distance

import mysql.connector

conn = mysql.connector.connect (
    host='localhost',
    port='3306',
    database='c_peli',
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
    return



def update_location(icao, p_range, u_money, g_id):
    sql = f'''UPDATE game SET location = %s, player_range = %s, money = %s WHERE id = %s'''
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (icao, p_range, u_money, g_id))





def bad_guy(player_range, current_airport,game_id, all_airports):













# haluuko pelaaja lukea backstoryn
storyDialog = input('Do you want to read the background story? (Y/N): ')
if storyDialog == 'Y':
    # print wrapped string line by line
    for line in Story.getStory():
        print(line)