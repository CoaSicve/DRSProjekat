import requests
from flask import current_app

from app.Extensions import socketio


class FlightService:

    @staticmethod
    def _get_base_url():
        return current_app.config.get("FLIGHT_SERVICE_URL", "http://localhost:5051")

    @staticmethod
    def get_all_flights():
        try:
            response = requests.get(f"{FlightService._get_base_url()}/api/v1/flights")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch flights: {str(e)}")

    @staticmethod
    def get_flight_by_id(flight_id: int):
        try:
            response = requests.get(f"{FlightService._get_base_url()}/api/v1/flights/{flight_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch flight: {str(e)}")

    @staticmethod
    def create_flight(data: dict, token: str):
        try:
            print(f"Creating flight with data: {data} and token: {token}")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"{FlightService._get_base_url()}/api/v1/flights",
                json=data,
                headers=headers
            )
            print(f"Flight creation response status: {response.status_code}")
            response.raise_for_status()
            try:
                flight_response = response.json()
                socketio.emit("flight_pending_approval", {
                    "id": flight_response.get("id"),
                    "name": flight_response.get("name"),
                    "status": flight_response.get("status"),
                    "created_by": flight_response.get("created_by_user_id"),
                    "airline": flight_response.get("airline_name"),
                    "departure": flight_response.get("departure_airport"),
                    "arrival": flight_response.get("arrival_airport"),
                    "departure_time": str(flight_response.get("departure_time"))
                }, room="role_ADMIN")
                print("Emitted flight_pending_approval event to ADMINs")
            except Exception as e:
                print(f"Failed to emit WebSocket event: {e}")
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to create flight: {str(e)}")

    @staticmethod
    def update_flight(flight_id: int, data: dict, token: str):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.put(
                f"{FlightService._get_base_url()}/api/v1/flights/{flight_id}",
                json=data,
                headers=headers
            )
            response.raise_for_status()
            try:
                flight_response = response.json()
                socketio.emit("flight_pending_approval", {
                    "id": flight_response.get("id"),
                    "name": flight_response.get("name"),
                    "status": flight_response.get("status"),
                    "created_by": flight_response.get("created_by_user_id"),
                    "airline": flight_response.get("airline_name"),
                    "departure": flight_response.get("departure_airport"),
                    "arrival": flight_response.get("arrival_airport"),
                    "departure_time": str(flight_response.get("departure_time"))
                }, room="role_ADMIN")
            except Exception as e:
                print(f"Failed to emit WebSocket event: {e}")
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to update flight: {str(e)}")

    @staticmethod
    def approve_flight(flight_id: int, token: str):
        try:
            print(f"Approving flight {flight_id} with token: {token}")
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
