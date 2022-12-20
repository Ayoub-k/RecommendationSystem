import flask
from flask_cors import CORS
from cnx_db import *
from flask_socketio import SocketIO

app = flask.Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app)
# app.config["DEBUG"] = True


@app.route('/recommandation/<string:username>', methods=['GET'])
def recommandation(username: str):
    livre = {}
    if test_user(username):
        livre = all_book_recommanded(username)
    return livre


socketio.run(app)