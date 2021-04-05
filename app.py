#Essentials
import werkzeug
from flask import Flask, render_template, request
from flask import send_file
from PIL import Image
import io

#Custom Modules
from backend.backend import *
from backend.DaemonDB import *

password = input("Database Password: ")
Thread(target=UpdateDB, args=(password,)).start()

#The Flask object constructor takes arguments
app = Flask(__name__)

#Removes caching -> removes hard resets.
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = os.path.join(pathlib.Path(__file__).parent.absolute(), "static", "essentialIgnored", "Uploads")
app.config['MAX_CONTENT_PATH'] = 100_000 #100KB file limit

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
    saved = ""
    if request.method == 'POST':
        uploadedFile = request.files['file']
        uploadedFile : werkzeug.datastructures.FileStorage

        appPath = pathlib.Path(__file__).parent.absolute()
        saveFilePath = os.path.join(appPath, "static", "essentialIgnored", "Uploads", getUploadNum() + "_" + uploadedFile.filename)

        uploadedFile.save(saveFilePath)
        print(uploadedFile)
        saved = "Your file has been saved!"

    return render_template("soundpage.html", soundFiles = getSoundFiles(), savetext = saved, icon = randomTabIcon(), player_list = getTopPlayers(),
                           player_icons = topPlayerIcons(), sound_active = "active")

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

@app.route("/ge")
def ge():
    ge_buy = getGEOffersFormatted("buy")
    ge_sell = getGEOffersFormatted("sell")
    return render_template("ge.html", icon = randomTabIcon(), player_list = getTopPlayers(),
                           player_icons = topPlayerIcons(), geBuyOffers = ge_buy, geSellOffers = ge_sell)

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