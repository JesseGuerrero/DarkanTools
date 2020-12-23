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
from backend.backend import *


#TODO: Annotate/organize all this better


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

    def __init__(self, stream, file_name, err = False):
        self.stream = stream
        # Append to constantly add
        self.file = open(f'{file_name}', mode='a')
        self.err = err

    # Calls itself to it writes again. It is overriding I believe, not sure. Email me if its an error
    def write(self, data):
        self.stream.write(data)
        self.file.write(f"{getNow()}: {data}\n")

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

def add_player_file(username, remote_name, branch) -> str:
    '''
    Adds a player file. Make sure all are lower case.
    Also commits player folder to branch. Remote VCS is
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
        # Add username file to playersdir path, make sure its lower.
        with open(os.path.join(getPlayerDir(), username.lower()), mode="w"):
            print(multiple_cmd(f"cd \"{getPlayerDir()}\"", "git add .",
                               f"git commit -m \"{date.today()} committed {username} via website\"",
                               f"git push {remote_name} {branch}"))
            return f"Successfully registered {username.title()}!"
    else:
        return f"{username.title()} does not exist in Darkan..."

def updatedPlayerList():
    '''
    This is a generator
    :return: list of players from highscores but generatred
    '''
    for page in range(0, 11):
        url = f"https://darkan.org/api/highscores?page={page}"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        page_info = json.loads(response.text.encode('utf8'))
        for each in page_info:
            yield each['displayName'].lower()

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

def emailAdmin():
    #Setup email, copied from Python zero to hero udemy course
    import smtplib
    smtp_object = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_object.ehlo()
    smtp_object.starttls()
    smtp_object.login("jesseguerrero1991@gmail.com", "fniv ihzs ofzk stsu")

    msg = f'''
    Subject: Your {getOS()} darkantools server has been turned off.
    '''
    smtp_object.sendmail("jesseguerrero1991@gmail.com", "jesseguerrero1991@gmail.com", msg)
    smtp_object.quit()
    print("emailAdmin was run")


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


#---Player assurance functions DONE


if __name__ == "__main__":
    print("you are running filemanagement")

