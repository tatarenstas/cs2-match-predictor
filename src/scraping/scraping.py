import time
import json
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from datetime import datetime, timedelta

month_dict = {1: 'january', 2: 'february', 3: 'march', 4: 'april', 5: 'may', 6: 'june', 7: 'july', 8: 'august', 9: 'september', 10: 'october', 11: 'november', 12: 'december'}
map_player_dict = {'trn': 'Train', 'nuke': 'Nuke', 'd2': 'Dust2', 'mrg': 'Mirage', 'inf': 'Inferno', 'anc': 'Ancient', 'anb': 'Anubis', 'vtg': 'Vertigo'}
map_team_dict = {'Dust2': 31, 'Mirage': 32, 'Inferno': 33, 'Nuke': 34, 'Train': 35, 'Vertigo': 46, 'Ancient': 47, 'Anubis': 48}
reverse_map_team_dict = {v: k for k, v in map_team_dict.items()}

driver = uc.Chrome()

def fetch_page(url):
    driver.get(url)
    html = driver.page_source
    return BeautifulSoup(html, "html.parser")

def load_processed_matches():
    try:
        with open('processed_matches.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_processed_matches(matches):
    with open('processed_matches.json', 'w') as f:
        json.dump(matches, f, indent=4)

def match_exists(match_url, processed_matches):
    return match_url in processed_matches

def save_match_data(match_data):
    try:
        with open("hltv_data.json", "r") as f:
            existing_data = json.load(f)
            if not isinstance(existing_data, list):
                existing_data = []
    except FileNotFoundError:
        existing_data = []

    existing_data.append(match_data)

    with open("hltv_data.json", "w") as f:
        json.dump(existing_data, f, indent=4)

def get_valve_points(url):
    html = fetch_page(url)
    item = html.find(class_='teamLineExpanded')

    if item is None:
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

def get_match_stats(url, map_code):
    html = fetch_page(url)
    unix = int(html.find("span", {"data-unix": True})["data-unix"]) / 1000
    date = datetime.fromtimestamp(unix) - timedelta(days=1)

    team1 = html.find(class_='team-left')
    team1_name = team1.find('a')['href'].split('/')[-1]
    team1_id = team1.find('a')['href'].split('/')[-2]
    team2 = html.find(class_='team-right')
    team2_name = team2.find('a')['href'].split('/')[-1]
    team2_id = team2.find('a')['href'].split('/')[-2]

    team1_stats = get_team_stats(team1_name, team1_id, date, map_code)
    team2_stats = get_team_stats(team2_name, team2_id, date, map_code)

    table1, table2 = html.find_all(class_='totalstats')

    players = [*table1.find_all(class_='st-player'), *table2.find_all(class_='st-player')]
    players_list = []

    for player in players:
        player_name = player.find("a")["href"].split('/')[-1]
        player_id = player.find("a")["href"].split('/')[-2]
        players_list.append({"name": player_name, "stats": get_player_stats(player_name, player_id, date)})

    result = "team1" if html.find(class_='team-left').find(class_='won') else "team2"

    head_to_head_url = html.find(class_='match-page-link')['href']
    head_to_head_stats = get_head_to_head_stats(f"https://www.hltv.org{head_to_head_url}")

    match_data = {
        "date": date.strftime('%Y-%m-%d'),
        "map": reverse_map_team_dict[map_code],
        "team1": {
            "name": team1_name,
            "valve_points": team1_stats[0],
            "win_rate": team1_stats[1],
            "map_win_rate": team1_stats[2],
            "recent_matches": get_recent_matches(team1_name, team1_id, date),
            "players": players_list[:5]
        },
        "team2": {
            "name": team2_name,
            "valve_points": team2_stats[0],
            "win_rate": team2_stats[1],
            "map_win_rate": team2_stats[2],
            "recent_matches": get_recent_matches(team2_name, team2_id, date),
            "players": players_list[5:]
        },
        "head_to_head": {
            "team1_winrate": 0 if head_to_head_stats[0] + head_to_head_stats[1] == 0 else round(head_to_head_stats[0] / (head_to_head_stats[0] + head_to_head_stats[1]) * 100, 1),
            "team2_winrate": 0 if head_to_head_stats[0] + head_to_head_stats[1] == 0 else round(head_to_head_stats[1] / (head_to_head_stats[0] + head_to_head_stats[1]) * 100, 1)
        },
        "result": result
    }

    save_match_data(match_data)

def get_dataset_by_team_matches(url, count):
    processed_matches = load_processed_matches()

    html = fetch_page(url)
    matches = html.find(class_='stats-table').find_all("tr", class_=["group-1", "group-2"], limit=count)

    for match in matches:
        start = time.time()

        match_url = match.find(class_='time').find('a')['href'].split('?')[-2]
        match_url = f"https://www.hltv.org{match_url}"
        if match_exists(match_url, processed_matches):
            print(f"Match exist : {match_url}")
            continue

        map_name = match.find(class_='statsMapPlayed').text.strip()
        get_match_stats(match_url, map_team_dict[map_name])

        processed_matches.append(match_url)
        save_processed_matches(processed_matches)

        print(f"Time taken: {round(time.time() - start)} seconds")

def create_dataset(count_teams):
    date = datetime.now() - timedelta(days=1)
    url = f"https://www.hltv.org/valve-ranking/teams/{date.year}/{month_dict[date.month]}/{date.day}"

    html = fetch_page(url)
    item = html.find(class_='ranking')
    team_links = item.find_all(class_='moreLink', limit=count_teams)

    teams_match_pages = []
    for team_link in team_links[27:]:
        team_id = team_link['href'].split('/')[-2]
        team_name = team_link['href'].split('/')[-1]
        print(team_name)
        res_url = f"https://www.hltv.org/stats/teams/matches/{team_id}/{team_name}"

        teams_match_pages.append(res_url)

    return teams_match_pages

if __name__ == "__main__":
    teams_match_pages = create_dataset(30)

    for team_match_page in teams_match_pages:
        print(team_match_page.split('/')[-1])
        get_dataset_by_team_matches(team_match_page, 100)