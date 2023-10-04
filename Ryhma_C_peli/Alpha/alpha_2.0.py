import random
from Ryhma_C_peli.Story import story
from geopy import distance

import mysql.connector

#
#  TÄMÄ PELI TOIMII JA TÄMÄ ON TOTEUTETTU small_airports AVULLA **VERSION** Alpha 2.0
#

conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    database='c_peli',
    user='root',
    password='exel80jajop',
    autocommit=True
)

# Global variable for climate temperature
climate_temperature = 0

# FUNCTIONS

# select 30 airports for the game
def get_airports():
    sql = """SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
FROM airport WHERE iso_country = 'BE' and TYPE = 'small_airport'
ORDER by RAND()
LIMIT 38;"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


# get all goals
def get_goals():
    sql = "SELECT * FROM goal;"
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


# create new game
def create_game(cur_airport, p_name, a_ports):
    sql = "INSERT INTO game (location, screen_name) VALUES (%s, %s);"
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (cur_airport, p_name))
    g_id = cursor.lastrowid

    # add goals
    goals = get_goals()
    goal_list = []
    for goal in goals:
        for i in range(0, goal['probability'], 1):
            goal_list.append(goal['id'])

    # exclude starting airport
    g_ports = a_ports[1:].copy()
    random.shuffle(g_ports)

    for i, goal_id in enumerate(goal_list):
        sql = "INSERT INTO ports (game, airport, goal) VALUES (%s, %s, %s);"
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (g_id, g_ports[i]['ident'], goal_id))

    return g_id


# get airport info
def get_airport_info(icao):
    sql = f'''SELECT iso_country, ident, name, latitude_deg, longitude_deg
                  FROM airport
                  WHERE ident = %s'''
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (icao,))
    result = cursor.fetchone()
    return result


# check if airport has a goal
def check_goal(g_id, cur_airport):
    sql = f'''SELECT ports.id, goal, goal.id as goal_id, name, money 
    FROM ports 
    JOIN goal ON goal.id = ports.goal 
    WHERE game = %s 
    AND airport = %s'''
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (g_id, cur_airport))
    result = cursor.fetchone()
    if result is None:
        return False
    return result


# calculate distance between two airports
def calculate_distance(current, target):
    start = get_airport_info(current)
    end = get_airport_info(target)
    return distance.distance((start['latitude_deg'], start['longitude_deg']),
                             (end['latitude_deg'], end['longitude_deg'])).km


# get airports in range
def airports_in_range(icao, a_ports):
    return a_ports

# villain of the game

villain_location = None
villain_visited_airports = 0

all_airports = get_airports()

def villain_moves_rounds(player_airports):
    global villain_location, villain_visited_airports
    # Retrieve a list of airports
    sql = "SELECT id, name, latitude_deg, longitude_deg, ident FROM airport;"
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    airports = cursor.fetchall()

    if not player_airports:
        print("No airports found in the database.")
        return

    # Randomly select an initial airport for the villain
    initial_airport = random.choice(player_airports)
    villain_location = initial_airport
    print("Villain is on the loose in Belgium")


def villain_has_reached_condition():
    # if the villain has visited 10 airports, the player loses
    return villain_visited_airports >= 10


# call villain function
villain_moves_rounds(all_airports)


# game starts
# ask to show the story
storyDialog = input('Do you want to read the background story? (Y/N): ')
if storyDialog == 'Y':
    # print wrapped string line by line
    for line in story.getStory():
        print(line)

# GAME SETTINGS
print('When you are ready to start, ')
player = input('type player name: ')
# boolean for game over and win
game_over = False
win = False

# all airports
all_airports = get_airports()
# start_airport ident
start_airport = all_airports[0]['ident']

# current airport
current_airport = start_airport

# game id
game_id = create_game(current_airport, player, all_airports)

# GAME LOOP
while not game_over:
    # get current airport info
    airport = get_airport_info(current_airport)
    # show game status
    print(f'''You are at {airport['name']}.''')
    print('You have unlimited range.')
    print(f"Climate temperature is now +{climate_temperature}°C.")
    # pause
    input('\033[32mPress Enter to continue...\033[0m')


    # show airports in range. if none, game over
    airports = airports_in_range(current_airport, all_airports)
    print(f'''\033[34mThere are {len(airports)} airports in range: \033[0m''')
    if len(airports) == 0:
        print('You are out of range.')
        game_over = True
    else:
        print(f'''Airports: ''')

        for i, airport in enumerate(airports, start=1):
            ap_distance = calculate_distance(current_airport, airport['ident'])
            print(f'''{i}. {airport['name']}, icao: {airport['ident']}, distance: {ap_distance:.0f}km''')
        # ask for destination
        dest = int(input('Enter the number of the airport you want to fly to: '))
        if dest >= 1 and dest <= len(airports):
            selected_distance = airports[dest - 1]
            dest = selected_distance['ident']
            selected_distance = calculate_distance(current_airport, dest)
            current_airport = dest

        # Update the climate temperature for every 100km flown
        while selected_distance >= 50:
            climate_temperature += 0.2
            selected_distance -= 50

            # Check if the climate temperature has reached a critical point
            if climate_temperature >= 6:
                print(f"Climate temperature is now +{climate_temperature:.2f}°C!")
                print("The world has exploded, and you are doomed!")
                game_over = True
                break

        # check if the player's current airport matches the villain's location
        if current_airport == villain_location['ident']:
            print("You found the villain!")
            win = True
            game_over = True

        # check if the villain has reached a certain location
        if villain_has_reached_condition():
            print("The villain has escaped, and you lost!")
            game_over = True


# show game result
print(f'''{'You won!' if win else 'You lost! Better luck next time'}''')