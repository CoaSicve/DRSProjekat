from app.Extensions.db import db
from app.Domain.models.Airline import Airline
from app.Domain.DTOs.AirlineDTO import AirlineDTO, CreateAirlineDTO


class AirlineService:

    @staticmethod
    def get_all_airlines():
        airlines = Airline.query.all()
        return [AirlineService._to_dto(a) for a in airlines]

    @staticmethod
    def get_airline_by_id(airline_id: int):
        airline = Airline.query.get(airline_id)
        if not airline:
            raise ValueError("Airline not found")
        return AirlineService._to_dto(airline)

    @staticmethod
    def create_airline(dto: CreateAirlineDTO):
        if Airline.query.filter_by(code=dto.code).first():
            raise ValueError(f"Airline with code '{dto.code}' already exists")

        airline = Airline(
            name=dto.name,
            code=dto.code,
            country=dto.country
        )

        db.session.add(airline)
        db.session.commit()

        return AirlineService._to_dto(airline)

    @staticmethod
    def delete_airline(airline_id: int):
        airline = Airline.query.get(airline_id)
        if not airline:
            raise ValueError("Airline not found")

        db.session.delete(airline)
        db.session.commit()

    @staticmethod
    def _to_dto(airline: Airline) -> AirlineDTO:
        return AirlineDTO(
            id=airline.id,
            name=airline.name,
            code=airline.code,
            country=airline.country
        )