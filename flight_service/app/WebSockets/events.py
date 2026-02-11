from flask import request
from flask_socketio import emit, join_room, leave_room

def register_socketio_events(socketio):
    
    @socketio.on("connect")
    def handle_connect():
        print(f"✅ Client connected: {request.sid}")  # 🔥 Dodaj print
        emit("connected", {"message": "Connected to Flight Service WebSocket"})

    @socketio.on("disconnect")
    def handle_disconnect():
        print(f"❌ Client disconnected: {request.sid}")  # 🔥 Dodaj print

    @socketio.on("join_role_room")
    def handle_join_role(data):
        print(f"📨 Received join_role_room: {data}")  # 🔥 Dodaj print
        role = data.get("role")
        if not role:
            print("⚠️ No role provided")  # 🔥 Dodaj print
            emit("error", {"message": "Role is required"})
            return
        
        room = f"role_{role}"
        join_room(room)
        print(f"✅ User joined room: {room}")  # 🔥 Dodaj print
        emit("joined_room", {"room": room, "role": role})

    @socketio.on("leave_role_room")
    def handle_leave_role(data):
        role = data.get("role")
        if not role:
            emit("error", {"message": "Role is required"})
            return
        
        room = f"role_{role}"
        leave_room(room)
        print(f"👋 User left room: {room}")  # 🔥 Dodaj print
        emit("left_room", {"room": room, "role": role})

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