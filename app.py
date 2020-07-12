#Essentials
from flask import Flask, render_template, request
from tracker_backend import xp_tracker_backend as be
#import matplotlib.pyplot as plt

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
    return render_template("index.html", icon = icon_list.pop(), player_list = be.reg_players)

@app.route('/register', methods=["GET", "POST"])
def register():
    #First implementation with backend
    reg_result = ""
    if request.method == "POST":
        new_player = request.form['user_reg']
        new_player = new_player.lower()
        reg_result = be.add_player(new_player)


    icondir = os.path.dirname(__file__)
    icondir = os.path.join(icondir, "static", "images", "icons")
    icon_list = os.listdir(icondir)

    shuffle(icon_list)
    return render_template("register_player.html", icon = icon_list.pop(), player_list = be.reg_players, result = reg_result)

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
    return render_template("index.html", icon = icon_list.pop(), player1 = player1, player2 = player2)
'''

