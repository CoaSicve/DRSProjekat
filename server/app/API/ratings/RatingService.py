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
            response.raise_for_status()
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
