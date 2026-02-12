from app.Extensions.db import db
from app.Domain.models.Flight import Flight
from app.Domain.models.Airline import Airline
from app.Domain.DTOs.FlightDTO import FlightDTO, CreateFlightDTO
from app.Domain.enums.FlightStatus import FlightStatus
from datetime import datetime
from app.Services.EmailService import EmailService
from app.Services.FlightMailTemplates import flight_created_body, flight_status_changed_body
from app.Extensions.socketio import socketio
import requests
from app.Domain.models.Purchase import Purchase
from app.Domain.enums.PurchaseStatus import PurchaseStatus
from app.Services.PassengerMailTemplates import flight_cancelled_for_passenger_body

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

        print(f"Flight created with ID: {flight.id} by user {created_by_user_id}")
        
        try:
            EmailService.send(
                to=user_email,
                subject="✈️ Novi let kreiran",
                body=flight_created_body(flight)
            )
        except Exception as e:
            print(f"Failed to send email: {e}")
        
        return FlightService._to_dto(flight)
    
    @staticmethod
    def approve_flight(flight_id: int, admin_email: str):
        flight = Flight.query.get(flight_id)
        if not flight:
            raise ValueError("Flight not found")
        
        old_status = flight.status
        flight.status = FlightStatus.APPROVED
        db.session.commit()

        try:
            EmailService.send(
                to=admin_email,
                subject="✅ Let odobren",
                body=flight_status_changed_body(flight, getattr(old_status, "value", old_status), flight.status.value)
            )
        except Exception as e:
            print(f"Failed to send email: {e}")
        
        try:
            socketio.emit("flight_approved", {
                "id": flight.id,
                "name": flight.name,
                "status": flight.status.value
            }, room="role_MANAGER")
            
            socketio.emit("flight_status_changed", {
                "id": flight.id,
                "name": flight.name,
                "status": flight.status.value
            })
        except Exception as e:
            print(f"Failed to emit WebSocket event: {e}")
        
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

        try:
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
        except Exception as e:
            print(f"Failed to send email: {e}")
        
        try:
            socketio.emit("flight_rejected", {
                "id": flight.id,
                "name": flight.name,
                "status": flight.status.value,
                "reason": reason
            }, room="role_MANAGER")
        except Exception as e:
            print(f"Failed to emit WebSocket event: {e}")
        
        return FlightService._to_dto(flight)
    
    @staticmethod
    def cancel_flight(flight_id: int, admin_email: str, auth_token: str, server_base_url: str):
        flight = Flight.query.get(flight_id)
        if not flight:
            raise ValueError("Flight not found")

        if flight.status == FlightStatus.COMPLETED:
            raise ValueError("Cannot cancel a completed flight")

        old_status = flight.status
        flight.status = FlightStatus.CANCELLED
        db.session.commit()

        # ------------------------
        #  Mail adminu
        # ------------------------
        try:
            EmailService.send(
                to=admin_email,
                subject="🛑 Let otkazan",
                body=flight_status_changed_body(
                    flight,
                    getattr(old_status, "value", old_status),
                    flight.status.value
                )
            )
        except Exception as e:
            print(f"Failed to send admin email: {e}")

        # ------------------------
        #  Mail svim korisnicima koji su kupili karte
        # ------------------------
        try:
            purchases = Purchase.query.filter_by(
                flight_id=flight.id,
                status=PurchaseStatus.COMPLETED
            ).all()

            for purchase in purchases:
                try:
                    # Pozovi auth server da dobiješ email korisnika
                    response = requests.get(
                        f"{server_base_url}/api/v1/users/{purchase.user_id}",
                        headers={"Authorization": f"Bearer {auth_token}"}
                    )

                    if response.status_code != 200:
                        print(f"Could not fetch user {purchase.user_id}")
                        continue

                    user_data = response.json()
                    user_email = user_data.get("email")

                    if not user_email:
                        continue

                    EmailService.send(
                        to=user_email,
                        subject="🛑 Vaš let je otkazan",
                        body=flight_cancelled_for_passenger_body(flight)
                    )

                except Exception as inner_e:
                    print(f"Error notifying user {purchase.user_id}: {inner_e}")

        except Exception as e:
            print(f"Failed to notify passengers: {e}")

        # ------------------------
        #  WebSocket event
        # ------------------------
        try:
            socketio.emit("flight_cancelled", {
                "id": flight.id,
                "name": flight.name,
                "status": flight.status.value
            })
        except Exception as e:
            print(f"Failed to emit WebSocket event: {e}")

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