from flask import Flask
from flask_table import Table, Col
from markupsafe import escape
from flask import render_template


app = Flask(__name__)

class Player:
    def __init__(self, name, color):
        self.name = name
        self.score = 0
        self.health = 100
        self.ammo = 50
        self.accuracy = 100
        self.connected = False
        self.color = color

    def get_player_stats(self):
        return "Player :"
    

class ItemTable(Table):
    name = Col('Name')
    health = Col('Health')
    score = Col('Score')
    ammo = Col('Ammo')
    connected = Col('Connected')

headers = ['Name','Health', 'Score', 'Accuracy', 'Ammo', 'Connected']


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

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    
    p1 = players.get(username)
    attributes = [p1.name, p1.health, p1.score, str(p1.accuracy) + "%", p1.ammo, p1.connected]
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
    headers = ['Name', 'Score', 'Accuracy', 'Connected']
    # leader_board = ""
    # for name, player in players:
    #     player = players.get(name)
    #     attributes = [player.name, player.health, player.score, player.ammo, player.connected]
    #     leader_board += render_template('leaderboard.html',
    #                         headers = headers,
    #                         objects = attributes)
    # return leader_board
    return render_template('leaderboard.html',
                            headers = headers,
                            objects = players
                            )
    return "h"
    # return table.__html__()
    # return "<p>" + str(p1.score) + "</p>"