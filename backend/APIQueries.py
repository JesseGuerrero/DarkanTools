def playerAPIQuery(player) -> tuple:
    '''
    Calls player from API and checks for error by accessing byte information.
    The GET request from HTTPS works even when there is no player. So we check
    after converting the byte file into a string by trying to access a known
    piece of information.

    :return: Tuple type (player existed in API, Actual Stat info)
    '''
    exists = False
    #=====----->The following was created with Postman
    url = "https://darkan.org/api/player/" + player.replace(" ", "_").lower()

    payload = {}
    headers= {}

    response = requests.request("GET", url, headers=headers, data = payload)

    #request, below, is the string representation of the player information
    request = response.text.encode('utf8')
    #=====----->

    #Load the API Request as a Python Dictionary
    player_info = json.loads(request)

    #"Stats" is a key. Inside that key is another dictionary of skills. If it does not exist, the GET was a failure
    try:
        player_info = player_info['stats'] #Remove everything else
    except:
        print("Player not found")
        pass
    else:
        print(f"{player} query success")
        exists = True
    return (exists, player_info)

def getGEOffers(buyorsell):
    '''
    Queries Darkan API then returns result as a list of dictionaries to be sorted by app.py

    Example dictionary item:
    {
        "itemId": 946,
        "itemName": "Knife",
        "owner": "sir_sick",
        "amountTotal": 1,
        "amountLeft": 1,
        "pricePerItem": 2
    }

    These can be either buy or sell
    '''
    url = f"https://darkan.org/api/ge/{buyorsell}"

    payload = {}
    headers= {}

    response = requests.request("GET", url, headers=headers, data = payload)

    request = (response.text.encode('utf8'))

    #Converts plaintext to dictionary of lists
    ge_offers = json.loads(request)
    return ge_offers


if __name__ == "__main__":
    print(getGEOffers("sell"))