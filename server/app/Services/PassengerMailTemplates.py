def flight_cancelled_for_passenger_body(flight: dict) -> str:
    name = flight.get("name", "Flight")
    departure = flight.get("departure_airport", "")
    arrival = flight.get("arrival_airport", "")
    departure_time = flight.get("departure_time", "")

    return (
        "<h2>Flight Cancelled</h2>"
        "<p>Your flight has been cancelled.</p>"
        "<ul>"
        f"<li><b>{name}</b></li>"
        f"<li>{departure} -&gt; {arrival}</li>"
        f"<li>Departure: {departure_time}</li>"
        "</ul>"
        "<p>Thank you,<br/>DRS team</p>"
    )
