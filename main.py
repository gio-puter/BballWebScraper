from bs4 import BeautifulSoup
import pandas as pd
import re
import requests
import csv
import json
import time
from helpPlayer import set_bio, set_awards, set_contract
from helperFunctions import get_soup, save_data, retrieve_data
# from urllib.request import urlopen

""" Finds all active NBA players (including rookies)
Puts them in big dictionary where their name is the key
"""
def find_active_players():
    active_url = "https://www.basketball-reference.com/players/a"
    players = retrieve_data('players.txt')

    if players: # jump ahead to next selection if already did url
        if 'Victor Wembanyama' in players:
            return players
        else:
            last_player = list(players.keys())[-6]
            last_letter = players[last_player]['bio']['lname'][0].lower()
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
            if ord(active_url[-1]) <= ord('z') and ord(active_url[-1]) >= ord('a'):  # find all active players
                soup = get_soup(active_url)
                collection = soup.find(id = 'players')

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
                collection = soup.findAll('td', attrs={'data-stat': 'player'})
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
                            'suffix': '',
                            'experience': 0
                        }
                    }
                    done = True
    players = dict(sorted(players.items(), key=lambda x: x[1]['bio']['lname']))
    return players

""" Fills player dictionary
Takes in dictionary of player
Fills their dictionary bio, stats, accolades, contract, etc
"""
def set_player_data(player):
    html_doc = get_soup('https://www.basketball-reference.com' + player['url'])

    # Setting Player Bio
    set_bio(html_doc, player)

    # Setting Player Awards
    set_awards(html_doc, player)

    # Setting Player Contract
    set_contract(html_doc, player)

    return player

if __name__ == '__main__':
    print("------------------------------")

    players = retrieve_data('players.txt')

    inp = input('Which player?\n')
    while inp != 'end':
        try:
            set_player_data(players[inp])
            print('\n-------------------------------\n')
            print(json.dumps(players[inp], indent=4))
            print('\n-------------------------------\n')
        except KeyError:
            print('Invalid name. Try Again...')
            print('\n-------------------------------\n')
        
        inp = input('Which player?\n')
    
    
    # FORMAT FOR MAIN METHOD IN FULL
    # players = find_active_players()
    # for player in players:
    #     set_player_data(players[player])
    # save_data('players.txt', players)
