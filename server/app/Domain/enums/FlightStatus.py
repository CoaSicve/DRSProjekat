import enum

class FlightStatus(enum.Enum):
    PENDING = "PENDING"           # Čeka odobrenje admina
    APPROVED = "APPROVED"         # Odobren, vidljiv korisnicima
    REJECTED = "REJECTED"         # Odbijen od admina
    IN_PROGRESS = "IN_PROGRESS"   # Let u toku
    COMPLETED = "COMPLETED"       # Let završen
    CANCELLED = "CANCELLED"       # Let otkazan