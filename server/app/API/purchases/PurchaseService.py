import requests
from flask import current_app

from app.API.flights.FlightService import FlightService
from app.Domain.models.User import User
from app.Extensions import db


class PurchaseService:

    @staticmethod
    def _get_base_url():
        return current_app.config.get("FLIGHT_SERVICE_URL", "http://localhost:5050")

    @staticmethod
    def create_purchase(data: dict):
        user_id = data.get("user_id")
        flight_id = data.get("flight_id")
        if not user_id or not flight_id:
            raise ValueError("Missing user_id or flight_id")

        flight = FlightService.get_flight_by_id(flight_id)
        ticket_price = flight.get("ticket_price")
        if ticket_price is None:
            raise ValueError("Flight price not available")

        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")

        if user.accountBalance < ticket_price:
            raise ValueError("Insufficient funds")

        user.accountBalance -= float(ticket_price)
        db.session.commit()

        try:
            response = requests.post(
                f"{PurchaseService._get_base_url()}/purchase",
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            user.accountBalance += float(ticket_price)
            db.session.commit()
            raise ValueError(f"Failed to create purchase: {str(e)}")

    @staticmethod
    def get_user_purchases(user_id: int):
        try:
            response = requests.get(
                f"{PurchaseService._get_base_url()}/purchases/{user_id}"
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch purchases: {str(e)}")

    @staticmethod
    def get_purchases_by_flight(flight_id: int):
        try:
            response = requests.get(
                f"{PurchaseService._get_base_url()}/purchases/by-flight/{flight_id}"
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch purchases for flight: {str(e)}")

    @staticmethod
    def get_purchase_by_id(purchase_id: int):
        try:
            response = requests.get(
                f"{PurchaseService._get_base_url()}/purchases/by-id/{purchase_id}"
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch purchase: {str(e)}")

    @staticmethod
    def cancel_purchase(purchase_id: int):
        try:
            response = requests.put(
                f"{PurchaseService._get_base_url()}/purchases/{purchase_id}/cancel"
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to cancel purchase: {str(e)}")
