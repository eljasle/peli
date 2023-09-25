import random
import story
from geopy import distance

import mysql.connector

conn = mysql.connector.connect (
    host='localhost',
    port='3306',
    database='flight_game',
    user=config.user,
    pwd=config.pwd,

)