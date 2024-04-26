from flask import Flask, render_template
from flask_socketio import SocketIO, emit

import zmq
import time
import json
import threading

context = zmq.Context()

# Create a ZeroMQ publisher
publisher = context.socket(zmq.PUB)
publisher.bind("tcp://*:5555")

# Create a ZeroMQ subscriber
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://0.0.0.0:5556")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

def publishData(topic,data):
    global publisher
    publisher.send_string(topic + " " + json.dumps(data))

app = Flask(__name__, static_url_path="/static", static_folder="static")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/register_service")
def register_service():
   return app.send_static_file("register_service.json")

@socketio.on('btn')
def handle_message(msg):
    print('button: ' + str(msg[0]) + '   ' + str(msg[1]))
    publishData("btn",{"id":msg[0],"value":msg[1]})

@socketio.on('key')
def handle_message(msg):
    print('key: ' + str(msg[0]) + '   ' + str(msg[1]))
    publishData("key",{"id":msg[0],"value":msg[1]})

@socketio.on('axi')
def handle_message(msg):
    print('axis: ' + str(msg[0]) + '   ' + str(msg[1]))
    publishData("axi",{"id":msg[0],"value":msg[1]})

def subscriberThread():
    global socketio
    print("Starting subscriber thread...")
    while True:
        data = subscriber.recv_string()
        
        if(data == 'serial active'):
            print("welcome, serial node")
            socketio.emit('serialstatus', 'active')

        if(data == 'serial failedToConnect'):
            print("serial failed to connect")
            socketio.emit('serialstatus', 'failed')

if __name__ == '__main__':
    subThread = threading.Thread(target=subscriberThread, daemon=True)
    subThread.start()
    socketio.run(app, allow_unsafe_werkzeug=True, host="0.0.0.0", port=5000)