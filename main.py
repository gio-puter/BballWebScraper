from bs4 import BeautifulSoup
import pandas as pd
import re
import requests
import csv
import json
import time
# from urllib.request import urlopen


def get_soup(url):
    page = requests.get(url)
    page = page.text.replace("<!--", "").replace("-->", "")
    soup = BeautifulSoup(page, 'html.parser')
    return soup


def save_data(save_file, store_data, sort=False):
    with open(save_file, 'w') as save_data:
        save_data.write(json.dumps(store_data, sort_keys=sort, indent=4))


def retrieve_data(get_file):
    try:
        with open(get_file) as f:
            data = f.read()
        return json.loads(data)
    except:
        return None


# players = {}
def get_active_players():
    active_url = "https://www.basketball-reference.com/players/a"
    players = retrieve_data('players.txt')
    if (len(players == 691)):
        return players

    if players:  # jump ahead to next selection if already did url
        last_player = players.getKeys()[-6]
        last_letter = players[last_player]['bio']['lname'][0].lower()
        try:
            if len(players == 691) or players[last_player]['bio']['experience'] == 0:
                return players
        except:
            if last_letter == 'z':
                active_url = 'ROOKIES'
            else:
                active_url = active_url[:-1] + chr(ord(last_letter) + 1)
    else:
        players = {}

    requests = 0
    done = False
    while not done:
        if requests == 15:  # wait for 70 seconds every 15 requests to not get banned
            time.sleep(70)
            requests = 0
        else:  # find players
            if ord(active_url[-1]) <= ord('z'):  # find all active players
                soup = get_soup(active_url)
                collection = soup.find(id='players')

                if not collection:
                    done = True
                else:
                    for player in collection.findAll('strong'):  # add player to dictionary
                        url = player.find('a', href=True)['href']
                        name = player.getText().split(' ')
                        fname = name[0]
                        lname = name[1]
                        suffix = '' if len(name) <= 2 else name[2]
                        players[player.getText()] = {
                            'url': url,
                            'bio': {
                                'fname': fname,
                                'lname': lname,
                                'suffix': suffix
                            }
                        }
                    # go to next letter
                    active_url = active_url[:-1] + chr(ord(active_url[-1]) + 1)
                    requests += 1
            else:  # find 2023 draftees
                active_url = 'https://www.basketball-reference.com/draft/NBA_2023.html'
                soup = get_soup(active_url)
                collection = soup.findAll('td',
                                          attrs={
                                              'class': 'left ',
                                              'data-stat': 'player'
                                          })

                if collection is None:
                    done = True
                else:
                    for player in collection:  # add player to dictionary
                        url = player.find('a', href=True)['href']
                        name = player.getText().split(' ')
                        fname = name[0]
                        lname = name[1]
                        suffix = '' if len(name) <= 2 else name[2]
                        players[player.getText()] = {
                            'url': url,
                            'bio': {
                                'fname': fname,
                                'lname': lname,
                                'suffix': suffix,
                                'experience': 0
                            }
                        }
                    # add Chet Holmgren
                    players['Chet Holmgren'] = {
                        'url': '/players/h/holmgch01.html',
                        'bio': {
                            'fname': 'Chet',
                            'lname': 'Holmgren',
                            'experience': 0
                        }
                    }
                    done = True
    players = dict(sorted(players.items(), key=lambda x: x[1]['bio']['lname']))
    save_data('players.txt', players)
    return players


if __name__ == '__main__':
    print("maybe")
    # print(get_active_players())
