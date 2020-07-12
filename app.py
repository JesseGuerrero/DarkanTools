#Essentials
from flask import Flask, render_template, request
#from DarkanTools1.tracker_backend import xp_tracker_backend as be
#import matplotlib.pyplot as plt

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
    return render_template("index.html", icon = icon_list.pop())

@app.route('/register')
def register():
    #First implementation with backend
    new_player = request.form['user_reg']


    icondir = os.path.dirname(__file__)
    icondir = os.path.join(icondir, "static", "images", "icons")
    icon_list = os.listdir(icondir)

    shuffle(icon_list)
    return render_template("register_player.html", icon = icon_list.pop())

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000, debug = False)


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

