from flask import request
from flask_socketio import emit, join_room, leave_room

def register_socketio_events(socketio):
    @socketio.on("connect")
    def handle_connect():
        emit("connected", {"message": "Connected to Flight Service WebSocket"})

    @socketio.on("disconnect")
    def handle_disconnect():
        pass

    @socketio.on("join")
    def handle_join(data):
        room = data.get("room")
        if not room:
            emit("error", {"message": "Room is required"})
            return
        join_room(room)
        emit("joined", {"room": room})

    @socketio.on("leave")
    def handle_leave(data):
        room = data.get("room")
        if not room:
            emit("error", {"message": "Room is required"})
            return
        leave_room(room)
        emit("left", {"room": room})