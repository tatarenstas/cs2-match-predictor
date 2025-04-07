import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def average_player_stats(team):
      avg_rating = np.mean([stat['rating2.0'] for player in team['players'] for stat in player['stats']])
      avg_kd = np.mean([stat['kd'] for player in team['players'] for stat in player['stats']])
      return avg_rating, avg_kd

def process_match(match):
    features = {}
    features['team1_valve_points'] = match['team1']['valve_points']
    features['team2_valve_points'] = match['team2']['valve_points']
    features['team1_win_rate'] = match['team1']['win_rate']
    features['team2_win_rate'] = match['team2']['win_rate']
    features['team1_map_win_rate'] = match['team1']['map_win_rate']
    features['team2_map_win_rate'] = match['team2']['map_win_rate']
    features['team1_h2h_winrate'] = match['head_to_head']['team1_winrate']
    features['team2_h2h_winrate'] = match['head_to_head']['team2_winrate']
    features['team1_recent_wins'] = sum([1 if r == 'W' else 0 for r in match['team1']['recent_matches']])
    features['team2_recent_wins'] = sum([1 if r == 'W' else 0 for r in match['team2']['recent_matches']])

    features['team1_avg_rating'], features['team1_avg_kd'] = average_player_stats(match['team1'])
    features['team2_avg_rating'], features['team2_avg_kd'] = average_player_stats(match['team2'])
    features['result'] = 1 if match['result'] == 'team1' else 0
    return features

def prepare_dataset(data):
    dataset = [process_match(match) for match in data]
    return pd.DataFrame(dataset)

data = load_data('hltv_data.json')
df = prepare_dataset(data)

X = df.drop(columns=['result'])
y = df['result']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy:.2f}')

joblib.dump(model, 'cs2_model.pkl')
print("Model saved as cs2_model.pkl")