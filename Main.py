import requests
from flask import *

auth = "79fc5b42e506dc518f577c31fca1fc460135c3f2236e7dde5f25e1e5ef17e9c7"

url = "https://lksh-enter.ru"

reason = "Я добряк, я умею программировать и быстро учусь"


def matches():
    return requests.get(url + "/matches", headers = {"Authorization" : auth}).json()

def teams():
    return requests.get(url + "/teams", headers = {"Authorization" : auth}).json()

def teams_id(id):
    return requests.get(url + f"/teams/{id}", headers = {"Authorization" : auth}).json()

def players_id(id):
    return requests.get(url + f"/players/{id}", headers = {"Authorization" : auth}).json()

def match_id(id):
    params = {"match_id" : str(id)}
    return requests.get(url + f"/goals?", params = params, headers = {"Authorization" : auth}).json()

def start():
    players_ids = []
    players_list = []
    list_of_teams = teams()
    for i in list_of_teams:
        for j in i['players']:
            players_ids.append(j)
    for k in players_ids:
        player_raw = players_id(k)
        player = f"{player_raw["name"]} {player_raw["surname"]}"
        if player not in players_list:
            players_list.append(player)
    players_list.sort()
    return players_list

def stats(name):
    win = 0
    lose = 0
    goals = 0
    team_id = 0
    for i in teams():
        if i['name'] == name:
            team_id = i['id']
    if team_id == 0:
        return 0, 0, 0
    for j in matches():
        team_number = 0
        if j['team1'] == team_id:
            team_number = 1
        if j['team2'] == team_id:
            team_number = 2
        if team_number == 0:
            pass
        elif team_number == 1:
            goals = goals + j['team1_score'] - j['team2_score']
            if j['team1_score'] > j['team2_score']:
                win += 1
            elif j['team2_score'] > j['team1_score']:
                lose += 1
        elif team_number == 2:
            goals = goals + j['team2_score'] - j['team1_score']
            if j['team2_score'] > j['team1_score']:
                win += 1
            elif j['team1_score'] > j['team2_score']:
                lose += 1
    if win > 0:
        win = "+" + str(win)
    return win, lose, goals

def versus(player1_id, player2_id):
    n_of_versus = 0
    player1_team_id = []
    player2_team_id  = []
    for i in teams():
        if player1_id in i['players']:
            player1_team_id.append(i['id'])
        if player2_id in i['players']:
            player2_team_id.append(i['id'])
    if player1_team_id == [] or player2_team_id == []:
        return 0
    for j in matches():
        if j['team1'] in player1_team_id and j['team2'] in player2_team_id or j['team2'] in player1_team_id and j['team1'] in player2_team_id:
            n_of_versus += 1
    return n_of_versus

def goals(id):
    player_team_id = []
    for i in teams():
        if id in i['players']:
            player_team_id.append(i['id'])
    matches_ids = []
    for j in matches():
        if j['team1'] in player_team_id or j['team2'] in player_team_id:
            matches_ids.append(j['id'])
    goals_lib = []
    for k in matches_ids:
        for l in match_id(k):
            if l['player'] == id:
                match = l['match']
                minute = l['minute']
                goals_lib.append({'match' : match, 'time' : minute})
    return goals_lib

def reasoning():
    return requests.post(url + "/login", json = {"reason" : reason}, headers = {"Authorization" : auth})

def main_base():
    for a in start():
        print(a)
    while True:
        req = input()
        command = req.split()
        if command[0] == "stats?":
            name = ""
            may_append = False
            for i in str(req):
                if may_append:
                    if i != "\"":
                        name = name + i
                if i == "\"":
                    may_append = True
            rsp = stats(name)
            print(rsp[0], rsp[1], rsp[2])
        elif command[0] == "versus?":
            print(versus(int(command[1]), int(command[2])))

def main_advanced():
    app = Flask(__name__)

    @app.route('/stats')
    def stats_req():
        team = request.args.get('team_name')
        resp = stats(team)
        return str(resp)

    @app.route('/versus')
    def versus_req():
        player1 = request.args.get('player1_id')
        player2 = request.args.get('player2_id')
        resp = versus(int(player1), int(player2))
        return str(resp)

    @app.route('/goals')
    def goals_req():
        player_id = int(request.args.get('player_id'))
        resp = jsonify(goals(player_id))
        return resp

    if __name__ == '__main__':
        app.run(debug = True)

main_advanced()