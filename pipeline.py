import joblib
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from datetime import datetime, timedelta

month_dict = {1: 'january', 2: 'february', 3: 'march', 4: 'april', 5: 'may', 6: 'june', 7: 'july', 8: 'august', 9: 'september', 10: 'october', 11: 'november', 12: 'december'}
map_player_dict = {'trn': 'Train', 'nuke': 'Nuke', 'd2': 'Dust2', 'mrg': 'Mirage', 'inf': 'Inferno', 'anc': 'Ancient', 'anb': 'Anubis', 'vtg': 'Vertigo'}
map_team_dict = {'Dust2': 31, 'Mirage': 32, 'Inferno': 33, 'Nuke': 34, 'Train': 35, 'Vertigo': 46, 'Ancient': 47, 'Anubis': 48}
reverse_map_team_dict = {v: k for k, v in map_team_dict.items()}

team1_name = 'team1'
team2_name = 'team2'

driver = uc.Chrome()

def fetch_page(url):
    driver.get(url)
    html = driver.page_source
    return BeautifulSoup(html, "html.parser")

def get_valve_points(url):
    html = fetch_page(url)
    item = html.find(class_='teamLineExpanded')

    if (item is None):
        item = html.find_all(class_='points')[-1]
        pts = int(item.text.split(' ')[0].split('(')[1])-1
    else:
        pts = int(item.find(class_='points').text.split(' ')[0].split('(')[1])

    return pts

def get_winrate(url):
    html = fetch_page(url)
    stats = html.find_all(class_='large-strong')[1].text
    w, d, l = map(int, stats.split(" / "))

    if w + d + l == 0:
        return 0

    return round(w/(w +d +l) * 100, 1)

def get_map_winrate(url):
    html = fetch_page(url)
    map_stats = html.find_all(class_='stats-row')[1].find_all('span')[1].text
    w, d, l = map(int, map_stats.split(" / "))

    if w + d + l == 0:
        return 0

    return round(w/(w + d + l)*100, 1)

def get_player_stats(name, player_id, date):
    url = f"https://www.hltv.org/stats/players/matches/{player_id}/{name}?startDate={(date - timedelta(days=90)).strftime('%Y-%m-%d')}&endDate={date.strftime('%Y-%m-%d')}"
    html = fetch_page(url)
    matches = html.find(class_='stats-table').find_all("tr", class_=["group-1", "group-2"], limit=10)
    stats = []
    for match in matches:
        map_name = match.find(class_='statsMapPlayed').text.strip()
        k, d = map(int, match.find(class_='statsCenterText').text.strip().split('-'))
        rating = float(match.find(class_=["match-lost", "match-won"]).text.strip())
        stats.append({"rating2.0": rating, "kd": round(k / d, 2), "map": map_player_dict[map_name]})

    return stats

def get_team_stats(name, team_id, date, map_code):
    stats_url_by_date = f"https://www.hltv.org/valve-ranking/teams/{date.year}/{month_dict[date.month]}/{date.day}?teamId={team_id}"
    valve_pts = get_valve_points(stats_url_by_date)
    stats_team_url = f'https://www.hltv.org/stats/teams/{team_id}/{name}?startDate={(date - timedelta(days=90)).strftime("%Y-%m-%d")}&endDate={date.strftime("%Y-%m-%d")}'
    winrate = get_winrate(stats_team_url)
    stats_map_url = f'https://www.hltv.org/stats/teams/map/{map_code}/{team_id}/{name}?startDate={(date - timedelta(days=90)).strftime("%Y-%m-%d")}&endDate={date.strftime("%Y-%m-%d")}'
    map_winrate = get_map_winrate(stats_map_url)

    return valve_pts, winrate, map_winrate

def get_head_to_head_stats(url):
    html = fetch_page(url)
    head_to_head_item = html.find(class_='head-to-head')

    stats = head_to_head_item.find_all(class_='bold')
    w1, overtimes, w2 = [int(stat.text) for stat in stats]

    return [w1, w2]

def get_recent_matches(name, team_id, date):
    url = f"https://www.hltv.org/stats/teams/matches/{team_id}/{name}?startDate={(date - timedelta(days=90)).strftime('%Y-%m-%d')}&endDate={date.strftime('%Y-%m-%d')}"

    html = fetch_page(url)
    matches = html.find(class_='stats-table').find_all("tr", class_=["group-1", "group-2"], limit=10)
    recent_matches_list = []

    for match in matches:
        res = match.find(class_=["match-lost", "match-won"]).text.strip()
        recent_matches_list.append(res)

    recent_matches_list.reverse()
    return recent_matches_list

def prepare_match(url, map):
    html = fetch_page(url)
    unix = int(html.find(class_='date')['data-unix'])/1000
    date = datetime.fromtimestamp(unix) - timedelta(days=1)
    map_code = map_team_dict[map]

    global team1_name, team2_name
    team1 = html.find(class_='team1-gradient')
    team1_name = team1.find('a')['href'].split('/')[-1]
    team1_id = team1.find('a')['href'].split('/')[-2]

    team2 = html.find(class_='team2-gradient')
    team2_name = team2.find('a')['href'].split('/')[-1]
    team2_id = team2.find('a')['href'].split('/')[-2]

    team1_stats = get_team_stats(team1_name, team1_id, date, map_code)
    team2_stats = get_team_stats(team2_name, team2_id, date, map_code)

    team1_players = html.find_all(class_='lineup')[0].find(class_='players').find_all('tr')[1]
    team1_players = team1_players.find_all(class_='player-compare')
    team2_players = html.find_all(class_='lineup')[1].find(class_='players').find_all('tr')[1]
    team2_players = team2_players.find_all(class_='player-compare')

    team1_players_stats = []
    for team1_player in team1_players:
        player_id = team1_player['data-player-id']
        player_name = team1_player.text.strip()

        stats = get_player_stats(player_name, player_id, date)
        team1_players_stats.append({"name": player_name, "stats": stats})

    team2_players_stats = []
    for team2_player in team2_players:
        player_id = team2_player['data-player-id']
        player_name = team2_player.text

        stats = get_player_stats(player_name, player_id, date)
        team2_players_stats.append({"name": player_name, "stats": stats})

    head_to_head_stats = get_head_to_head_stats(url)

    match_data = {
        "date": date.strftime('%Y-%m-%d'),
        "map": reverse_map_team_dict[map_code],
        "team1": {
            "name": team1_name,
            "valve_points": team1_stats[0],
            "win_rate": team1_stats[1],
            "map_win_rate": team1_stats[2],
            "recent_matches": get_recent_matches(team1_name, team1_id, date),
            "players": team1_players_stats
        },
        "team2": {
            "name": team2_name,
            "valve_points": team2_stats[0],
            "win_rate": team2_stats[1],
            "map_win_rate": team2_stats[2],
            "recent_matches": get_recent_matches(team2_name, team2_id, date),
            "players": team2_players_stats
        },
        "head_to_head": {
            "team1_winrate": 0 if head_to_head_stats[0] + head_to_head_stats[1] == 0 else round(head_to_head_stats[0] / (head_to_head_stats[0] + head_to_head_stats[1]) * 100, 1),
            "team2_winrate": 0 if head_to_head_stats[0] + head_to_head_stats[1] == 0 else round(head_to_head_stats[1] / (head_to_head_stats[0] + head_to_head_stats[1]) * 100, 1)
        }
    }

    return match_data

def average_player_stats(team):
    avg_rating = np.mean([stat['rating2.0'] for player in team['players'] for stat in player['stats']])
    avg_kd = np.mean([stat['kd'] for player in team['players'] for stat in player['stats']])
    return avg_rating, avg_kd


def process_match(match_for_predict):
    features = {
        'team1_valve_points': match_for_predict['team1']['valve_points'],
        'team2_valve_points': match_for_predict['team2']['valve_points'],
        'team1_win_rate': match_for_predict['team1']['win_rate'],
        'team2_win_rate': match_for_predict['team2']['win_rate'],
        'team1_map_win_rate': match_for_predict['team1']['map_win_rate'],
        'team2_map_win_rate': match_for_predict['team2']['map_win_rate'],
        'team1_h2h_winrate': match_for_predict['head_to_head']['team1_winrate'],
        'team2_h2h_winrate': match_for_predict['head_to_head']['team2_winrate'],
        'team1_recent_wins': sum(1 if r == 'W' else 0 for r in match_for_predict['team1']['recent_matches']),
        'team2_recent_wins': sum(1 if r == 'W' else 0 for r in match_for_predict['team2']['recent_matches'])
    }

    features['team1_avg_rating'], features['team1_avg_kd'] = average_player_stats(match_for_predict['team1'])
    features['team2_avg_rating'], features['team2_avg_kd'] = average_player_stats(match_for_predict['team2'])

    return features


def predict_match(match_for_predict):
    match_df = pd.DataFrame([process_match(match_for_predict)])

    probabilities = model.predict_proba(match_df)[0]

    team1_prob = probabilities[1] * 100
    team2_prob = probabilities[0] * 100

    predicted_winner = 'team1' if team1_prob > team2_prob else 'team2'

    return predicted_winner, team1_prob, team2_prob


match_for_predict = prepare_match('https://www.hltv.org/matches/2381303/liquid-vs-virtuspro-pgl-bucharest-2025', 'Dust2')

model = joblib.load('model/cs2_model.pkl')
predicted_winner, team1_prob, team2_prob = predict_match(match_for_predict)

print(f'Predicted winner: {team1_name if predicted_winner == "team1" else team2_name}')
print(f'{team1_name} win probability: {team1_prob:.2f}%')
print(f'{team2_name} win probability: {team2_prob:.2f}%')