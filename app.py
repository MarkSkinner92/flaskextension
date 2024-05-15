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
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
subscriber.bind("tcp://*:5556")

def publishJSON(topic,data):
    global publisher
    publisher.send_string(topic + " " + json.dumps(data))

def publishMessage(topic,message):
    global publisher
    publisher.send_string(topic + " " + message)

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
    publishJSON("man/btn",{"id":msg[0],"value":msg[1]})

@socketio.on('key')
def handle_message(msg):
    print('key: ' + str(msg[0]) + '   ' + str(msg[1]))
    publishJSON("man/key",{"id":msg[0],"value":msg[1]})
    publishMessage("serial", "1" if msg[1] == 1 else "0")

@socketio.on('axi')
def handle_message(msg):
    print('axis: ' + str(msg[0]) + '   ' + str(msg[1]))
    publishJSON("man/axis",{"id":msg[0],"value":msg[1]})

def backgroundThread():
    global socketio
    while True:

        data = subscriber.recv_string()
        parts = data.split(" ", 1)
        message = parts[1]
        path = parts[0]

        splitPath = path.split('/', 1)
        protocol = splitPath[0]
        subPath = splitPath[1] if len(splitPath) > 1 else ""

        if(protocol == 'web'):
            print("sending webdata: topic = " + subPath + "; message = " + message)
            socketio.emit(subPath, message)

        if(protocol == 'serial'):
            print("recieved serial data: " + message)

if __name__ == '__main__':
    threading.Thread(target=backgroundThread, daemon=True).start()
    socketio.run(app, allow_unsafe_werkzeug=True, host="0.0.0.0", port=5000)