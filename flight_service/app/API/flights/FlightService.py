from app.Extensions.db import db
from app.Domain.models.Flight import Flight
from app.Domain.models.Airline import Airline
from app.Domain.DTOs.FlightDTO import FlightDTO, CreateFlightDTO
from app.Domain.enums.FlightStatus import FlightStatus
from datetime import datetime
from app.Services.EmailService import EmailService
from app.Services.FlightMailTemplates import flight_created_body, flight_status_changed_body
from app.Extensions.socketio import socketio

class FlightService:
    
    @staticmethod
    def get_all_flights():
        flights = Flight.query.all()
        return [FlightService._to_dto(f) for f in flights]
    
    @staticmethod
    def get_flight_by_id(flight_id: int):
        flight = Flight.query.get(flight_id)
        if not flight:
            raise ValueError("Flight not found")
        return FlightService._to_dto(flight)
    
    @staticmethod
    def create_flight(dto: CreateFlightDTO, created_by_user_id: int, user_email: str):
        airline = Airline.query.get(dto.airline_id)
        if not airline:
            raise ValueError("Airline not found")
        
        flight = Flight(
            name=dto.name,
            airline_id=dto.airline_id,
            distance_km=dto.distance_km,
            duration_minutes=dto.duration_minutes,
            departure_time=datetime.strptime(dto.departure_time, "%Y-%m-%d %H:%M:%S"),
            departure_airport=dto.departure_airport,
            arrival_airport=dto.arrival_airport,
            created_by_user_id=created_by_user_id,
            ticket_price=dto.ticket_price,
            status=FlightStatus.PENDING
        )
        
        db.session.add(flight)
        db.session.commit()

        # Email manageru koji je kreirao
        EmailService.send(
            to=user_email,
            subject="✈️ Novi let kreiran",
            body=flight_created_body(flight)
        )
        
        # WebSocket - Obavesti sve ADMIN-e da ima novi let za approve
        socketio.emit("flight_pending_approval", {
            "id": flight.id,
            "name": flight.name,
            "status": flight.status.value,
            "created_by": created_by_user_id,
            "airline": airline.name,
            "departure": flight.departure_airport,
            "arrival": flight.arrival_airport,
            "departure_time": str(flight.departure_time)
        }, room="role_ADMIN")  # 🔥 Samo ADMIN-i
        
        return FlightService._to_dto(flight)
    
    @staticmethod
    def approve_flight(flight_id: int, admin_email: str):
        flight = Flight.query.get(flight_id)
        if not flight:
            raise ValueError("Flight not found")
        
        old_status = flight.status
        flight.status = FlightStatus.APPROVED
        db.session.commit()

        # Email adminu koji je odobrio
        EmailService.send(
            to=admin_email,
            subject="✅ Let odobren",
            body=flight_status_changed_body(flight, getattr(old_status, "value", old_status), flight.status.value)
        )
        
        # WebSocket - Obavesti MANAGER-a da je let odobren
        socketio.emit("flight_approved", {
            "id": flight.id,
            "name": flight.name,
            "status": flight.status.value
        }, room="role_MANAGER")  # Samo MANAGER-i
        
        # Obavesti i sve korisnike (javni event)
        socketio.emit("flight_status_changed", {
            "id": flight.id,
            "name": flight.name,
            "status": flight.status.value
        })  # Broadcast svima
        
        return FlightService._to_dto(flight)
    
    @staticmethod
    def reject_flight(flight_id: int, reason: str, admin_email: str):
        flight = Flight.query.get(flight_id)
        if not flight:
            raise ValueError("Flight not found")
        
        old_status = flight.status
        flight.status = FlightStatus.REJECTED
        flight.rejection_reason = reason
        db.session.commit()

        # Email adminu
        EmailService.send(
            to=admin_email,
            subject="❌ Let odbijen",
            body=flight_status_changed_body(
                flight,
                getattr(old_status, "value", old_status),
                flight.status.value,
                reason=reason
            )
        )
        
        # WebSocket - Obavesti MANAGER-a da je let odbijen
        socketio.emit("flight_rejected", {
            "id": flight.id,
            "name": flight.name,
            "status": flight.status.value,
            "reason": reason
        }, room="role_MANAGER")  # Samo MANAGER-i
        
        return FlightService._to_dto(flight)
    
    @staticmethod
    def cancel_flight(flight_id: int, admin_email: str):
        flight = Flight.query.get(flight_id)
        if not flight:
            raise ValueError("Flight not found")
        
        if flight.status == FlightStatus.COMPLETED:
            raise ValueError("Cannot cancel a completed flight")
        
        old_status = flight.status
        flight.status = FlightStatus.CANCELLED
        db.session.commit()

        # Email adminu
        EmailService.send(
            to=admin_email,
            subject="🛑 Let otkazan",
            body=flight_status_changed_body(flight, getattr(old_status, "value", old_status), flight.status.value)
        )
        
        # WebSocket - Broadcast svima
        socketio.emit("flight_cancelled", {
            "id": flight.id,
            "name": flight.name,
            "status": flight.status.value
        })  # Svima jer utice na korisnike koji su kupili kartu
        
        return FlightService._to_dto(flight)
    
    @staticmethod
    def delete_flight(flight_id: int):
        flight = Flight.query.get(flight_id)
        if not flight:
            raise ValueError("Flight not found")
        
        db.session.delete(flight)
        db.session.commit()

        # WebSocket
        socketio.emit("flight_deleted", {
            "id": flight.id,
            "name": flight.name
        })
    
    @staticmethod
    def _to_dto(flight: Flight) -> FlightDTO:
        return FlightDTO(
            id=flight.id,
            name=flight.name,
            airline_id=flight.airline_id,
            airline_name=flight.airline.name,
            distance_km=flight.distance_km,
            duration_minutes=flight.duration_minutes,
            departure_time=flight.departure_time,
            departure_airport=flight.departure_airport,
            arrival_airport=flight.arrival_airport,
            created_by_user_id=flight.created_by_user_id,
            ticket_price=flight.ticket_price,
            status=flight.status.value,
            rejection_reason=flight.rejection_reason
        )