#Essentials
import warnings

import werkzeug
from flask import Flask, render_template, request
from flask import send_file
from PIL import Image
import io
from flask_socketio import SocketIO, emit

#Custom Modules
from backend.backend import *
from backend.DaemonDB import *

#The Flask object constructor takes arguments
app = Flask(__name__)
socketio = SocketIO(app)

#Removes caching -> removes hard resets.
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = os.path.join(pathlib.Path(__file__).parent.absolute(), "static", "essentialIgnored", "Uploads")
app.config['MAX_CONTENT_PATH'] = 100_000 #100KB file limit
warnings.filterwarnings("ignore")

#Jinja
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

'''
Example code to clean up Jinja2 & app.py
'''
@app.context_processor
def my_utility_processor():
    def date_now(format="%d.m.%Y %H:%M:%S"):
        """ returns the formated datetime """
        return datetime.now().strftime(format)
    def increment(count):
        count['value'] += 1
        return ''
    return dict(date_now=date_now, increment=increment)

#Really good code here~~~~!!!!
@app.route('/images/<i>.png')
def image(i : str):
    if(i.startswith("christmas")):
        img = Image.open(io.BytesIO(readHolidayImage(i)))
        pass
    else:
        img = Image.open(io.BytesIO(readGEIcon(i)))

    # create file-object in memory
    file_object = io.BytesIO()

    # write PNG in file-object
    img.save(file_object, 'PNG')

    # move to beginning of file so `send_file()` it will read from start
    file_object.seek(0)

    return send_file(file_object, mimetype='image/PNG')

#Really good code here~~~~!!!!
@app.route('/sounds/<i>.mp3')
def sounds(i : str):
    if(i.isdigit()):
        pass
    else:
        i = 0;
    return send_file("static/essentialIgnored/effects/" +i + ".mp3")


#Landing page
@app.route('/', methods=["GET", "POST"])
def home():
    return render_template("home.html", icon = randomTabIcon(), player_list = getTopPlayers(),
                           player_icons = topPlayerIcons(), home_active="active")


@app.route('/soundpage', methods=["GET", "POST"])
def soundpage():
    return render_template("soundpage.html", soundFiles = getSoundFiles(), icon = randomTabIcon(), player_list = getTopPlayers(),
                           player_icons = topPlayerIcons(), sound_active = "active")
@socketio.on('client_message')
def receive_message (client_msg, repost = False):
    # if repost:
    #     appPath = pathlib.Path(__file__).parent.absolute()
    #     saveFilePath = os.path.join(appPath, "static", "essentialIgnored", "userInput")
    #     with open(saveFilePath, "r") as myfile:
    #         for line in myfile.readlines():
    #             msgInfo = line.split("~")
    #             msg = {"nickname": msgInfo[0], "message": msgInfo[1]}
    #             emit('server_message', msg, broadcast=True)
    # else:
    appPath = pathlib.Path(__file__).parent.absolute()
    saveFilePath = os.path.join(appPath, "static", "essentialIgnored", "userInput")
    with open(saveFilePath, "a") as myfile:
        name = client_msg["nickname"]
        msg = client_msg["message"]
        name.replace("~", "-")
        name.replace("\n", "")
        msg.replace("~", "-")
        msg.replace("\n", "")
        myfile.write(name + "~" + msg + "\n")
        emit('server_message', client_msg, broadcast=True)


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
def profile():
    player, days = "Username", 2
    if request.method == "POST":
        try:
            player = request.form['name_input']
        except:
            player = "Username"
        try:
            days = request.form['days_input']
        except:
            days = 2
    return render_template("profile.html", icon = randomTabIcon(), player_list = getTopPlayers(),
                           player_icons = topPlayerIcons(), player_profiler = MakeSkillsDeltaListing(player, days), player = player, tracker_active="active")

#A section for adding usernames
@app.route('/register', methods=["GET", "POST"])
def register():
    #Processes POSTS of registered player search and player registration
    reg_result = ""
    searched_player = ""

    return render_template("register.html", icon = randomTabIcon(), player_list = getTopPlayers(),
                           result = reg_result, result2 = searched_player, player_icons = topPlayerIcons(),
                           tracker_active = "active")

@app.route("/ge-buy", methods=["GET", "POST"])
def geBuy():
    ge_sell = getGEOffersFormatted("sell")

    minimum_price = -1
    maximum_price = -1
    if request.method == "POST":
        try:
            minimum_price = int(request.form['price_minimum'])
        except:
            pass
        else:
            if (minimum_price > 0):
                ge_sell = removeGEOffersByMinimumPrice(ge_sell, minimum_price)
        try:
            maximum_price = int(request.form['price_maximum'])
        except:
            pass
        else:
            if (maximum_price > 0):
                ge_sell = removeGEOffersByMaximumPrice(ge_sell, maximum_price)
    # print(ge_sell)

    ge_sell = alphabeticalGEOffers(ge_sell)
    ge_sell = orderGEOffersByTableOrder(ge_sell)

    return render_template("ge-buy.html", icon = randomTabIcon(), player_list = getTopPlayers(),
                           player_icons = topPlayerIcons(), geSellOffers = ge_sell, ge_active="active")

@app.route("/ge-sell", methods=["GET", "POST"])
def geSell():
    ge_buy = getGEOffersFormatted("buy")

    minimum_price = -1
    maximum_price = -1
    if request.method == "POST":
        try:
            minimum_price = int(request.form['price_minimum'])
        except:
            pass
        else:
            if (minimum_price > 0):
                ge_buy = removeGEOffersByMinimumPrice(ge_buy, minimum_price)
        try:
            maximum_price = int(request.form['price_maximum'])
        except:
            pass
        else:
            if (maximum_price > 0):
                ge_buy = removeGEOffersByMaximumPrice(ge_buy, maximum_price)
    print(ge_buy)

    ge_buy = alphabeticalGEOffers(ge_buy)
    ge_buy = orderGEOffersByTableOrder(ge_buy)

    return render_template("ge-sell.html", icon = randomTabIcon(), player_list = getTopPlayers(),
                           player_icons = topPlayerIcons(), geBuyOffers = ge_buy, ge_active="active")

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
        socketio.run(app, host = '0.0.0.0', port=5000, debug=True)
        # app.run(host = '0.0.0.0', threaded=True, port=5000, debug = False)
    else:
        socketio.run(app, host = '0.0.0.0', port=80)
        # app.run(host = '0.0.0.0', port=80, threaded=True, debug=False)

        #https://stackoverflow.com/questions/66069215/the-client-is-using-an-unsupported-version-of-the-socket-io-or-engine-io-protoco