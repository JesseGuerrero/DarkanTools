import operator
import json
import os
import subprocess
from datetime import date, datetime, timedelta
from threading import Thread
from time import sleep
from random import shuffle
import requests
from os.path import dirname as up
from os.path import join, realpath
import sys
from backend.APIQueries import *
from backend.filemanagement import *
from backend.databaseMethods import *
import pathlib
from backend.DaemonDB import *

class Skills():
    '''
    Retrieves skill names and ids for the project
    '''

    name_to_id = {"Attack": 0, "Defence": 1, "Strength": 2, "Hitpoints": 3, "Ranged": 4, "Prayer": 5, "Magic": 6,
                "Cooking": 7, "Woodcutting": 8, "Fletching": 9, "Fishing": 10, "Firemaking": 11, "Crafting": 12,
                "Smithing": 13, "Mining": 14, "Herblore": 15, "Agility": 16, "Thieving": 17, "Slayer": 18,
                "Farming": 19, "Runecrafting": 20, "Hunter": 21, "Construction": 22, "Summoning": 23,
                "Dungeoneering": 24, "totalXp": 25}

    #Reverses key and value
    id_to_name = dict(map(reversed, name_to_id.items()))

    def __init__(self):
        pass
    def getName(self, id : int):
        return self.id_to_name[id]
    def getSkillID(self, skill_name : str):
        return self.name_to_id[skill_name.title()]

#---Top Weekly
def getTopPlayers() -> list:
    global DB_PASSWORD
    '''
    Returns top 10 players of the week organized as a list of tuples.
    If it runs out of players who have more than 0 xp then it adds
    'No more XP registered' and exits the organization phase

    :return: list of tuples [(PLAYER1, XP1), (PLAYER2, XP2), ..., (PLAYER10, XP10)]
    '''
    connection = create_connection(DB_HOST_IP, DB_USERNAME, DB_PASSWORD, DB_MAIN_NAME)
    topPlayers = askQuery(connection, "SELECT * FROM top_ten;")
    connection.close()

    for i, each in enumerate(topPlayers):
        xpDelta = "{:,}".format(each[3])
        topPlayers[i] = (each[1], xpDelta, each[2])
    if (len(topPlayers) < 10):
        topPlayers.append("No more XP registered!")
    return topPlayers

def topPlayerIcons():
    '''
    Creates player tags for top 10 players. Perhaps create a tag
    folder just for this purpose

    :return: icon strings in a list. Try list of lists once we get into online and offline.
    '''
    icon_dir = "static/images/"

    return [f"{icon_dir}goldtrophy.png", f"{icon_dir}silvertrophy.png", f"{icon_dir}bronzetrophy.png", "", "", "", "", "", "", ""]
#---Top Weekly DONE

#---Pure site oriented functions
def randomTabIcon():
    '''
    Returns a random icon image string for all page tabs
    '''
    icondir = up(up(__file__))
    icondir = os.path.join(icondir, "static", "images", "icons")
    icon_list = os.listdir(icondir)
    shuffle(icon_list)
    return icon_list.pop()


# noinspection SqlResolve
def MakeSkillsDeltaListing(name, days):
    connection = create_connection(DB_HOST_IP, DB_USERNAME, DB_PASSWORD, "xp_profiles")
    try:
        query = f"SELECT totalLevel, attack, defence, strength, hitpoints, ranged, prayer, magic, cooking, woodcutting, fletching, fishing,\
           firemaking, crafting, totalXp, smithing, mining, herblore, agility, thieving, slayer, farming, runecrafting,\
           hunter, construction, summoning, dungeoneering FROM `{name.lower()}` WHERE date = CURDATE()"
        today = askQuery(connection, query)


        query = f"SELECT totalLevel, attack, defence, strength, hitpoints, ranged, prayer, magic, cooking, woodcutting, fletching, fishing,\
               firemaking, crafting, totalXp, smithing, mining, herblore, agility, thieving, slayer, farming, runecrafting,\
               hunter, construction, summoning, dungeoneering FROM `{name.lower()}` WHERE date = DATE(NOW()) - INTERVAL {days} DAY;"
        previous = askQuery(connection, query)
        connection.close()
        answer = (list(map(operator.sub, today[0], previous[0])))
        return answer
    except:
        connection.close()
        return [0]*27


#---Pure site oriented functions DONE

def readGEIcon(icon_id):
    print("Reading BLOB data from python_employee table")

    try:
        connection = mysql.connector.connect(host=DB_HOST_IP,
                                             database=DB_MAIN_NAME,
                                             user=DB_USERNAME,
                                             password=DB_PASSWORD)

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

def getGEOffersFormatted(buyorsell):
    for offer in (getGEOffers(buyorsell)):
        print(offer)
    return getGEOffers(buyorsell)

def readHolidayImage(name):
    print("Reading BLOB data from python_employee table")

    try:
        connection = mysql.connector.connect(host=DB_HOST_IP,
                                             database=DB_MAIN_NAME,
                                             user=DB_USERNAME,
                                             password=DB_PASSWORD)

        cursor = connection.cursor()
        sql_fetch_blob_query = """SELECT * from holiday_images where name = %s"""

        cursor.execute(sql_fetch_blob_query, (name,))
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

def getSoundFiles() -> list:
    '''
    Returns a list of tuples which represent (sound_number, sound_solution)
    Later in the front end if the solution is empty it is marked as unanswered.
    '''
    def parseSolutionsTXT(file_text) -> list:
        file_text = file_text.readlines()
        parsed_solutions = []

        for solution_line in file_text:
            current_solution = solution_line.replace("\n", "").split("-")
            current_solution[0] = int(current_solution[0])
            parsed_solutions.append(tuple(current_solution))
        return parsed_solutions

    project_path = pathlib.Path(__file__).parent.parent.absolute()
    solutions_txt_path = os.path.join(project_path, "static", "essentialIgnored", "effectsSolved.txt")
    solutions_txt = open(solutions_txt_path)
    full_solutions = parseSolutionsTXT(solutions_txt)

    # print(full_solutions) #For testing
    return full_solutions

def getUploadNum() -> str:
    uploadCount=0
    appPath = pathlib.Path(__file__).parent.absolute()
    path = os.path.join(appPath, "static", "essentialIgnored", "Uploads")

    for fileName in (os.listdir(path)):
        uploadCount+=1
    return str(uploadCount)

if __name__ == "__main__":
    '''
    if we are running this file, it is usually for testing and debugging.
    This won't run when imported as it would not be the __main__.
    Remember, main is established as the first indentation of code, even 
    in imports. This means all level 0 indentations run, even in imports.
    '''
    pass





if __name__ != "__main__":
    '''
    When you run Python from this file __name__ becomes __main__ as a string
    If you run this file from another module by importing it __name__ returns
    a string of the module name.
    
    We can check for which file/module we are running from importing and 
    using __main__. 
    
    Below we say if our primary Flask app, "app.py" us the __main__ or starting
    file we then do specific actions. 
    
    Otherwise if it is not the "app.py" module do nothing.
    '''

    #If we are up and running outside this file and in app.py as a web server
    import __main__
    if 'app.py' in str(__main__):

        #check if we are in windows
        if "win" in os.sys.platform:
            logdir = join(getLogDir(), f"win_{date.today()}.log")
            #Send errors and console outputs to file that is only unique to the day. Files will be unique according to day.
            sys.stdout = logConsoleFile(sys.stdout, logdir)
            sys.stderr = logConsoleFile(sys.stderr, logdir, err=True)

        #Otherwise ubuntu
        else:
            logdir = join(getLogDir(), f"ubuntu_{date.today()}.log")
            #Do the same here but with ubuntu.
            sys.stdout = logConsoleFile(sys.stdout, logdir)
            sys.stderr = logConsoleFile(sys.stderr, logdir, err=True)

        # Update stats everyday if we are out of focus, runs twice on a debug

    #If we are not running from app.py then we are not running the webserver so pass.
    else:
        pass




