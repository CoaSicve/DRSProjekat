import requests
from flask import current_app


class FlightService:
    """Proxy service to call flight_service microservice"""

    @staticmethod
    def _get_base_url():
        return current_app.config.get("FLIGHT_SERVICE_URL", "http://localhost:5001")

    @staticmethod
    def get_all_flights():
        """Get all flights from flight_service"""
        try:
            response = requests.get(f"{FlightService._get_base_url()}/api/v1/flights")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch flights: {str(e)}")

    @staticmethod
    def get_flight_by_id(flight_id: int):
        """Get flight by ID from flight_service"""
        try:
            response = requests.get(f"{FlightService._get_base_url()}/api/v1/flights/{flight_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch flight: {str(e)}")

    @staticmethod
    def create_flight(data: dict, token: str):
        """Create flight in flight_service"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"{FlightService._get_base_url()}/api/v1/flights",
                json=data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to create flight: {str(e)}")

    @staticmethod
    def approve_flight(flight_id: int, token: str):
        """Approve flight in flight_service"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.put(
                f"{FlightService._get_base_url()}/api/v1/flights/{flight_id}/approve",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to approve flight: {str(e)}")

    @staticmethod
    def reject_flight(flight_id: int, data: dict, token: str):
        """Reject flight in flight_service"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.put(
                f"{FlightService._get_base_url()}/api/v1/flights/{flight_id}/reject",
                json=data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to reject flight: {str(e)}")

    @staticmethod
    def cancel_flight(flight_id: int, token: str):
        """Cancel flight in flight_service"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.put(
                f"{FlightService._get_base_url()}/api/v1/flights/{flight_id}/cancel",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to cancel flight: {str(e)}")

    @staticmethod
    def delete_flight(flight_id: int, token: str):
        """Delete flight from flight_service"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.delete(
                f"{FlightService._get_base_url()}/api/v1/flights/{flight_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to delete flight: {str(e)}")
