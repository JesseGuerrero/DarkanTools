'''
This is the stats module
'''
from datetime import date, datetime
import os
import json
from time import sleep
import requests
from threading import Thread
import subprocess
import os

#<----GET RELATIVE PATH TO PLAYERS---->

#Magic variable with file path string
filePath = __file__

#Convert to standard of OS path string
filePath = os.path.realpath(filePath)

#Just get the folder
filePath = os.path.dirname(filePath)
filePath = os.path.realpath(filePath)

#Now get player directory from this relative path
playersdir = os.path.join(filePath, "players")

#Convert to standard of OS
playersdir = os.path.realpath(playersdir)

#<---- DONE ---->

#Create Globals
reg_players = os.listdir(playersdir)

skill_ID = {"Attack": 0, "Defence": 1, "Strength": 2, "Hitpoints": 3, "Ranged": 4, "Prayer": 5,"Magic": 6,"Cooking": 7
    ,"Woodcutting": 8,"Fletching": 9,"Fishing": 10,"Firemaking": 11,"Crafting": 12,"Smithing": 13,"Mining": 14
    ,"Herblore": 15,"Agility": 16,"Thieving": 17,"Slayer": 18,"Farming": 19,"Runecrafting": 20,"Hunter": 21
    ,"Construction": 22,"Summoning": 23,"Dungeoneering": 24}

#Create a Stat class
class Stat():
    def __init__(self, name : str, value : int, timestamp : date):
        self.name = name
        self.value = value
        self.timestamp = timestamp

    def __str__(self):
        return f"{self.name} : {self.value} : {self.timestamp}"

    def getName(self): return self.name
    def getValue(self): return self.value
    def getDate(self): return self.timestamp

def add_player(username) -> str:
    if username in reg_players:
        return f"{username.title()} already registered..."
    else:
        file = open(os.path.join(playersdir, username), mode="w")
        file.close()
        return f"Successfully registered {username.title()}!"

def get_stats(player : str) -> dict:
    '''
    Meant for internal use.

    :param player: Insert a Darkan username as a string
    :return: Returns their stats from the Darkan API & adds a username key
    '''

    #=====----->The following was created with Postman
    url = "https://darkan.org/api/player/" + player

    payload = {}
    headers= {}

    response = requests.request("GET", url, headers=headers, data = payload)

    #request, below, is the string representation of the player information
    request = response.text.encode('utf8')
    #=====----->

    #Load the API Request as a Python Dictionary
    player_info = json.loads(request)

    #"Stats" is a key. Inside that key is another dictionary of skills. If it does not exist, the GET was a failure
    try:
        player_info = player_info['stats'] #Remove everything else
    except:
        print("Player not found")
    else:
        print(f"{player} query success")

    #Now we add meta data to the dict for future reference
    player_info["name"] = player  # Add a name

    #We will add a date meta to it as a string
    player_info["timestamp"] = str(date.today()) #JSON does not accept date objects so its str
    return player_info

def save_stats(stats : dict):
    '''
    Adds a current record of stat changes to a file. with the oldest at the top

    :param stats: Requires dictionary of current statistics
    :return: None
    '''
    #Opens a file in write mode, saving it as PLAYERNAME
    directory = f"{playersdir}/{stats['name'].lower()}"
    with open(directory, mode="a") as file:
        file.write(str(stats).replace("'", '"') + "\n") #JSON does not accept single quotes

def load_stats(player : str, stat_ID : str, days = 90) -> list:
    '''
    stats: list of stats from oldest to newest top to bottom
    newest_dict: Current stat from top to bottom
    current stat: parsed stat_dict
    :return: a list of Stat objects for the specified stat
    '''
    directory = f"players/{player}"
    with open(directory, mode="r") as file:
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
            elif stat_ID.title() in skill_ID:
                #I need to get all the attributes for the Stat() class but there is a lot of nesting
                #Remember it is name, datetime, xp

                #Name
                stat_name = stat_ID.title()

                #Date
                stamp = datetime.strptime(newest_stat["timestamp"], "%Y-%m-%d").date()

                #XP value, remember the value for skill_ID is its place in the skill dictionary
                skill_index = skill_ID[stat_name] #Get the index for skills list
                newest_stat = newest_stat["skills"] #Specify into list of stat dictionaries
                newest_stat = newest_stat[skill_index]
                xp_value = newest_stat['xp']

                #Create stat
                newest_stat = Stat(stat_name, xp_value, stamp)
            else:
                print("Wrong stat name")
                break

            #Here we are adding stats to a list with conditions
            if len(stats) is 0:
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

def gather_all():
    '''
    Gathers all stat information for registered players
    '''
    for player in reg_players:
        stat_record = get_stats(player) #Gets stat of the day and puts it in a record
        save_stats(stat_record) #save it into a file and append to it

def clean_stats():
    '''
    Deletes stats recorded on the same day for all players and deletes past 180 days.
    Maybe do this once a month. The delete after 180 days is unwritten.
    '''
    for player in reg_players:
        #Create stats for outer scope, the cleaned_stats is the filtered list of {PLAYERDICT}s
        cleaned_stats = []

        #This will be the most recent {PLAYERDICT} as we iterate
        newest_dict = {}


        with open(f"{playersdir}/{player}", mode='r') as file:
            #Open the file as a string "{PLAYERDICT} \n" over and over
            player_file = file.readlines()
            player_file

            #Each line is a new {PLAYERDICT}
            for line in player_file:
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

        with open(f"{playersdir}/{player}", mode='w+') as file:
             for each in cleaned_stats:
                 #Remember load JSON does not accept single quotes, this one may be unnecessary
                 file.write(str(each).replace("'", '"')+"\n")

def sync_stats():
    gather_all()
    clean_stats()
    print("all stats updated & cleaned")

    #60 seconds * 60 minutes * 24 hours
    sleep(60*60*24)
    sync_stats()


def multiple_cmd(*cmds):
    '''
    Runs multiple commands in sub-process shell. Commands are seperated differently depending on OS.
    If it is not windows it will default to a ";" seperator.

    :param cmds: A tuple which is joined/combined into a string with a seperator
    :return: output of shell
    '''
    command = ""
    if "win" in os.sys.platform:
        command = " & ".join(cmds)
    else:
        command = " ; ".join(cmds)

    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    return proc_stdout

#Version control automation
def ensure_remote(url, remote_name):
    '''
    Ensures local repo, branch master and remote 'remote_name' exists
    we need to pull AT THE START OF THE WEBSERVER ONLY TO UPDATE THE WEB
    '''

    #----Get current file path
    gitPath = __file__
    # Convert to standard of OS path string
    gitPath = os.path.realpath(gitPath)
    # Just get the folder, then the folder of the folder, go one up
    gitPath = os.path.dirname(gitPath)
    gitPath = os.path.dirname(gitPath)

    #Convert to OS friendly
    gitPath = os.path.realpath(gitPath)
    #----


    if remote_name in str(multiple_cmd(f"cd \"{gitPath}\"", "git remote")):
        print(f"Remote {remote_name} exists, don't worry")
    #CHANGE THIS TO PULL
    else:
        multiple_cmd(f"cd \"{gitPath}\"",
                     "git init .",
                     f"git commit -m \"local repo & remote created on server as {remote_name}!\"",
                     f"git remote add {remote_name} {url}")
        print(f"Created remote {remote_name}!")


def commitplayers(remote_name, username):
    '''
    commits a folder to remote_name. REMOTE NAME IS ENSURED AT THE START
    '''
    if username in os.listdir("players"):
        print("player already exists")
    else:  # Commit player
        subprocess.call("git add players", shell=True)
        subprocess.call(f"git commit -m \"{username} was committed\"", shell=True)
        subprocess.check_output(f"git push {remote_name} master", shell=True)
        print("executed")

if __name__ == "__main__":
    #clean_stats()
    #Gathers stats for all registered players
    gather_all()

if __name__ != "__main__":
    #Make sure there is a connection to remote github
    ensure_remote("https://github.com/JesseGuerrero/link.git", "link")

    #Update stats everyday if we are out of focus, runs twice on a debug
    Thread(target=sync_stats).start()




