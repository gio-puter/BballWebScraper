from bs4 import BeautifulSoup
import pandas as pd
import re
import requests
import csv
import json
import time
from helpPlayer import set_bio, set_awards, set_contract, set_stats
from helperFunctions import get_soup, save_data, retrieve_data, getTeamDict

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

    # Setting Player Stats
    set_stats(html_doc, player)

    return player

def find_active_teams():
    teams = {}

    teamDict = getTeamDict()

    nba_teams_url = "https://www.basketball-reference.com/leagues/NBA_2024.html"
    nba_teams_soup = get_soup(nba_teams_url)
    east_teams = nba_teams_soup.find(id = 'divs_standings_E').find('tbody').find_all('tr')
    west_teams = nba_teams_soup.find(id = 'divs_standings_W').find('tbody').find_all('tr')

    divison = ""
    for team in east_teams:
        if team.get('class')[0] == 'thead':
            divison = team.find('th').getText()
            continue
        
        team = team.find('th')
        team_name = team.find('a').getText()
        team_abbrev = teamDict[team_name]
        team_url = team.find('a', href=True)['href']
        team_divison = divison
        team_conf = "Eastern Conference"
        
        teams[team_name] = {
            "name" : team_name,
            "abbrev" : team_abbrev,
            "url" : team_url,
            "division" : team_divison,
            "conference" : team_conf
        }

    for team in west_teams:
        if team.get('class')[0] == 'thead':
            divison = team.find('th').getText()
            continue
        
        team = team.find('th')
        team_name = team.find('a').getText()
        team_abbrev = teamDict[team_name]
        team_url = team.find('a', href=True)['href']
        team_divison = divison
        team_conf = "Western Conference"

        teams[team_name] = {
            "name" : team_name,
            "abbrev" : team_abbrev,
            "url" : team_url,
            "division" : team_divison,
            "conference" : team_conf
        }

    return teams

def set_team_roster(team):
    html_doc = get_soup('https://www.basketball-reference.com' + team['url'])
    team_roster = html_doc.find(id = 'roster').find('tbody').find_all('tr')

    players = retrieve_data('players.txt')
    roster = []

    for player in team_roster:
        player = player.find('td')
        player_name = player.find('a').getText()
        player_url = player.find('a', href=True)['href']

        if player_name in players and players[player_name]['url'] == player_url:
            roster.append(player_name)
        else:
            print(player_name, player_url)

    return roster

def run_input():
    players = retrieve_data('players.txt')
    inp = input('Which player?\n')
    while inp != 'end':
        start = time.time()
        try:
            set_player_data(players[inp])
            print('\n-------------------------------\n')
            print(json.dumps(players[inp], indent=4))
            print('\n-------------------------------\n')
            end = time.time()
            print(end - start)
            print('\n-------------------------------\n')
        except KeyError:
            print('Invalid name. Try Again...')
            print('\n-------------------------------\n')
        
        inp = input('Which player?\n')

if __name__ == '__main__':
    print("------------------------------\n")

    teams = find_active_teams()

    requests = 0
    for team in teams:
        team = teams[team]
        if requests == 18:
            print("\nSleeping...\n")
            time.sleep(60)
            requests = 0

        team['roster'] = set_team_roster(team)
        requests += 1
    
    print(json.dumps(teams, indent=4))
    
    save_data('teams.txt', teams)

    # run_input()
    # player = {
    #     "bio": {
    #         "fname": "Chris",
    #         "lname": "Paul",
    #         "suffix": ""
    #     },
    #     "url": "/players/p/paulch01.html"
    # }
    
    # set_player_data(player)
    # print(json.dumps(player, indent=4))

    # FORMAT FOR MAIN METHOD IN FULL
    
    # players = retrieve_data('players.txt')
    # requests = 0
    # for player in players:
    #     if requests == 19:
    #         print("\nPausing\n")
    #         time.sleep(60)
    #         requests = 0

    #     set_player_data(players[player])
    #     print(player)
    #     requests += 1

    # save_data('bigger_data.txt', players)