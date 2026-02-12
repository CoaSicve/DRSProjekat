from app.Domain.models.Flight import Flight

def flight_cancelled_for_passenger_body(f: Flight) -> str:
    return f"""
    <h2>Otkazan let</h2>
    <p>Obaveštavamo vas da je otkazan let:</p>
    <ul>
      <li><b>{f.name}</b></li>
      <li>{f.departure_airport} → {f.arrival_airport}</li>
      <li>Polazak: {f.departure_time}</li>
    </ul>
    <p>Prijatan dan,<br/>DRS tim</p>
    """