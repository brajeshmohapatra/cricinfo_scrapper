import requests
import warnings
import pandas as pd
from bs4 import BeautifulSoup
warnings.filterwarnings('ignore')
url = 'https://www.espncricinfo.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
team_names, team_links = [], []
teams = soup.find_all('a', attrs = {'class' : 'nav-link dropdown-item'})
teams = teams[20 : 32]
for team in teams:
    team_names.append(team.text)
    link = team.get('href')
    team_links.append('https://www.espncricinfo.com/ci/content/player/country.html?country=' + link.split('-')[-1])
Teams = pd.DataFrame()
Teams['Teams'] = team_names
Teams['Links'] = team_links
player_country, player_names, player_codes = [], [], []
for link in Teams['Links']:
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    players_list = soup.find_all('td', attrs = {'class' : 'divider'})
    t_list = []
    for player in players_list:
        t_list.append(player.find('a'))
    players_list = t_list
    for player in players_list:
        player_country.append(Teams.loc[Teams.Links == link]['Teams'].values[0])
        player_names.append(player.text)
        player_codes.append(player.get('href').split('/')[4].split('.')[0])
Players = pd.DataFrame()
Players['Country'] = player_country
Players['Players'] = player_names
Players['Codes'] = player_codes
Players.drop_duplicates(inplace = True)
print('Number of Players found: ', Players.shape[0])
print('=' * 100)
batting = ['country', 'player', 'matches', 'innings', 'not_outs', 'runs', 'highest_score', 'average', 'balls_faced', 'strike_rate', 'centuries', 'half_centuries', 'ducks', 
           'boundaries', 'sixes']
fc_bowling = ['country', 'player', 'matches', 'innings', 'overs', 'maidens', 'runs', 'wickets', 'best_bowling_innings', 'best_bowling_match', 'average', 'economy', 
              'strike_rate', 'fi_fers', 'ten_fers']
lo_bowling = ['country', 'player', 'matches', 'innings', 'overs', 'maidens', 'runs', 'wickets', 'best_bowling_innings', 'average', 'economy', 'strike_rate', 'four_fers', 
              'fi_fers']
Test_Batting = pd.DataFrame(columns = batting)
ODI_Batting = pd.DataFrame(columns = batting)
T20I_Batting = pd.DataFrame(columns = batting)
Test_Bowling = pd.DataFrame(columns = fc_bowling)
ODI_Bowling = pd.DataFrame(columns = lo_bowling)
T20I_Bowling = pd.DataFrame(columns = lo_bowling)
format_classes = [1, 2, 3]
stats_types = ['batting', 'bowling']
counter = 1
for p_code in Players['Codes']:
    for format_class in format_classes:
        for stats_type in stats_types:
            url = 'https://stats.espncricinfo.com/ci/engine/player/' + str(p_code) + '.html?class=' + str(format_class) + ';template=results;type=' + stats_type
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            infos = soup.find_all('tr', attrs = {'class' : 'data1'})
            stats = []
            for info in infos:
                stats.append(info.text.split('\n'))
            if len(stats) > 1:
                if stats_type == 'batting':
                    stats = stats[0][-17 : -2]
                    stats[0] = Players.loc[Players.Codes == p_code]['Country'].values[0]
                    stats[1] = Players.loc[Players.Codes == p_code]['Players'].values[0]
                    data = pd.DataFrame([stats], columns = batting)
                    if format_class == 1:
                        Test_Batting = pd.concat([Test_Batting, data], axis = 0)
                    elif format_class == 2:
                        ODI_Batting = pd.concat([ODI_Batting, data], axis = 0)
                    else:
                        T20I_Batting = pd.concat([T20I_Batting, data], axis = 0)
                else:
                    if format_class == 1:
                        stats = stats[0][-17 : -2]
                        stats[0] = Players.loc[Players.Codes == p_code]['Country'].values[0]
                        stats[1] = Players.loc[Players.Codes == p_code]['Players'].values[0]
                        data = pd.DataFrame([stats], columns = fc_bowling)
                        Test_Bowling = pd.concat([Test_Bowling, data], axis = 0)
                    else:
                        stats = stats[0][-16 : -2]
                        stats[0] = Players.loc[Players.Codes == p_code]['Country'].values[0]
                        stats[1] = Players.loc[Players.Codes == p_code]['Players'].values[0]
                        data = pd.DataFrame([stats], columns = lo_bowling)
                        if format_class == 2:
                            ODI_Bowling = pd.concat([ODI_Bowling, data], axis = 0)
                        else:
                            T20I_Bowling = pd.concat([T20I_Bowling, data], axis = 0)        
    print('Player', counter, 'done.')
    counter += 1
Test_Batting.to_csv('Test Batting.csv', index = None)
ODI_Batting.to_csv('ODI Batting.csv', index = None)
T20I_Batting.to_csv('T20I Batting.csv', index = None)
Test_Bowling.to_csv('Test Bowling.csv', index = None)
ODI_Bowling.to_csv('ODI Bowling.csv', index = None)
T20I_Bowling.to_csv('T20I Bowling.csv', index = None)