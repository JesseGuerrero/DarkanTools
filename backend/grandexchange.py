import requests
import json

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