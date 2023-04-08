from flask import Flask
from flask_table import Table, Col
from markupsafe import escape


app = Flask(__name__)

class Player:
    def __init__(self, name, color):
        self.name = name
        self.score = 0
        self.health = 100
        self.ammo = 50
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


players = {'Bob': Player('Bob', color.get("blue")), 
            "Joe": Player('Joe', color.get("yellow")), 
            "Bill": Player('Bill', color.get("red"))}

# table = ItemTable(players)

# Print the html
# print(table.__html__())

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    
    table = ItemTable([players.get(username)])
    
    
    
    return table.__html__()
    return f'User {escape(username)}'

@app.route("/")
def hello_world():
    return "h"
    # return table.__html__()
    # return "<p>" + str(p1.score) + "</p>"