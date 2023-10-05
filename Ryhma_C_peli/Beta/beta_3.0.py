import random
from Ryhma_C_peli.Beta.Story import story
from geopy import distance

import mysql.connector

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
FROM airport
WHERE continent = 'EU' 
AND type='large_airport'
AND iso_country!='RU'
ORDER by RAND()
LIMIT 30;"""
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
    airports_with_country = []
    for airport in a_ports:
        airport_info = get_airport_info(airport['ident'])
        airports_with_country.append({
            'ident': airport['ident'],
            'name': airport['name'],
            'distance': calculate_distance(icao, airport['ident']),
            'country': airport_info['iso_country']
        })
    return airports_with_country

# villain of the game

villain_location = None


all_airports = get_airports()
villain_visited_airports = set()
def villain_moves_rounds(player_airports):
    global villain_location, villain_visited_airports
    # Step 1: Retrieve a list of airports
    sql = "SELECT id, name, latitude_deg, longitude_deg, ident FROM airport;"
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    airports = cursor.fetchall()

    if not player_airports:
        print("No airports found in the database.")
        return

    # Step 2: Randomly select an initial airport for the villain
    initial_airport = random.choice(player_airports)
    villain_location = initial_airport
    villain_visited_airports.add(villain_location['ident'])
    print(f"Villain is on", villain_location)


def villain_movement():
    global villain_location

    # Calculate distances from the villain's current location to all airports
    distances = []
    for airport in all_airports:
        if airport['ident'] != villain_location['ident'] and airport['ident'] not in villain_visited_airports:
            et채isyys = calculate_distance(villain_location['ident'], airport['ident'])
            distances.append((airport, et채isyys))

    # Sort the airports by distance (in ascending order)
    distances.sort(key=lambda x: x[1])

    # Select the three closest unvisited airports (excluding the current one)
    closest_unvisited_airports = [airport for airport in distances if airport[0]['ident'] not in villain_visited_airports][:3]

    if closest_unvisited_airports:
        # Choose one of the closest unvisited airports randomly
        chosen_airport = random.choice(closest_unvisited_airports)[0]

        # Update the villain's location to the chosen airport
        villain_location = chosen_airport

        # Mark the chosen airport as visited
        villain_visited_airports.add(villain_location['ident'])

        print("Villain is now in", villain_location)
    else:
        print("The villain has visited all available airports.")


def generate_directional_hints(player_airport, villain_airport):
    lat_diff = villain_airport['latitude_deg'] - player_airport['latitude_deg']
    lon_diff = villain_airport['longitude_deg'] - player_airport['longitude_deg']

    if lat_diff > 0 and lon_diff > 0:
        return "The villain is to the North-East of you."
    elif lat_diff < 0 and lon_diff > 0:
        return "The villain is to the South-East of you."
    elif lat_diff > 0 and lon_diff < 0:
        return "The villain is to the North-West of you."
    elif lat_diff < 0 and lon_diff < 0:
        return "The villain is to the South-West of you."
    else:
        return "You're very close to the villain!"


# game starts
# ask to show the story
storyDialog = input('Do you want to read the background story? (Y/N): ')
if storyDialog == 'Y' or storyDialog == "y":
    # print wrapped string line by line
    for line in story.getStory():
        print(line)

# GAME SETTINGS
print('When you are ready to start, ')
player = input('Type your player name: ')
# boolean for game over and win
game_over = False
win = False

# all airports
all_airports = get_airports()
villain_moves_rounds(all_airports)
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
    print(f"Climate temperature is now +{climate_temperature}째C.")
    # pause
    input('\033[32mPress Enter to continue...\033[0m')

    hint = generate_directional_hints(get_airport_info(current_airport), villain_location)
    print(f"Hint: {hint}")


    # show airports in range. if none, game over
    airports = airports_in_range(current_airport, all_airports)
    airports.sort(key=lambda airport: calculate_distance(current_airport, airport['ident']))
    print(f'''\033[34mThere are {len(airports)} airports in range: \033[0m''')
    if len(airports) == 0:
        print('You are out of range.')
        game_over = True
    else:
        print(f'''Airports: ''')
        for i, airport in enumerate(airports, start=1):
            ap_distance = calculate_distance(current_airport, airport['ident'])
            print(f'''{i}. {airport['name']}, Country: {airport['country']}, icao: {airport['ident']}, distance: {ap_distance:.0f}km''')
            # ask for destination
        dest = int(input('Enter the number of the airport you want to fly to: '))
        if dest >= 1 and dest <= len(airports):
            selected_distance = airports[dest - 1]
            dest = selected_distance['ident']
            selected_distance = calculate_distance(current_airport, dest)
            current_airport = dest



        # Update the climate temperature for every 100km flown
        while selected_distance >= 100:
            climate_temperature += 0.05
            selected_distance -= 100

            # Check if the climate temperature has reached a critical point
            if climate_temperature >= 6:
                print(f"Climate temperature is now +{climate_temperature:.2f}째C!")
                print("The world has exploded, and you are doomed!")
                game_over = True
                break

        # check if the player's current airport matches the villain's location
        if current_airport == villain_location['ident']:
            print("You found the villain!")
            win = True
            game_over = True
        else:
            villain_movement()

        # check if the villain has reached a certain location



# show game result
print(f'''{f'You won! Good job {player}!' if win else f'You lost! Better luck next time {player} :('}''')