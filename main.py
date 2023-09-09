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
        'Detroit Pistons' : 'DET',
        'Atlanta Hawks' : 'ATL',
        'Miami Heat' : 'MIA',
        'Washington Wizards' : 'WSH',
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
        'Seattle SuperSonics' : 'SEA',
        'Charlotte Bobcats' : 'CHA',
        'New Jersey Nets' : 'NJ'
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
        'AG' : 'Antigua and Barbuda',
        'AT' : 'Austria',
        'AU' : 'Australia',
        'BS' : 'Bahamas',
        'BE' : 'Belgium',
        'BA' : 'Bosnia & Herzegovina',
        'BR' : 'Brazil',
        'CA' : 'Canada',
        'CM' : 'Cameroon',
        'CN' : 'China',
        'CO' : 'Colombia',
        'HR' : 'Croatia',
        'CZ' : 'Czechia',
        'DO' : 'Dominican Republic',
        'CD' : 'D.R.C.',
        'FI' : 'Finland',
        'FR' : 'France',
        'GA' : 'Gabon',
        'DE' : 'Germany',
        'GE' : 'Georgia',
        'GR' : 'Greece',
        'GN' : 'Guinea',
        'HT' : 'Haiti',
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
        'DR' : 'Quebec',
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
    # if (len(players == 691)):
    #     return players

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
    # save_data('players.txt', players)
    return players

"""
Takes in dictionary of player
Fills their dictionary bio, stats, accolades, contract, etc
"""
def set_player_data(player):
    html_doc = get_soup('https://www.basketball-reference.com' + player['url'])
    """
    Bio Section
    """
    bio = html_doc.find(id = 'meta').findAll('p')
    for item in bio:
        item = ' '.join(item.getText().split())
        if 'Position' in item: # get position(s) and shooting hand
            item = item.replace('and ', '')
            hand = item.find('Shoots: ')
            player['bio']['hand'] = item[hand + 8]

            position = item[item.find(':') + 2 : hand-3]

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
            if monthConvert(bmonth) < datetime.datetime.now().month:
                age += 1
            elif monthConvert(bmonth) == datetime.datetime.now().month and int(bday) <= datetime.datetime.now().day:
                age += 1
            
            player['bio']['birth-info'] = {
                'birth-month' : bmonth,
                'birth-day' : int(bday),
                'birth-year' : int(byear)
            }
            player['bio']['age'] = int(age)
            try:
                player['bio']['country'] = countryConvert(bloc)
            except:
                print("Don't know what " + bloc + " is")
                inp = input("Country?\n")
                player['bio']['country'] = inp
                print("Got it")
        elif 'College' in item: # show multiple colleges if applicable
            player['bio']['school'] = item[item.find(':') + 2:]
        elif 'High School' in item and 'school' not in player['bio']: #  might need to fix for multiple HS's like Jalen Green
            player['bio']['school'] = item[item.find(':') + 2 : item.find(' in ')]
        elif 'Draft' in item: # get draft info
            item = item[item.find(':') + 2:]
            team, round, pick, draft = item.split(', ')
            draft = draft[:4]
            pick = round[round.find('(') + 1:]
            if pick[1].isdigit():
                pick = int(pick[0] + pick[1])
            else:
                pick = pick[0]

            round = round[0]
            player['bio']['draft-info'] = {
                'round' : int(round),
                'pick' : int(pick),
                'year' : int(draft),
                'team' : team
            }
        elif 'NBA Debut' in item: # get NBA debut date
            player['bio']['debut'] = item[item.find(':') + 2:]
        elif 'Experience' in item: # get years of NBA exp.
            item = item[item.find(':') + 2:].split()
            if item[0] == 'Rookie':
                player['bio']['experience'] = 0
            else:
                player['bio']['experience'] = int(item[0])

    jersey_num = html_doc.findAll('svg', {'class' : 'jersey'})
    jersey_num = None if not jersey_num else int(jersey_num[-1].getText()) # get most recent jersey number
    player['bio']['jersey-num'] = jersey_num

    if 'draft-info' not in player['bio']: player['bio']['draft-info'] = {'round' : 'Undrafted'}

    """
    Awards Section
    """


    return player



if __name__ == '__main__':
    print("maybe")
    
    players = retrieve_data('players.txt')
    length = float(len(players))
    reqs = 0
    for player in players:
        if reqs % 18 == 0 and reqs > 0:
            print('{:.2f}'.format(reqs/length))
            print('Pausing...')
            time.sleep(65)
            
        print(players[player]['url'])
        set_player_data(players[player])
        reqs += 1
    
    print('Done')
    print('Initializing prompt stuff...')
    time.sleep(5)

    inp = input('Which player?\n')

    while inp != '?':
        try:
            print(json.dumps(players[inp], indent=4))
            print('\n-------------------------------\n')
        except KeyError:
            print('Invalid name')
        
        inp = input('Which player?\n')
    

    # FORMAT FOR MAIN METHOD IN FULL
    # players = find_active_players()
    # for player in players:
    #     set_player_data(players[player])
    # save_data('players.txt', players)
