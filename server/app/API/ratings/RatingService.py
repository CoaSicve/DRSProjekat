import requests
from flask import current_app


class RatingService:

    @staticmethod
    def _get_base_url():
        return current_app.config.get("FLIGHT_SERVICE_URL", "http://localhost:5051")

    @staticmethod
    def create_rating(data: dict):
        try:
            response = requests.post(
                f"{RatingService._get_base_url()}/rating",
                json=data
            )
            if response.status_code >= 400:
                try:
                    error_payload = response.json()
                    error_message = error_payload.get("error") or str(error_payload)
                except ValueError:
                    error_message = response.text
                raise ValueError(f"Failed to create rating: {error_message}")
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to create rating: {str(e)}")

    @staticmethod
    def get_all_ratings():
        try:
            response = requests.get(
                f"{RatingService._get_base_url()}/ratings"
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch ratings: {str(e)}")
