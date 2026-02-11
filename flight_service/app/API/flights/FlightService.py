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
    def create_flight(dto: CreateFlightDTO, created_by_user_id: int):
        # Validate airline exists
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

        EmailService.send(
            subject="✈️ Novi let kreiran",
            body=flight_created_body(flight)
        )
        
        socketio.emit("flight_created", {
            "id": flight.id,
            "name": flight.name,
            "status": flight.status.value if hasattr(flight.status, "value") else flight.status
        })
        return FlightService._to_dto(flight)
    
    @staticmethod
    def approve_flight(flight_id: int):
        flight = Flight.query.get(flight_id)
        if not flight:
            raise ValueError("Flight not found")
        
        old_status = flight.status
        flight.status = FlightStatus.APPROVED
        db.session.commit()

        EmailService.send(
            subject="✅ Let odobren",
            body=flight_status_changed_body(flight, getattr(old_status, "value", old_status), flight.status.value)
        )
        
        return FlightService._to_dto(flight)
    
    @staticmethod
    def reject_flight(flight_id: int, reason: str):
        flight = Flight.query.get(flight_id)
        if not flight:
            raise ValueError("Flight not found")
        
        old_status = flight.status
        flight.status = FlightStatus.REJECTED
        flight.rejection_reason = reason
        db.session.commit()

        EmailService.send(
            subject="❌ Let odbijen",
            body=flight_status_changed_body(
                flight,
                getattr(old_status, "value", old_status),
                flight.status.value,
                reason=reason
            )
        )
        
        return FlightService._to_dto(flight)
    
    @staticmethod
    def cancel_flight(flight_id: int):
        flight = Flight.query.get(flight_id)
        if not flight:
            raise ValueError("Flight not found")
        
        if flight.status == FlightStatus.COMPLETED:
            raise ValueError("Cannot cancel a completed flight")
        
        old_status = flight.status
        flight.status = FlightStatus.CANCELLED
        db.session.commit()

        EmailService.send(
            subject="🛑 Let otkazan",
            body=flight_status_changed_body(flight, getattr(old_status, "value", old_status), flight.status.value)
        )
        
        return FlightService._to_dto(flight)
    
    @staticmethod
    def delete_flight(flight_id: int):
        flight = Flight.query.get(flight_id)
        if not flight:
            raise ValueError("Flight not found")
        
        db.session.delete(flight)
        db.session.commit()

        socketio.emit("flight_deleted", {
            "id": flight.id,
            "name": flight.name,
            "status": flight.status.value if hasattr(flight.status, "value") else flight.status
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