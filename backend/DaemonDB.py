import operator
import mysql.connector, requests, json, schedule
from mysql.connector import Error, MySQLConnection
from datetime import datetime
from time import sleep


# TODO: Update all players every Monday with Iron as well.

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


def askQuery(connection: MySQLConnection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Query successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return cursor.fetchall()


def executeQuery(connection: MySQLConnection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query run successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def listPlayers():
    '''
    This is a generator
    :return: list of players from highscores but generatred
    '''
    page = 0
    while (True):
        print(f"page {page}")
        url = f"https://darkan.org/api/highscores?page={page}"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        page_info = json.loads(response.text.encode('utf8'))

        page_info: list
        if len(page_info) is 0:
            break

        page += 1
        for player_info in page_info:
            # print(player_info)
            name = player_info['displayName'].lower()
            isIron = player_info["ironman"]
            # print(f"{name} {isIron}")
            yield (name, isIron)


# Main here, make varchar name length longer

def UpdatePlayerListDB():
    connection = create_connection("51.79.66.9", "Jawarrior1", "ilikepeas1", "darkantools")

    for player in listPlayers():
        name = player[0]
        isIron = player[1]
        if isIron:
            isIron = 1
        else:
            isIron = 0
        executeQuery(connection, f"INSERT IGNORE INTO players (name, isIron) VALUES (\"{name}\", {isIron});")

    connection.close()


def GeneratePlayerNamesFromDB():
    connection = create_connection("51.79.66.9", "Jawarrior1", "ilikepeas1", "darkantools")
    for player_info in askQuery(connection, "SELECT * FROM darkantools.players;"):
        yield player_info
    connection.close()


def playerAPIQuery(player) -> tuple:
    '''
    Calls player from API and checks for error by accessing byte information.
    The GET request from HTTPS works even when there is no player. So we check
    after converting the byte file into a string by trying to access a known
    piece of information.

    :return: Tuple type (player existed in API, Actual Stat info)
    '''
    exists = False
    # =====----->The following was created with Postman
    url = "https://darkan.org/api/player/" + player.replace(" ", "_").lower()

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    # request, below, is the string representation of the player information
    request = response.text.encode('utf8')
    # =====----->

    # Load the API Request as a Python Dictionary
    player_info = json.loads(request)

    # "Stats" is a key. Inside that key is another dictionary of skills. If it does not exist, the GET was a failure
    try:
        player_info = player_info['stats']  # Remove everything else
    except:
        print("Player not found")
        pass
    else:
        print(f"{player} query success")
        exists = True
    return (exists, player_info)


def createXP_Profiles():
    connection = create_connection("51.79.66.9", "Jawarrior1", "ilikepeas1", "xp_profiles")
    skill_ID = {"Attack": 0, "Defence": 1, "Strength": 2, "Hitpoints": 3, "Ranged": 4, "Prayer": 5, "Magic": 6,
                "Cooking": 7, "Woodcutting": 8, "Fletching": 9, "Fishing": 10, "Firemaking": 11, "Crafting": 12,
                "Smithing": 13, "Mining": 14, "Herblore": 15, "Agility": 16, "Thieving": 17, "Slayer": 18,
                "Farming": 19, "Runecrafting": 20, "Hunter": 21, "Construction": 22, "Summoning": 23,
                "Dungeoneering": 24}

    for player in GeneratePlayerNamesFromDB():
        # Connection also created/seperate in generator
        name = f"`{player[0].lower()}`"
        create_TableSQL = f"CREATE TABLE IF NOT EXISTS {name} (date DATE PRIMARY KEY, name VARCHAR(30), isIron BOOLEAN, totalLevel SMALLINT UNSIGNED, " \
                          f"totalXp BIGINT UNSIGNED, attack INT UNSIGNED, defence INT UNSIGNED, strength INT UNSIGNED, hitpoints INT UNSIGNED, " \
                          f"ranged INT UNSIGNED, prayer INT UNSIGNED, magic INT UNSIGNED, cooking INT UNSIGNED, woodcutting INT UNSIGNED, " \
                          f"fletching INT UNSIGNED, fishing INT UNSIGNED, firemaking INT UNSIGNED, crafting INT UNSIGNED, smithing INT UNSIGNED, " \
                          f"mining INT UNSIGNED, herblore INT UNSIGNED, agility INT UNSIGNED, thieving INT UNSIGNED, slayer INT UNSIGNED, " \
                          f"farming INT UNSIGNED, runecrafting INT UNSIGNED, hunter INT UNSIGNED, construction INT UNSIGNED, summoning INT UNSIGNED, " \
                          f"dungeoneering INT UNSIGNED);"
        executeQuery(connection, create_TableSQL)

        (querySuccess, player_stats) = playerAPIQuery(name[1:-1])
        if (querySuccess):
            # print(player_stats)
            # print(datetime.now().strftime('%Y-%m-%d'))
            insertSkillSQL = f"INSERT IGNORE INTO {name} (date, name, isIron, totalLevel, totalXp, attack, defence, strength, hitpoints, " \
                             f"ranged, prayer, magic, cooking, woodcutting, fletching, fishing, firemaking, crafting, smithing, " \
                             f"mining, herblore, agility, thieving, slayer, farming, runecrafting, hunter, construction, summoning, " \
                             f"dungeoneering) VALUES (\"{datetime.now().strftime('%Y-%m-%d')}\", \"{name}\", {player[1]}, {player_stats['totalLevel']}" \
                             f", {player_stats['totalXp']}, "
            for name, id in skill_ID.items():
                insertSkillSQL = insertSkillSQL + f"{player_stats['skills'][id]['xp']}, "
            insertSkillSQL = insertSkillSQL[0:-2] + ");"
            # print(insertSkillSQL)
            executeQuery(connection, insertSkillSQL)

        # Connection closed seperately in generator
    connection.close()


def CreateTopTenDB():
    top_ten = []

    connection = create_connection("51.79.66.9", "Jawarrior1", "ilikepeas1", "xp_profiles")
    for player in GeneratePlayerNamesFromDB():
        query = f"SELECT date, name, isIron, totalXp FROM `{player[0]}` WHERE date >= DATE(NOW()) - INTERVAL 7 DAY;"
        answer = askQuery(connection, query)

        if (len(answer) is 0):
            continue
        name = answer[0][1]
        xpDelta = answer[-1][3] - answer[0][3]
        isIron = answer[0][2]
        answer = (name, isIron, xpDelta)

        if (xpDelta is 0):
            # No Xp!
            pass
        else:
            top_ten.append(answer)
    connection.close()

    top_ten.sort(key=lambda x: x[2])

    top_ten.reverse()
    print(top_ten)
    top_ten = top_ten[:10]
    print(top_ten)

    connection = create_connection("51.79.66.9", "Jawarrior1", "ilikepeas1", "darkantools")
    executeQuery(connection, "TRUNCATE TABLE top_ten;")
    for rank, player in enumerate(top_ten):
        name = player[0][1:-1]  # remove the quotes/apostraphie
        print(name)
        query = f"INSERT INTO top_ten (rank, name, isIron, totalXp) VALUES ({rank + 1}, \"{name}\", {player[1]}, {player[2]});"
        executeQuery(connection, query)
    connection.close()


def UpdateDB():
    while (True):
        (UpdatePlayerListDB())
        (createXP_Profiles())
        (CreateTopTenDB())
        sleep(60 * 60 * 13)


def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def readGEIcon(icon_id):
    print("Reading BLOB data from python_employee table")

    try:
        connection = mysql.connector.connect(host='51.79.66.9',
                                             database='darkantools',
                                             user='Jawarrior1',
                                             password='ilikepeas1')

        cursor = connection.cursor()
        sql_fetch_blob_query = """SELECT * from ge_icons where id = %s"""

        cursor.execute(sql_fetch_blob_query, (icon_id,))
        record = cursor.fetchall()
        for row in record:
            return row[1]

    except mysql.connector.Error as error:
        print("Failed to read BLOB data from MySQL table {}".format(error))

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def updateAllGEIcons():
    def insertIconBLOB(connection, id, path):
        print("Inserting BLOB")
        try:
            cursor = connection.cursor()
            sql_insert_blob_query = """ INSERT INTO ge_icons
                              (id, image) VALUES (%s,%s)"""

            empPicture = convertToBinaryData(path)

            # Convert data into tuple format
            insert_blob_tuple = (id, empPicture)
            result = cursor.execute(sql_insert_blob_query, insert_blob_tuple)
            connection.commit()
            print(f"Icon {id} inserted!")
        except mysql.connector.Error as error:
            print(f"Failed inserting BLOB data into MySQL table {error}")
        except Exception as e:
            print(f"other exception: {e}")


    connection = create_connection("51.79.66.9", "Jawarrior1", "ilikepeas1", "darkantools")
    executeQuery(connection, "TRUNCATE ge_icons;")
    for id in range(0, 24806):
        path = f"/root/Jesse/DarkanTools/ge_icons/items/{id}.png"
        insertIconBLOB(connection, id, path)
    if (connection.is_connected()):
        connection.close()
        print("MySQL connection is closed")

UpdateDB()


# from tkinter import *
# from PIL import ImageTk, Image
# import io
#
#
#
# root = Tk()
# canvas = Canvas(root, width = 300, height = 300)
#
# img = Image.open(io.BytesIO(readGEIcon(10)))
# img = ImageTk.PhotoImage(img)
#
# canvas.pack()
# canvas.create_image(150,150, anchor=NW, image=img)
# mainloop()
