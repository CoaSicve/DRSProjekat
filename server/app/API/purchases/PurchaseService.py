import requests
from flask import current_app


class PurchaseService:

    @staticmethod
    def _get_base_url():
        return current_app.config.get("FLIGHT_SERVICE_URL", "http://localhost:5051")

    @staticmethod
    def create_purchase(data: dict):
        try:
            response = requests.post(
                f"{PurchaseService._get_base_url()}/purchase",
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
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
