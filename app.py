#Essentials
from flask import Flask, render_template, request
import os

#TODO: Checkout iframe, tipit, runehq, sals realm
    #1: Download tip.it
    #2: Make it runnable on Darkantools local
    #3: Relink all urls, media, js to Darkantools
    #4: Push to ubuntu
#TODO: Darken all colors
#TODO: Redo above for available webstes on web archive
#TODO: Convert all images to webp, bookmark in browser
#TODO: Then start on GE
#TODO: Apply Dry to page functions
#TODO: Create stat increase profile where each stat is categorized and shown to players
#Create Tabs for XP Tracker, GE Tracker https://getbootstrap.com/docs/4.5/components/navs/#tabs
#TODO: Change color scheme of tabs

#Custom Modules
from backend.backend import *
from backend.filemanagement import getRegPlayers

#The Flask object constructor takes arguments
app = Flask(__name__)

#Removes caching -> removes hard resets.
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


#Landing page
@app.route('/', methods=["GET", "POST"])
def home():
    return render_template("home.html", icon = randomTabIcon(), player_list = getTopPlayers(),
                           player_icons = topPlayerIcons(), home_active="active")

#XP Comparison
@app.route('/compare', methods=["GET", "POST"])
def tracker():
    player1, player2, stat_name, days = "", "", 25, 7
    if request.method == "POST":
        try:
            player1 = request.form['player1_input']
        except:
            player1 = ""
        try:
            player2 = request.form['player2_input']
        except:
            player2 = ""
        stat_name = request.form['skill_input']
        days = request.form['days_input']

    return render_template("compare.html", icon = randomTabIcon(), player_list = getTopPlayers(),
                           player_icons = topPlayerIcons(), tracker_active="active")

#Profile each player and their gains
@app.route('/profile', methods=["GET", "POST"])
def compare():
    return render_template("profile.html", icon = randomTabIcon(), player_list = getTopPlayers(),
                           player_icons = topPlayerIcons(), tracker_active="active")

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

            # reg_result is determined by the return of add_player_file
            if "win" in os.sys.platform:
                reg_result = add_player_file(new_player, "github", "windows")
            else:
                reg_result = add_player_file(new_player, "github", "ubuntu")
        try:
            searched_player = request.form['search_reg']
        except:
            # If search form fails/empty, do nothing
            pass
        else:
            if searched_player.lower() in getRegPlayers():
                searched_player = f"{searched_player.title()} is in our DB..."

    return render_template("register.html", icon = randomTabIcon(), player_list = getTopPlayers(),
                           result = reg_result, result2 = searched_player, player_icons = topPlayerIcons(),
                           tracker_active = "active")

@app.route("/ge")
def ge():
    '''
    Using API create a UI for GE
    '''
    return render_template("ge.html", icon = randomTabIcon(), player_list = getTopPlayers(),
                           player_icons = topPlayerIcons(), ge_active ="active")

@app.route('/street')
def street():
    return render_template("street.html", icon = randomTabIcon(), player_list = getTopPlayers(),
                           player_icons = topPlayerIcons(), ge_active ="active")

@app.route('/upload')
def upload():
    return render_template("upload.html", icon = randomTabIcon(), player_list = getTopPlayers(),
                           player_icons = topPlayerIcons(), ge_active ="active")

@app.route('/donate')
def donate():
    return render_template("donate.html", icon = randomTabIcon(), player_list = getTopPlayers(),
                           player_icons = topPlayerIcons(), donate_active = "active")

if __name__ == '__main__':
    #Threaded option to enable multiple instances for multiple user access support
    #If its windows, we are probably debugging at home.
    if "win" in os.sys.platform:
        app.run(threaded=True, port=5000, debug = False)
    else:
        app.run(host = '0.0.0.0', port=80, threaded=True, debug=False)