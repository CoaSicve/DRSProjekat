import requests
from flask import current_app


class AirlineService:
    """Proxy service to call flight_service microservice for airline endpoints"""

    @staticmethod
    def _get_base_url():
        return current_app.config.get("FLIGHT_SERVICE_URL", "http://localhost:5001")

    @staticmethod
    def get_all_airlines():
        """Get all airlines from flight_service"""
        try:
            response = requests.get(f"{AirlineService._get_base_url()}/api/v1/airlines")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch airlines: {str(e)}")

    @staticmethod
    def get_airline_by_id(airline_id: int):
        """Get airline by ID from flight_service"""
        try:
            response = requests.get(f"{AirlineService._get_base_url()}/api/v1/airlines/{airline_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch airline: {str(e)}")

    @staticmethod
    def create_airline(data: dict):
        """Create airline in flight_service"""
        try:
            response = requests.post(
                f"{AirlineService._get_base_url()}/api/v1/airlines",
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to create airline: {str(e)}")

    @staticmethod
    def delete_airline(airline_id: int):
        """Delete airline from flight_service"""
        try:
            response = requests.delete(
                f"{AirlineService._get_base_url()}/api/v1/airlines/{airline_id}"
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to delete airline: {str(e)}")
