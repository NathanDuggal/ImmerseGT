from flask import Flask
from flask_table import Table, Col
from markupsafe import escape
from flask import render_template
from flask import request, make_response
import json
import requests


app = Flask(__name__)

class Player:
    def __init__(self, name, color):
        self.name = name
        self.score = 0
        self.kills = 0
        self.deaths = 0
        self.health = 100
        self.ammo = 50
        self.accuracy = 100
        self.connected = False
        self.color = color

    def get_player_stats(self):
        return "Player :"
    


headers = ['Name','Health', 'Score', 'Kills', 'Deaths', 'Accuracy', 'Ammo', 'Connected']


color = {
        'blue': '002aff',
        'yellow': 'e1eb34',
        'green': '28fc03',
        'red': 'fc1703', 
        'purple': 'b503fc', 
        'orange': 'FF9733 ',
        'black' : 'FFFFFF',
        'light-blue': '0AE5E3', 
        'pink': 'FF95AE',
        'blue-green' : '95FFCA'}



players = {'Bob': Player('Bob', color.get("light-blue")), 
            "Joe": Player('Joe', color.get("yellow")), 
            "Bill": Player('Bill', color.get("red"))}

# table = ItemTable(players)

# Print the html
# print(table.__html__())


#for tesing
d = {}
for player_name in players:
    p1 = players.get(player_name)
    d[player_name] = {"Health" : p1.health - 20,
                      "Score" : p1.score - 20,
                      "Kills" : p1.score - 2,
                      "Deaths" : p1.score - 200,
                      "Accuracy" : p1.accuracy - 20,
                      "Ammo" : p1.ammo - 20,
                      "Connected" : p1.connected}
    

with open("output.json", "w") as f:
    json.dump(d, f)


# import requests
# url = 'https://google.com'
# payload = {'key1': 'value1', 'key2': 'value2'}

# # GET
# r = requests.get(url)

# # GET with params in URL
# r = requests.get(url, params=payload)

# # POST with form-encoded data
# r = requests.post(url, data=payload)

# # POST with JSON 
# import json
# r = requests.post(url, data=json.dumps(payload))

# # Response, status etc
# r.text
# r.status_code

@app.route('/request', methods=['POST', 'GET'])
def post():
    r = requests.post('http://127.0.0.1:5000/hello', json=d)
    # print(d)
    # print(r.text)
    return make_response("",200)
    return render_template('request.html')

@app.route('/hello', methods=['POST', 'GET'])
def update_players_stats():
    # print(request.get_json())
    # return
    # post()
    # print(443)
    
    # print(request.get_json(force=True))


    # data = json.load(request.get_json(force=True))
    data = request.get_json(force=True)
    # print(data["Bob"])
    # print(data)
    # with open("output.json", "r") as content:
    #     data = json.load(content)
    # if request.method == 'POST':
    #     data = request.get_json()
    #     print(data)
    for player_name in data:
        player = players.get(player_name)
        # print ("3  " + str(data[player_name]["Health"]))
        player.health = data[player_name]["Health"]
        player.score =  data[player_name]["Score"]
        player.kills =  data[player_name]["Kills"]
        player.deaths =  data[player_name]["Deaths"]
        player.accuracy =  data[player_name]["Accuracy"]
        player.ammo =  data[player_name]["Ammo"]
        player.connected =  data[player_name]["Connected"]
    return make_response("",200)


    # if request.method == 'POST':
    #     data = json.load(request.get_json(force=True))
        
    #     for player_name in data:
    #         player = players.get(player_name)
    #         player.health = player_name[0]
    #         player.score = player_name[1]
    #         player.accuracy = player_name[2]
    #         player.ammo = player_name[3]
    #         player.connected = player_name[4]

        # if valid_login(request.form['username'],
        #                request.form['password']):
        #     return log_the_user_in(request.form['username'])



@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    
    p1 = players.get(username)
    attributes = [p1.name, p1.health, p1.score, p1.kills, p1.deaths, str(p1.accuracy) + "%", p1.ammo, p1.connected]
    return render_template('playerStats.html',
                            headers = headers,
                            objects = attributes,
                            color = p1.color)
    table = ItemTable([players.get(username)])
    
    
    # return ItemTable([players.get(username)]).__html__()

    
    return '''<h1 style="color:  #002aff">''' + table.__html__() + "</h1>"
    
    
    
    
    
    return table.__html__()
    return f'User {escape(username)}'
# table = ItemTable(players)

@app.route("/")
def leader_board():
    headers = ['Name', 'Score', 'Kills', 'Deaths', 'Accuracy', 'Connected']
    # leader_board = ""
    # for name, player in players:
    #     player = players.get(name)
    #     attributes = [player.name, player.health, player.score, player.ammo, player.connected]
    #     leader_board += render_template('leaderboard.html',
    #                         headers = headers,
    #                         objects = attributes)
    # return leader_board
    update_players_stats()
    return render_template('leaderboard.html',
                            headers = headers,
                            objects = players
                            )
    return "h"
    # return table.__html__()
    # return "<p>" + str(p1.score) + "</p>"