"""
app.py
======
Project:    Real-Time Chat Application (starter)
Stack:      Flask, Flask-SocketIO, WebSockets (via engine.io), HTML/JS client

What you will build:
    A multi-client chat room where messages appear instantly without polling.
    The browser uses the Socket.IO JavaScript client; the server uses
    Flask-SocketIO with event handlers for connect, disconnect, and chat.

How to run (from this directory):
    pip install -r requirements.txt
    python app.py

Then open http://127.0.0.1:5000 in two browser tabs.

Learning goals:
    - Real-time bidirectional communication (not request/response only)
    - Broadcasting messages to all connected clients (or rooms)
    - Optional: named rooms, private messages, typing indicators, persistence
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me-in-production"

# cors_allowed_origins="*" is convenient for local dev only — tighten for production.
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/")
def index():
    """Serve the chat page template."""
    return render_template("chat.html")


@socketio.on("connect")
def handle_connect():
    emit("system", {"msg": "You are connected. Say hello!"})


@socketio.on("disconnect")
def handle_disconnect():
    # Optional: broadcast that someone left (omit if you prefer quiet disconnects)
    pass


@socketio.on("chat_message")
def handle_chat_message(data):
    """Receive { "user": str, "text": str } and broadcast to every connected client."""
    if not isinstance(data, dict):
        return
    text = (data.get("text") or "").strip()
    user = (data.get("user") or "Guest").strip() or "Guest"
    if not text:
        return
    emit("chat_message", {"user": user, "text": text}, broadcast=True)


if __name__ == "__main__":
    print("Real-time chat starting at http://127.0.0.1:5000")
    print("Open two browser tabs to test broadcasting.\n")
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)
