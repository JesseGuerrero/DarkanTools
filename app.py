#Essentials
from flask import Flask, render_template, request
from random import shuffle
import os

#TODO: Finish XP Tracker then deploy. Then start on GE
#TODO: Apply Dry to page functions

#Custom Modules
from tracker_backend import xp_tracker_backend as be

#TODO: Create log system

#The Flask object constructor takes arguments
app = Flask(__name__)

#Landing page
@app.route('/', methods=["GET", "POST"])
def home():
    #Unique PATH per OS
    icondir = os.path.dirname(__file__)
    icondir = os.path.join(icondir, "static", "images", "icons")
    icon_list = os.listdir(icondir)

    shuffle(icon_list)

    #Create website oriented function section in backend. use each func ind at first, get rid of shuffle at each page.
    #Do this for each
    return render_template("home.html", icon = icon_list.pop(), player_list = be.getTopPlayers(),
                           player_icons = be.populatePlayerIcons())

#XP Tracker(Graph not made, graphmaker.py)
@app.route('/tracker', methods=["GET", "POST"])
def tracker():
    #Unique PATH per OS
    icondir = os.path.dirname(__file__)
    icondir = os.path.join(icondir, "static", "images", "icons")
    icon_list = os.listdir(icondir)

    return render_template("tracker.html", icon = icon_list.pop(), player_list = be.getTopPlayers(),
                           player_icons = be.populatePlayerIcons())

#A section for adding usernames
@app.route('/register', methods=["GET", "POST"])
def register():
    #Processes POSTS of registered player search and player registration
    reg_result = ""
    searched_player = ""
    if request.method == "POST":
        try:
            new_player = request.form['user_reg']
        except:
            #If user_reg form fails/empty, do nothing
            pass
        else:
            #Otherwise do this...
            new_player = new_player.lower()

            # reg_result is determined by the return of commit_player
            reg_result = be.commit_player(new_player, "github")
        try:
            searched_player = request.form['search_reg']
        except:
            # If search form fails/empty, do nothing
            pass
        else:
            if searched_player.lower() in be.getRegPlayers():
                searched_player = f"{searched_player.title()} is in our DB..."

    #Get path to icon, os.path works with all os, list icons in path, shuffle path
    icondir = os.path.dirname(__file__)
    icondir = os.path.join(icondir, "static", "images", "icons")
    icon_list = os.listdir(icondir)
    shuffle(icon_list)

    return render_template("register_player.html", icon = icon_list.pop(), player_list = be.getTopPlayers(),
                           result = reg_result, result2 = searched_player, player_icons = be.populatePlayerIcons())

@app.route("/grandexchange")
def grandexchange():
    '''
    Using API create a UI for GE
    '''

    icondir = os.path.dirname(__file__)
    icondir = os.path.join(icondir, "static", "images", "icons")
    icon_list = os.listdir(icondir)
    shuffle(icon_list)
    return render_template("grandexchange.html", icon = icon_list.pop(), player_list = be.getTopPlayers(),
                           player_icons = be.populatePlayerIcons())

if __name__ == '__main__':
    #Threaded option to enable multiple instances for multiple user access support
    #If its windows, we are probably debugging at home.
    if "win" in os.sys.platform:
        app.run(threaded=True, port=5000, debug = True)
    else:
        app.run(host = '0.0.0.0', port=80, threaded=True, debug=False)

