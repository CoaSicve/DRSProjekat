import enum

class PurchaseStatus(enum.Enum):
    IN_PROGRESS = "IN_PROGRESS" #Kupovina se obradjuje
    COMPLETED = "COMPLETED"     #Kupovina je uspesna
    CANCELLED = "CANCELLED"     #Kupovina je otkazana
    FAILED = "FAILED"           #Kupovina je neuspesna