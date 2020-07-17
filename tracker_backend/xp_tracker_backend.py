import json
import os
import subprocess
from datetime import date, datetime, timedelta
from threading import Thread
from time import sleep

import requests

from os.path import dirname as up
from os.path import join, realpath

#TODO: Seperate tracker and backend work, create a seperate module for general backend -> backend.py
#TODO: Upgrade, debug player commit
#TODO: Create a logs commit->PUSH system
#TODO: Make top weekly
#TODO: Annotate new register forms and register page func

#Make everythin logged on Ubuntu
import sys


#--Log all updates
#Modified from Stack Overflow!
class logConsoleFile:
    '''
    ##FROM Stack Overflow, so you may not understand it all.
    We are wrapping stdout and stderr to make them write to console and file logs,
    sort of like overrifing their built-in "write" function. Note, "write" coincidently
    has the same name for file IO class.

    Requires: sys.stdout = logConsoleFile(sys.stdout, file_name) in that format
    It can also be used for sys.stderr
    '''

    def __init__(self, stream, file_name):
        self.stream = stream
        # Append to constantly add
        self.file = open(f'{file_name}', mode='a')

    # Calls itself to it writes again. It is overriding I believe, not sure
    def write(self, data):
        self.stream.write(data)

        # self.stream.flush()
        # self.file.write(f"{time}")
        self.file.write(f"{getNow()}: {data}")

    def flush(self):
        pass
def getLogDir():
    '''
    Makes all code simpler. If the alias are changed
    in the imports section that could be an issue
    '''
    logdir = up(up(__file__))
    return join(logdir, "logs")

def getNow():
    '''
    Gets time in Hour:Min:Sec format. Should be used with a date specified externally
    :return: string format
    '''
    return datetime.now().strftime("%H:%M:%S")
#--Log all updates DONE

#--Log all updates DONE

#VCS/Shell Automation----
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
    return "COMMAND: " + str(proc_stdout)

def ensure_remote(url, remote_name, branch):
    '''
    Ensures local repo, branch master and remote 'remote_name' exists
    if it does not then we create it and update the cloud to the github version.
    Remember remote 'github' is the name of the local pointer to the actual
    github repository.
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

    #Check if github is registered as remote
    if remote_name in str(multiple_cmd(f"cd \"{gitPath}\"", "git remote")):
        print(f"Remote {remote_name} exists")
    #If it is not then make it
    else:
        print(multiple_cmd(f"cd \"{gitPath}\"",
                     "git init .",
                     f"git remote add {remote_name} {url}"))

    #Check if branch is there, if it is not you cannot start the program without potentially losing info on wrong branch
    if branch in str(multiple_cmd(f"cd \"{gitPath}\"", "git status")):
        print(f"Git branch:{branch} is checked out, being used.")
    else:
        print(f"Created remote {remote_name}!\nYou need to UPDATE/CHECKOUT LOCAL with a relevant repo!!\n EXITING NOW")
        exit()

#TODO: WRITE THIS, How to stay logged into github over ubuntu
def push_players(remote_name, branch):
    '''
    Branch should already be ensured by ensure_remote.
    Print automatically goes to console and logs.
    '''
    print(multiple_cmd(f"cd \"{getPlayerDir()}\"", "git add .",
                       f"git commit -m \"Pushing players at {getNow()} from {getOS()}\"",
                       f"git push {remote_name} {branch}"))

def push_logs(remote_name, branch):
    print(multiple_cmd(f"cd \"{getLogDir()}\"", "git add .",
                       f"git commit -m \"Pushing logs at {getNow()} from {getOS()}\"",
                       f"git push {remote_name} {branch}"))

def commit_player(username, remote_name, branch) -> str:
    '''
    Commits a folder to branch. Remote VCS is
    initialized before in a seperate function.
    players dir is already defined outside scope
    '''
    #exit if empty
    if username == "":
        return ""

    user_exists, player_info = playerAPIQuery(username)

    if username in getRegPlayers():
        return f"{username.title()} already registered..."
    elif user_exists:
        # Add username file to playersdir path
        with open(os.path.join(getPlayerDir(), username), mode="w"):
            print(multiple_cmd(f"cd \"{getPlayerDir()}\"", "git add .",
                               f"git commit -m \"{date.today()} committed {username} via website\"",
                               f"git push {remote_name} {branch}"))
            return f"Successfully registered {username.title()}!"
    else:
        return f"{username.title()} does not exist in Darkan..."

#push all files
def push_all(remote_name, branch):
    print(multiple_cmd(f"cd \"{getPlayerDir()}\"", "git add .",
                       f"git commit -m \"Committed all files via {remote_name} branch:{branch} internal at {getNow()}\"",
                       f"git push {remote_name} {branch}"))

#TODO: Replace all long code with this
def getOS():
    '''
    Returns either win or OS, used to respect DRY principles
    '''
    if "win" in os.sys.platform:
        return "win"
    else:
        return "ubuntu"

#TODO: Needs to be annotated and more precise on directory.
# def pull_all(remote_name, branch):
#     print(multiple_cmd(f"cd \"{getPlayerDir()}\"",
#                        f"git pull {remote_name} {branch}"))

#VCS/Shell DONE----

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

#---Player assurance functions
def getPlayerDir():
    '''
    Returns player directory as a string. Compatible with other OS using
    os.path

    :return: String directory path/breadcrumb, dynamic to OS
    '''
    #Magic Python variable
    filePath = __file__

    # Convert to standard of OS path string
    filePath = os.path.realpath(filePath)

    # Just get the folder
    filePath = os.path.dirname(filePath)
    filePath = os.path.realpath(filePath)

    # Now get player directory from this relative path
    playersdir = os.path.join(filePath, "players")

    # Convert to standard of OS
    playersdir = os.path.realpath(playersdir)
    return playersdir

def getRegPlayers():
    '''
    uses the current python file as a path and modifies it
    to find players folder. Players folder is parsed and
    strings are recorded and placed into a list. At the end
    it is gathered and sorted before returning the list.

    :return: a list of strings showing files in "players" folder
    '''
    filePath = __file__

    # Convert to standard of OS path string
    filePath = os.path.realpath(filePath)

    # Just get the folder
    filePath = os.path.dirname(filePath)
    filePath = os.path.realpath(filePath)

    # Now get player directory from this relative path
    playersdir = os.path.join(filePath, "players")

    # Convert to standard of OS
    playersdir = os.path.realpath(playersdir)

    #Sort it before you return the files as a list of strings. Sort returns none btw
    players = os.listdir(playersdir)
    players.sort()

    return players

def playerAPIQuery(player) -> tuple:
    '''
    Calls player from API and checks for error by accessing byte information.
    The GET request from HTTPS works even when there is no player. So we check
    after converting the byte file into a string by trying to access a known
    piece of information.

    :return: Tuple type (player existed in API, Actual Stat info)
    '''
    exists = False
    #=====----->The following was created with Postman
    url = "https://darkan.org/api/player/" + player.replace(" ", "_").lower()

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
        pass
    else:
        print(f"{player} query success")
        exists = True
    return (exists, player_info)
#---Player assurance functions DONE

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

def sync_stats():
    '''
    Syncronizes stats every 24 hours by calling gather game stats
    then cleaning the data. Lastly it will populate the day's
    Top weekly
    '''

    if "win" in os.sys.platform:
        clean_stats()
        setTopPlayers()
        #Windows doesnt update players
        push_logs("github", "windows")

    if "win" not in os.sys.platform:
        gather_game_stats()
        clean_stats()
        setTopPlayers()
        #Ubuntu will always be updated
        push_players("github", "ubuntu")
        push_logs("github", "ubuntu")


    print("all stats updated & cleaned & players potentially pushed. Also did top weekly!")

    #60 seconds * 60 minutes * 24 hours
    sleep(60*60*12)
    sync_stats()
#---XP tracking assurance DONE

#---Graph Maker
def makeGraph():
    pass
#---Graph Maker DONE

#---Top Weekly
def setTopPlayers():
    '''
    Sets top players for the week in the top_players file
    '''
    #TODO: Document previous work

    #Will be used to hold total xp over the week, keyed by name
    delta_week_all = {}

    #Do this for all players
    for player in getRegPlayers():
        #Take out only totalxp for the lifetime of the player, remember its a list of Stat objs
        player_stats = get_file_stats(player, "totalXp")

        #Xp from week goes here, every day registered will be here
        xpBuffer = []

        #Retrieve individual stat_obj
        for totalXp in player_stats:
            #If date is after 7 days ago ignore
            if totalXp.getDate() > (date.today() - timedelta(days=7)):
                #Put the dates until 7 days ago in the buffer
                xpBuffer.append(totalXp.getValue())

        #Create new player key, we are still in the reg player loop,
        #and substract last day of week by first day. Total difference is xp gained.
        #Lastly make sure the player has more than 1 entry
        if len(xpBuffer) > 1:
            delta_week_all[player] = xpBuffer[-1]-xpBuffer[0]

    #Get the folder above playerDir using os.path.dirname
    with open(f"{os.path.dirname(getPlayerDir())}/top_players", mode = "w") as file:
        #Stop at 10th player, i is counter
        i = 0

        # Organize the dictionary by top ten using keyword sorted
        for w in sorted(delta_week_all, key=delta_week_all.get, reverse=True):
            #Stop at 10th player
            if i == 10:
                break

            #Write each line then add to count
            file.write(f"{w}, {delta_week_all[w]}\n")
            i += 1

def getTopPlayers() -> list:
    '''
    Returns top 10 players of the week organized as a list of tuples.
    If it runs out of players who have more than 0 xp then it adds
    'No more XP registered' and exits the organization phase

    :return: list of tuples [(PLAYER1, XP1), (PLAYER2, XP2), ..., (PLAYER10, XP10)]
    '''
    #unorganized list, organize list
    unorg_players = []
    org_players = []

    #Start with unorganized: get a list of the top, [PLAYER1, XP1, PLAYER2, XP2, ...]
    with open(f"{os.path.dirname(getPlayerDir())}/top_players", mode="r") as file:
        unorg_players = file.read().split('\n')

    #End with organized list as a list of tuples
    for player in unorg_players:
        #If its empty let it go
        if player == '':
            continue

        #The line is "PLAYER1, XP1\n" as all strings so we split to interpret each as a list -> [P1, XP1]
        interpreted_line = player.split(", ")

        ranout_notice = "No more XP registered!"

        #If they earned nothing let it go and end the top list. Split makes a list of the line
        if interpreted_line[1] == '0':
            org_players.append(ranout_notice)
            break
        #Turn the list to a tuple
        else:
            #if there is a ranout notice skip
            if not ranout_notice in interpreted_line[1]:
                #Format the xp string, but the format function requires a int cast.
                xp = "{:,}".format(int(interpreted_line[1]))

                #Create a tuple from list elements.
                interpreted_line = (interpreted_line[0], xp)
                org_players.append(interpreted_line)
    #-Organize list DONE
    return org_players

def populatePlayerIcons():
    '''
    Creates player tags for top 10 players. Perhaps create a tag
    folder just for this purpose

    :return: icon strings in a list. Try list of lists once we get into online and offline.
    '''
    icon_dir = "static/images/"

    return [f"{icon_dir}goldtrophy.png", f"{icon_dir}silvertrophy.png", f"{icon_dir}bronzetrophy.png", "", "", "", "", "", "", ""]
#---Top Weekly DONE

#---Pure site oriented functions
def randomTab():
    '''
    Returns a random icon image string for all page tabs
    '''
    pass
#---Pure site oriented functions DONE

if __name__ == "__main__":
    '''
    if we are running this file, it is usually for testing and debugging.
    This won't run when imported as it would not be the __main__.
    Remember, main is established as the first indentation of code, even 
    in imports. This means all level 0 indentations run, even in imports.
    '''

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
            sys.stderr = logConsoleFile(sys.stderr, logdir)
            ensure_remote("https://github.com/JesseGuerrero/DarkanTools.git", "github", "windows")

        #Otherwise ubuntu
        else:
            logdir = join(getLogDir(), f"ubuntu_{date.today()}.log")
            #Do the same here but with ubuntu.
            sys.stdout = logConsoleFile(sys.stdout, logdir)
            sys.stderr = logConsoleFile(sys.stderr, logdir)
            ensure_remote("https://github.com/JesseGuerrero/DarkanTools.git", "github", "ubuntu")

        # Update stats everyday if we are out of focus, runs twice on a debug
        Thread(target=sync_stats).start()

    #If we are not running from app.py then we are not running the webserver so pass.
    else:
        pass




