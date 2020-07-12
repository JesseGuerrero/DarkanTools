#Essentials
from flask import Flask, render_template, request
from tracker_backend import xp_tracker_backend as be

#TODO: Create log system

#Extras
from random import shuffle
import os

#The Flask object constructor takes arguments
app = Flask(__name__)

# A welcome message to test our server
@app.route('/', methods=["GET", "POST"])
def home():
    #Unique PATH per OS
    icondir = os.path.dirname(__file__)
    icondir = os.path.join(icondir, "static", "images", "icons")
    icon_list = os.listdir(icondir)

    shuffle(icon_list)
    return render_template("home.html", icon = icon_list.pop(), player_list = be.getRegPlayers())

@app.route('/tracker', methods=["GET", "POST"])
def tracker():
    #Unique PATH per OS
    icondir = os.path.dirname(__file__)
    icondir = os.path.join(icondir, "static", "images", "icons")
    icon_list = os.listdir(icondir)

    return render_template("tracker.html", icon = icon_list.pop(), player_list = be.getRegPlayers())

@app.route('/register', methods=["GET", "POST"])
def register():
    #First implementation with backend
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

    return render_template("register_player.html", icon = icon_list.pop(), player_list = be.getRegPlayers(),
                           result = reg_result, result2 = searched_player)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    #If its windows, we are probably debugging at home.
    if "win" in os.sys.platform:
        app.run(threaded=True, port=5000, debug = True)
    else:
        app.run(threaded=True, port=5000, debug=False)

'''
@app.route('/', methods=["GET", "POST"])
def home():



    player1 = ""
    player2 = ""
    if request.method == "POST":
        player1 = request.form['player1_input']
        player2 = request.form['player2_input']
    return render_template("home.html", icon = icon_list.pop(), player1 = player1, player2 = player2)
'''

