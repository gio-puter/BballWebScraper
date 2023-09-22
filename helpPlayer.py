import datetime
from helperFunctions import monthConvert, countryConvert, cleanAwardID, cleanAwardText, getAward, yearConvert, salaryConvert


""" Adds player's metadata to their bio
Position
Height/Weight
Birthday/Nationality
Education
Draft Position
NBA Debut Date
Experience
Jersey Number
"""
def set_bio(html, player):
    bio = html.find(id = 'meta').findAll('p')
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

    jersey_num = html.findAll('svg', {'class' : 'jersey'})
    jersey_num = None if not jersey_num else int(jersey_num[-1].getText()) # get most recent jersey number
    player['bio']['jersey-num'] = jersey_num

    if 'draft-info' not in player['bio']: player['bio']['draft-info'] = {'round' : 'Undrafted'}


""" Adds player's awards to their awards list by year
e.g.
'awards' : {
    '2019-2020' : {
        'all-star' : True
    },
    '2020-2021' : {
        'all-star' : True
    },
    '2022-2023' : {
        'all-star' : True,
        'all-nba' : '3rd',
        'league-leader' : {'reb'}
    }
}
"""
def set_awards(html, player):
    awards = {}
    collection = html.find_all('div', {'class' : 'data_grid_box'})
    for category in collection:
        id = cleanAwardID(category.get('id'))
        if not id:
            continue
        
        category = category.find_all('td', {'class' : 'single'})
        for award in category:
            awardText = award.getText()
            if not cleanAwardText(awardText):
                continue
            
            award = getAward(id, awardText)
            if not award:
                continue
            
            year, awardText = award

            try:
                awards[year].append(awardText)
            except:
                awards[year] = []
                awards[year].append(awardText)
                
    player['awards'] = dict(sorted(awards.items()))

""" Adds player's contract info
Year
Salary
Option
Team
"""
def set_contract(html, player):
    contract = {}
    collection = html.find(id = 'div_contract')

    if collection is None:
        player['contract'] = contract
    
    collection = collection.find('div', {'class' : 'table_container'})
    if collection is None:
        player['contract'] = contract
    
    years = collection.find_all('th')[1:]
    salaries = collection.find_all('td')[1:]

    team = collection.find('a').getText()
    contract['team'] = team

    for i in range(len(years)):
        year = years[i].getText()
        year = yearConvert(year)

        salary = salaries[i].getText()
        salary = salaryConvert(salary)

        option = salaries[i].find('span').get('class')
        if option == []:
            option = ''
        elif 'tm' in option[0]:
            option = 'Team'
        elif 'pl' in option[0]:
            option = 'Player'

        contract[year] = {'salary': salary, 'option' : option}


    player['contract'] = contract



