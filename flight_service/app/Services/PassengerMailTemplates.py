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

def purchase_completed_body(f: Flight, purchase_id: int, ticket_price: float) -> str:
  return (
    "Kupovina karte je uspesno zavrsena.\n\n"
    f"ID kupovine: {purchase_id}\n"
    f"Let: {f.name}\n"
    f"Ruta: {f.departure_airport} -> {f.arrival_airport}\n"
    f"Polazak: {f.departure_time}\n"
    f"Cena karte: {ticket_price}\n\n"
    "Hvala na poverenju,\nDRS tim\n"
  )