import matplotlib.pyplot as plt
from datetime import date, timedelta
from os.path import dirname as up
from os.path import join, realpath
import os
from random import shuffle

if __name__ != '__main__':
    from . import xp_tracker_backend as be


#TODO: Annotate
def xpTracker(stat_name, player1 = "", player2 = "", days = 7):
    #Static directory for the rest of the function. I used from imports to reduce size. It starts from this file
    staticDir = realpath(join(up(up(__file__)), "static"))

    #Convert stat number from option menu to string and days to string
    stat_name = be.Stat.skill_Name[int(stat_name)]
    days = int(days)

    #Create axis lists
    x1_axis = []
    x2_axis = []
    y1_axis = []
    y2_axis = []

    #Player toggle on and off if it works and does not
    p1 = True
    p2 = True

    #Get stat object list but if you fail, dont plot it
    try:
        stat_profile1 = be.get_file_stats(player1, stat_name, days)
    #Player 1 plotting disabled
    except:
        p1 = False

    #Get stat object list for player 2
    try:
        stat_profile2 = be.get_file_stats(player2, stat_name, days)
    #player 2 plotting disabled
    except:
        p2 = False

    #If both are false show a standard error image
    if p1 == False and p2 == False:
        try:
            #TODO: perhaps make 3 funny random error images
            if "win" in os.sys.platform:
                be.multiple_cmd(f"cd \"{staticDir}\"", "del graph.png", "copy tryagain.png graph.png")
            else:
                be.multiple_cmd(f"cd \"{staticDir}\"", "rm graph.png", "cp tryagain.png graph.png")
        except:
            return
        else:
            return

    #Get date and value elements but if player 1 is empty do not
    if p1:
        for stat in stat_profile1:
            x_element = str(stat.getDate())[-5:]
            x1_axis.append(x_element)

            y_element = stat.getValue()
            y1_axis.append(y_element)

    #get date and value elements but if player 2 is empty do not
    if p2:
        for stat in stat_profile2:
            x_element = str(stat.getDate())[-5:]
            x2_axis.append(x_element)

            y_element = stat.getValue()
            y2_axis.append(y_element)

    #Setup default colors
    COLOR = 'red'
    plt.rcParams['text.color'] = COLOR
    plt.rcParams['axes.labelcolor'] = COLOR
    plt.rcParams['xtick.color'] = COLOR
    plt.rcParams['ytick.color'] = COLOR

    #Get the internal portion and set it to black and make the title the stat_name
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.patch.set_facecolor('black')
    ax.set_title(stat_name.title())


    #player2 random color, default red if only 1 player
    random_color = "r"
    if p1 and p2:
        color = ['g', 'b', "c", "m", "y", "w"]
        shuffle(color)
        random_color = color.pop()

    #Plot both players unless they are toggled off. Also add names only if toggled on
    player_names = []
    if p1:
        ax.plot(x1_axis, y1_axis, color = 'r', marker='o', label="test")
        player_names.append(player1)
    if p2:
        ax.plot(x2_axis, y2_axis, color=random_color, marker='o', label="test")
        player_names.append(player2)

    #Now that the graph data is set, setup the players
    plt.legend(player_names, title="Players", facecolor = "#2b2b2b")

    #Color the legend text
    leg = ax.get_legend()
    leg.legendHandles[0].set_color('red')

    #If there are two players setup color of second to the random
    if len(player_names) > 1 :
        leg.legendHandles[1].set_color(random_color)

    #Lastly setup the ticks
    locs, labels = plt.yticks()
    for i, x in enumerate(locs):
        '''
        locs are the number values of the y-axis, it is actual xp in float format
        We turn to integer to take off decimal and then turn to string to format.
        The format function is used to add commas 
        
        x_element = 10000->10k, 10,000,000->10M
        
        to test you can change x-element in between this int() and str() cast below.
        Lastly labels is some kind of text object where you can set the text.
        When you re-insert it into ply.yticks() object it works but it requires locs too.
        '''
        x_element = int(x)
        x_element = str(x_element)

        #Now lets add a M for millions, IT EATS THE K and the 3 zeros
        if len(x_element) > 7:
            x_element = x_element[0:-6] + "M"

        #Now lets add a k for thousands
        elif len(x_element) > 4:
            x_element = x_element[0:-3] + "K"

        #The labels will override the values
        labels[i] = x_element

    #Put it back in with the string changes
    plt.yticks(locs, labels)

    #Go to the static folder and save the graph, make the face of the entire figure black with a little transparency
    plt.savefig(realpath(join(staticDir, 'graph.png')), facecolor=(0,0,0,.8))

#Imports act different depending on where main is.
if __name__ == '__main__':
    import xp_tracker_backend as be

    #The options menu gives a number from 0-25. With the Stat.skill_ID attribute we can convert string stats to ID
    xpTracker(be.Stat.skill_ID["Attack"], "", "Garlic Pork", int(14))
