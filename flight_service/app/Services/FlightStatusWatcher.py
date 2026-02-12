import threading
import time
from datetime import datetime, timedelta

from app.Extensions.db import db
from app.Extensions.socketio import socketio
from app.Domain.enums.FlightStatus import FlightStatus
from app.Domain.models.Flight import Flight

class FlightStatusWatcher:
    _thread = None
    _running = False

    @classmethod
    def start(cls, app, interval_seconds: int = 5):
        if cls._thread and cls._thread.is_alive():
            return

        cls._running = True
        cls._thread = threading.Thread(target=cls._run, args=(app, interval_seconds,), daemon=True)
        cls._thread.start()

    @classmethod
    def stop(cls):
        cls._running = False

    @classmethod
    def _run(cls, app, interval_seconds: int):
        while cls._running:
            try:
                with app.app_context():
                    cls._check_flights()
            except Exception as e:
                print(f"FlightStatusWatcher error: {e}")
            time.sleep(interval_seconds)

    @classmethod
    def _check_flights(cls):
        now = datetime.now()
        flights = Flight.query.filter(Flight.status.in_(["APPROVED", "IN_PROGRESS"])).all()
        updated = False
        for flight in flights:
            departure = flight.departure_time
            landing = departure + timedelta(minutes=flight.duration_minutes)

            if flight.status.name == "APPROVED" and now >= departure and now < landing:
                flight.status = FlightStatus.IN_PROGRESS
                updated = True
            elif flight.status.name in ("APPROVED", "IN_PROGRESS") and now >= landing:
                flight.status = FlightStatus.COMPLETED
                updated = True

        if updated:
            db.session.commit()

        payload = {
            "timestamp": now.isoformat(),
            "count": len(flights),
        }

        socketio.emit("flight_status_tick", payload)