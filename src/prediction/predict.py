import json
import joblib
import numpy as np
import pandas as pd

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def average_player_stats(team):
    avg_rating = np.mean([stat['rating2.0'] for player in team['players'] for stat in player['stats']])
    avg_kd = np.mean([stat['kd'] for player in team['players'] for stat in player['stats']])
    return avg_rating, avg_kd


def process_match(match_for_predict):
    features = {'team1_valve_points': match_for_predict['team1']['valve_points'],
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


match_for_predict = load_data('2381300.json')

model = joblib.load('cs2_model.pkl')
predicted_winner, team1_prob, team2_prob = predict_match(match_for_predict)

print(f'Predicted winner: {predicted_winner}')
print(f'Team1 win probability: {team1_prob:.2f}%')
print(f'Team2 win probability: {team2_prob:.2f}%')