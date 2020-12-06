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

#TODO: Annotate new register forms and register page func
#TODO: Needs to be annotated and more precise on directory.
# def pull_all(remote_name, branch):
#     print(multiple_cmd(f"cd \"{getPlayerDir()}\"",
#                        f"git pull {remote_name} {branch}"))



#Create a Stat class
class Stat():
    '''
    Stores stats information for future use.
    name of stat
    value is xp
    timestamp is a date the stat was made.

    These are meant to be generated and sent to garbage as they are made
    and left in a dead scope.
    '''

    skill_ID = {"Attack": 0, "Defence": 1, "Strength": 2, "Hitpoints": 3, "Ranged": 4, "Prayer": 5, "Magic": 6,
                "Cooking": 7, "Woodcutting": 8, "Fletching": 9, "Fishing": 10, "Firemaking": 11, "Crafting": 12,
                "Smithing": 13, "Mining": 14, "Herblore": 15, "Agility": 16, "Thieving": 17, "Slayer": 18,
                "Farming": 19, "Runecrafting": 20, "Hunter": 21, "Construction": 22, "Summoning": 23,
                "Dungeoneering": 24, "totalXp": 25}

    #Reverses key and value
    skill_Name = dict(map(reversed, skill_ID.items()))

    def __init__(self, name : str, value : int, timestamp : date):
        self.name = name
        self.value = value
        self.timestamp = timestamp

    def __str__(self):
        return f"{self.name} : {self.value} : {self.timestamp}"

    def getName(self): return self.name
    def getValue(self): return self.value
    def getDate(self): return self.timestamp


#---XP tracking assurance
def get_game_stats(player : str) -> dict:
    '''
    Meant for internal use.

    :param player: Insert a Darkan username as a string
    :return: Returns their stats from the Darkan API & adds a username key
    '''
    user_exists, player_info = playerAPIQuery(player)

    if user_exists:
        # Now we add meta data to the dict for future reference
        player_info["name"] = player  # Add a name

        #We will add a date meta to it as a string
        player_info["timestamp"] = str(date.today()) #JSON does not accept date objects so its str
        return player_info

def save_stats(stats : dict):
    '''
    Adds a current record of stat changes to a file. with the oldest at the top.
    It finds the appropriate file name to write the stats dictionary via the
    name key, which was added in get_game stats.

    :param stats: Requires dictionary of current statistics
    :return: None
    '''
    #Opens a file in write mode, saving it as PLAYERNAME
    directory = f"{getPlayerDir()}/{stats['name'].lower()}"
    with open(directory, mode="a") as file:
        file.write(str(stats).replace("'", '"') + "\n") #JSON does not accept single quotes

def get_file_stats(player : str, stat_ID : str, days = 7) -> list:
    '''
    stats: list of stats from oldest to newest top to bottom
    newest_dict: Current stat from top to bottom
    current stat: parsed stat_dict
    :return: a list of Stat objects for the specified stat
    '''
    with open(f"{getPlayerDir()}/{player}", mode="r") as file:
        stats = []

        #readlines returns a list of lines/string dictionaries of each daily stat report
        for line in file.readlines():
            # Load the file read as a Python Dictionary from the top, starting with the oldest dictionary entry
            newest_stat = json.loads(line)

            #Create the stat for outer scope

            # Total xp is special in that there are not too many nested calls
            if stat_ID == "totalXp":
                #Construct stats, remember it has a date object in constructor
                stamp = datetime.strptime(newest_stat["timestamp"], "%Y-%m-%d").date()
                newest_stat = Stat(stat_ID, newest_stat[stat_ID], stamp)
            # Use the stat_ID keys to signify it is a regular skill
            elif stat_ID.title() in Stat.skill_ID:
                #I need to get all the attributes for the Stat() class but there is a lot of nesting
                #Remember it is name, datetime, xp

                #Name
                stat_name = stat_ID.title()

                #Date
                stamp = datetime.strptime(newest_stat["timestamp"], "%Y-%m-%d").date()

                #XP value, remember the value for skill_ID is its place in the skill dictionary
                skill_index = Stat.skill_ID[stat_name] #Get the index for skills list
                newest_stat = newest_stat["skills"] #Specify into list of stat dictionaries
                newest_stat = newest_stat[skill_index]
                xp_value = newest_stat['xp']

                #Create stat
                newest_stat = Stat(stat_name, xp_value, stamp)
            else:
                print("Wrong stat name")
                break

            #Here we are adding stats to a list with conditions
            if newest_stat.timestamp < (date.today() - timedelta(days=days)):
                #If our newest date was made after the past DAYS days
                continue
            elif len(stats) is 0:
                # If stats is an empty list add to it
                stats.append(newest_stat)
            elif newest_stat.timestamp <= stats[-1].timestamp or newest_stat is None:
                '''
                newest stat is the newest line of stats, the one below, as a Stat object. Stats[-1] is the previous or
                the one before, making it older. The newest cannot be after so we continue and skip this stat.
                '''
                continue
            else:
                #The stat passed the test and can be added to the list
                stats.append(newest_stat)
        return stats

def gather_game_stats():
    '''
    Gathers all stat information for registered players
    '''
    for player in getRegPlayers():
        stat_record = get_game_stats(player) #Gets stat of the day and puts it in a record
        save_stats(stat_record) #save it into a file and append to it

def clean_stats():
    '''
    Deletes stats recorded on the same day for all players and deletes past 180 days.
    Maybe do this once a month. The delete after 180 days is unwritten.
    '''
    for player in getRegPlayers():

        #Create stats for outer scope, the cleaned_stats is the filtered list of {PLAYERDICT}s
        cleaned_stats = []

        #This will be the most recent {PLAYERDICT} as we iterate
        newest_dict = {}

        with open(f"{getPlayerDir()}/{player}", mode='r') as file:
            #Open the file as a string "{PLAYERDICT} \n" over and over
            player_file = file.readlines()
            player_file

            #Each line is a new {PLAYERDICT}
            for line in player_file:

                #Don't accept anything that is not starting with "{"
                if line[0] != "{":
                    continue

                # Remember load JSON does not accept single quotes
                line = line.replace("'", '"')

                #Convert to dictionary
                newest_dict = json.loads(line)

                #Always add the first stat dictionary
                if len(cleaned_stats) == 0:
                    cleaned_stats.append(newest_dict)

                #The newest cannot be the oldest. As we parse down the file we get to newer stat_dict, otherwise skip it
                elif newest_dict['timestamp'] <= cleaned_stats[-1]['timestamp']:
                    continue
                else:
                    cleaned_stats.append(newest_dict)

        with open(f"{getPlayerDir()}/{player}", mode='w+') as file:
             for each in cleaned_stats:
                 #Remember load JSON does not accept single quotes, this one may be unnecessary
                 file.write(str(each).replace("'", '"')+"\n")

#---XP tracking assurance DONE


#---Top Weekly
def getTopPlayers() -> list:
    '''
    Returns top 10 players of the week organized as a list of tuples.
    If it runs out of players who have more than 0 xp then it adds
    'No more XP registered' and exits the organization phase

    :return: list of tuples [(PLAYER1, XP1), (PLAYER2, XP2), ..., (PLAYER10, XP10)]
    '''
    connection = create_connection("51.79.66.9", "Jawarrior1", "ilikepeas1", "darkantools")
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
    connection = create_connection("51.79.66.9", "Jawarrior1", "ilikepeas1", "xp_profiles")
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

def getGEOffersFormatted(buyorsell):
    for offer in (getGEOffers(buyorsell)):
        print(offer)
    return getGEOffers(buyorsell)

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
            ensure_remote("https://github.com/JesseGuerrero/DarkanTools.git", "github", "windows")

        #Otherwise ubuntu
        else:
            logdir = join(getLogDir(), f"ubuntu_{date.today()}.log")
            #Do the same here but with ubuntu.
            sys.stdout = logConsoleFile(sys.stdout, logdir)
            sys.stderr = logConsoleFile(sys.stderr, logdir, err=True)
            ensure_remote("https://github.com/JesseGuerrero/DarkanTools.git", "github", "ubuntu")

        # Update stats everyday if we are out of focus, runs twice on a debug

    #If we are not running from app.py then we are not running the webserver so pass.
    else:
        pass




