import enum

class PurchaseStatus(enum.Enum):
    IN_PROGRESS = "IN_PROGRESS" #Kupovina se obradjuje
    COMPLETED = "COMPLETED"     #Kupovina je uspesna
    FAILED = "FAILED"           #Kupovina je neuspesna