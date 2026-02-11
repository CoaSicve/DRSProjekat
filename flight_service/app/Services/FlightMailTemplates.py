from app.Domain.models.Flight import Flight
from typing import Optional

def flight_created_body(f: Flight) -> str:
    return (
        f"✈️ Novi let kreiran\n\n"
        f"ID: {f.id}\n"
        f"Naziv: {f.name}\n"
        f"Avio-kompanija: {f.airline.name if f.airline else f.airline_id}\n"
        f"Polazak: {f.departure_airport} @ {f.departure_time}\n"
        f"Dolazak: {f.arrival_airport}\n"
        f"Cena karte: {f.ticket_price}\n"
        f"Status: {getattr(f.status, 'value', f.status)}\n"
    )

def flight_status_changed_body(f: Flight, old_status, new_status, reason: Optional[str] = None) -> str:
    text = (
        f"🔔 Promena statusa leta\n\n"
        f"Let: {f.name} (ID {f.id})\n"
        f"Status: {old_status} ➜ {new_status}\n"
        f"Avio-kompanija: {f.airline.name if f.airline else f.airline_id}\n"
        f"Polazak: {f.departure_airport} @ {f.departure_time}\n"
        f"Dolazak: {f.arrival_airport}\n"
    )
    if reason:
        text += f"\nRazlog: {reason}\n"
    return text