import threading
import time
from datetime import datetime, timezone

from app.Extensions.db import db
from app.Extensions.socketio import socketio
from app.Domain.models.Flight import Flight

class FlightStatusWatcher:
    _thread = None
    _running = False

    @classmethod
    def start(cls, interval_seconds: int = 5):
        if cls._thread and cls._thread.is_alive():
            return

        cls._running = True
        cls._thread = threading.Thread(target=cls._run, args=(interval_seconds,), daemon=True)
        cls._thread.start()

    @classmethod
    def stop(cls):
        cls._running = False

    @classmethod
    def _run(cls, interval_seconds: int):
        while cls._running:
            try:
                cls._check_flights()
            except Exception as e:
                pass
            time.sleep(interval_seconds)

    @classmethod
    def _check_flights(cls):
        now = datetime.now(timezone.utc)

        flights = Flight.query.all()

        payload = {
            "timestamp": now.isoformat(),
            "count": len(flights),
        }

        socketio.emit("flight_status_tick", payload, broadcast=True)