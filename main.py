from bs4 import BeautifulSoup
import pandas as pd
import re
import requests
import csv
import json
import time
import datetime
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
def teamAbbrev(team_name):
    squads = {
        'Boston Celtics' : 'BOS',
        'Philadelphia 76ers' : 'PHI',
        'New York Knicks' : 'NY',
        'Brooklyn Nets' : 'BKN',
        'Toronto Raptors' : 'TOR',
        'Milwaukee Bucks' : 'MIL',
        'Cleveland Cavaliers' : 'CLE',
        'Chicago Bulls' : 'CHI',
        'Indiana Pacers' : 'IND',
        'Detroit Pacers' : 'DET',
        'Atlanta Hawks' : 'ATL',
        'Miami Heat' : 'MIA',
        'Washington Wizard' : 'WSH',
        'Orlando Magic' : 'ORL',
        'Charlotte Hornets' : 'CHA',
        'Denver Nuggets' : 'DEN',
        'Minnesota Timberwolves' : 'MIN',
        'Oklahoma City Thunder' : 'OKC',
        'Utah Jazz' : 'UTAH',
        'Portland Trailblazers' : 'POR',
        'Sacramento Kings' : 'SAC',
        'Phoenix Suns' : 'PHX',
        'Los Angeles Clippers' : 'LAC',
        'Los Angeles Lakers' : 'LAL',
        'Golden State Warriors' : 'GS',
        'Memphis Grizzlies' : 'MEM',
        'New Orleans Pelicans' : 'NO',
        'Dallas Mavericks' : 'DAL',
        'Houston Rockets' : 'HOU',
        'San Antonio Spurs' : 'SA',
        'New Orleans Hornets' : 'NO',
        'Seattle SuperSonics' : 'SEA'
    }
    return squads[team_name]
def monthConvert(month):
    monthConvert = {
        'January' : 1,
        'February' : 2,
        'March' : 3,
        'April' : 4,
        'May' : 5,
        'June' : 6,
        'July' : 7,
        'August' : 8,
        'September' : 9,
        'October' : 10,
        'November' : 11,
        'December' : 12
    }
    return monthConvert[month]
def countryConvert(country):
    countryConvert = {
        'AO' : 'Angola',
        'AR' : 'Argentina',
        'AT' : 'Austria',
        'AU' : 'Australia',
        'BS' : 'Bahamas',
        'BA' : 'Bosnia & Herzegovina',
        'BR' : 'Brazil',
        'CA' : 'Canada',
        'CM' : 'Cameroon',
        'CN' : 'China',
        'HR' : 'Croatia',
        'CZ' : 'Czechia',
        'DO' : 'Dominican Republic',
        'CD' : 'D.R.C.',
        'FI' : 'Finland',
        'FR' : 'France',
        'DE' : 'Germany',
        'GE' : 'Georgia',
        'GR' : 'Greece',
        'GN' : 'Guinea',
        'IL' : 'Israel',
        'IT' : 'Italy',
        'JM' : 'Jamaica',
        'JP' : 'Japan',
        'LV' : 'Latvia',
        'LT' : 'Lithuania',
        'ME' : 'Montenegro',
        'NG' : 'Nigeria',
        'MK' : 'North Macedonia',
        'NZ' : 'New Zealand',
        'PL' : 'Poland',
        'PT' : 'Portugal',
        'CG' : 'Republic of the Congo',
        'SN' : 'Senegal',
        'SD' : 'Sudan',
        'RS' : 'Serbia',
        'SI' : 'Slovenia',
        'ES' : 'Spain',
        'LC' : 'St. Lucia',
        'CH' : 'Switzerland',
        'TR' : 'Turkey',
        'UA' : 'Ukraine',
        'US' : 'U.S.A.',
        'GB' : 'United Kingdom'
    }
    return countryConvert[country]

"""
Finds all active NBA players (including rookies)
Puts them in big dictionary where their name is the key
"""
def find_active_players():
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
                collection = soup.findAll('td', attrs={'class': 'left ', 'data-stat': 'player'})

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
    # save_data('players.txt', players)
    return players

"""
Takes in dictionary of player
Fills their dictionary bio, stats, accolades, contract, etc
"""
def set_player_data(player):
    html_doc = get_soup('https://www.basketball-reference.com' + player['url'])
    """
    Fill in bio section first
    """
    bio = html_doc.find(id = 'meta').findAll('p')
    for item in bio:
        item = ' '.join(item.getText().split())
        if 'Position' in item: # get position(s) and shooting hand
            item = item.replace('and ', '')
            hand = item.find('Shoots: ')
            player['bio']['hand'] = item[hand + 8]

            position = item[10 : hand-3]

            if ', ' in position: # 3+ positions
                player['bio']['position'] = position.split(', ')
            else: # 2- positions "Point Guard Shooting Guard"
                position = position.split() # [Point, Guard, Shooting, Guard]
                del position[1::2] # [Point, Shooting]
                for index in range(len(position)):
                    if position[index] == 'Point' or position[index] == 'Shooting':
                        position[index] += ' Guard'
                    elif position[index] == 'Small' or position[index] == 'Power':
                        position[index] += ' Foward'
                player['bio']['position'] = position
        elif item[0].isdigit(): # height (inches) and weight (pounds)
            height = item[:item.find(',')]
            height = int(height[0]) * 12 + int(height[-1])
            weight = item[item.find(',') + 2: item.find('l')]

            player['bio']['height'] = height
            player['bio']['weight'] = int(weight)
        elif 'Born' in item: # birthday + age
            bdate = item[item.find(':') + 2: item.find('in') - 1].replace(',', '')
            bloc = item[-2:].upper()
            bmonth, bday, byear = bdate.split(' ')
            age = datetime.datetime.now().year - int(byear) - 1
            if monthConvert(bmonth) < datetime.datetime.now().month and int(bday) < datetime.datetime.now().day:
                age += 1
            
            player['bio']['birth-info'] = {
                'birth-month' : bmonth,
                'birth-day' : int(bday),
                'birth-year' : int(byear)
            }
            player['bio']['age'] = int(age)
            player['bio']['country'] = countryConvert(bloc)
        elif 'College' in item: # might need to plan for if player went to multiple colleges
            player['bio']['school'] = item[9:]
        elif 'High School' in item and 'school' not in player['bio']: # might need to fix for multiple HS's like Jalen Green
            player['bio']['school'] = item[item.find(':') + 2 : item.find(' in ')]
        elif 'Draft' in item: # get draft info
            item = item[item.find(':') + 2:]
            team, round, pick, draft = item.split(', ')
            draft = draft[:4]
            round = round[0]
            pick = round[round.find('(') + 1]
            player['bio']['draft-info'] = {
                'round' : int(round),
                'pick' : int(pick),
                'year' : int(draft),
                'team' : teamAbbrev(team)
            }
        elif 'NBA Debut' in item: # get NBA debut date
            player['bio']['debut'] = item[item.find(':') + 2:]
        elif 'Experience' in item: # get years of NBA exp.
            item = item[item.find(':') + 2:].split()
            player['bio']['experience'] = int(item[0])

    jersey_num = html_doc.findAll('svg', {'class' : 'jersey'})
    jersey_num = None if not jersey_num else int(jersey_num[-1].getText()) # get most recent jersey number
    player['bio']['jersey-num'] = jersey_num

    if 'draft-info' not in player['bio']: player['bio']['draft-info'] = {'round' : 'Undrafted'}

    return player



if __name__ == '__main__':
    print("maybe")
    players = retrieve_data('players.txt')
    # set_player_data(players['Kevin Durant'])
    # print(json.dumps(players['Kevin Durant'], indent=4))
    # inp = input('Which player?\n')

    # while inp != '?':
    #     print(inp)
    #     try:
    #         set_player_data(players[inp])
    #         print(json.dumps(players[inp], indent=4))
    #         print('\n-------------------------------\n')
    #     except KeyError:
    #         print('Invalid name')
        
    #     inp = input('Which player?\n')
    

    # FORMAT FOR MAIN METHOD IN FULL
    # players = find_active_players()
    # save_data('players.txt', players)
    # for player in players.keys():
    #     players[player] = set_player_data(players[player])
