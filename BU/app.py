from flask import Flask, render_template, request
from functions import get_player_scores, getDates, convertID

import pandas as pd
import matplotlib.pyplot as plt


prev = pd.read_csv("../static/PrevList.csv")



def plotSkill(player1:str, player2:str, skill:str, daysback:str):
    global prev
    list_player1_scores = []
    date_list = []
    error1 = False
    error2 = False
    color_list = []

    date_list = getDates(daysback)

    try:
        list_player1_scores = get_player_scores(player1, skill, daysback)
    except:
        print("Error in player1 score retrieval")
        error1 = True

    try:
        list_player2_scores = get_player_scores(player2, skill, daysback)
    except:
        print("Error in player2 score retrieval")
        error2 = True

    #Convert string num to name of skill string
    skill = convertID(skill)

    data2 = None
    df2 = pd.DataFrame()

    if error2 and not error1:
        new_row = pd.DataFrame({'Player1': player1, 'Player2': 'None', 'Skill': skill}, index=[0])
        prev = pd.concat([new_row, prev[:]]).reset_index(drop=True)
        prev.to_csv("static/PrevList.csv", index = False)

        data2 = {'Date': date_list,
                 player1: list_player1_scores,
                 }
        df2 = pd.DataFrame(data2, columns=['Date', player1])
        df2 = df2[['Date', player1]].groupby('Date').sum()
        print(df2)
        color_list = ['r']
    elif error1 and not error2:
        new_row = pd.DataFrame({'Player1': 'None', 'Player2': player2, 'Skill': skill}, index=[0])
        prev = pd.concat([new_row, prev[:]]).reset_index(drop=True)
        prev.to_csv("static/PrevList.csv", index = False)

        data2 = {'Date': date_list,
                 player2: list_player2_scores,
                 }
        df2 = pd.DataFrame(data2, columns=['Date', player2])
        df2 = df2[['Date', player2]].groupby('Date').sum()
        print(df2)
        color_list = ['g']
    elif not error1 and not error2:
        new_row = pd.DataFrame({'Player1': player1, 'Player2': player2, 'Skill': skill}, index=[0])
        prev = pd.concat([new_row, prev[:]]).reset_index(drop=True)
        prev.to_csv("static/PrevList.csv", index = False)

        data2 = {'Date': date_list,        
                 player1: list_player1_scores,
                 player2: list_player2_scores,
                 }
        df2 = pd.DataFrame(data2, columns=['Date', player1, player2])
        df2 = df2[['Date', player1, player2]].groupby('Date').sum()
        print(df2)
        color_list = ['r', 'g']
    else:
        print("exited without usernames")
        return





    COLOR = 'darkgrey'
    plt.rcParams['text.color'] = COLOR
    plt.rcParams['axes.labelcolor'] = COLOR
    plt.rcParams['xtick.color'] = COLOR
    plt.rcParams['ytick.color'] = COLOR



    #Remember a figure is the overall graph
    figure2 = plt.figure(figsize=(5, 4), dpi=100)
    ax2 = figure2.add_subplot(111) #A subplot is within the figure

    df2.plot(kind='line', legend=True, ax=ax2, color=color_list, marker='o', fontsize=10)

    ax2.set_title(skill.title() + ' XP')

    #Ax2 is the subplot
    ax2.patch.set_facecolor('black')
    #ax2.patch.set_alpha(0.75) #Might look nice

    #Legend text color
    leg = ax2.legend()
    for text in leg.get_texts():
        text.set_color("black")

    ###XTick
    locs, labels = plt.xticks()
    #print(locs)

    #This does not need to be understood
    for i in range(1, len(labels)):
        df_index = int(locs[i])
        try:
            xtick_value = list(df2.index)[df_index]
            labels[i].set_text(xtick_value)
        except:
            pass

    #for each in labels:
    #    print(each)

    plt.xticks(locs, labels)

    ##Y-Tick
    locs, labels = plt.yticks()

    i = 0
    for each in locs:
        print(each)
        each = int(each)
        if each < 0:
            labels[i].set_text("")
            print(each)
            i = i + 1
            continue
        if each > 10000:
            each = str(each)
            each = each[:-3]+"K"

        print(each)
        labels[i].set_text(each)
        i = i + 1

    plt.yticks(locs, labels)
    print(locs)

    #Facecolor changes the figure not the subplot
    figure2.savefig("static/test.png", facecolor='none', edgecolor='blue')

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


player1 = "Player1"
player2 = "Player2"
@app.route('/', methods=["GET", "POST"])
def button():
    global player1
    global player2
    if request.method == "POST":
        player1 = request.form['player1_input']
        player2 = request.form['player2_input']
        skill = request.form['skill_input']
        days = request.form['days_input']
        print("the skill is " + skill)
        plotSkill(player1, player2, skill, days)
        return render_template("home.html", current_player1 = player1, current_player2 = player2, prevDF = prev)
    return render_template("home.html", current_player1 = player1, current_player2 = player2, prevDF = prev)
