import time
import threading #ovo za asinhronu obranu koristim
from app.Extensions.db import db
from app.Domain.enums.PurchaseStatus import PurchaseStatus
from app.Domain.models.Purchase import Purchase
from app.Domain.models.Flight import Flight

class PurchaseService:
    @staticmethod
    def start_purchase(user_id: int, flight_id: int):
        flight = Flight.query.get(flight_id)
        if not flight:
            raise ValueError("Let ne postoji.")
        if flight.status.name != "APPROVED":
            raise ValueError("Kupovina je moguca samo za odobrene letove.")
        
        purchase = Purchase(
            user_id=user_id,
            flight_id=flight_id,
            ticket_price=flight.ticket_price,
            status=PurchaseStatus.IN_PROGRESS
        )
        db.session.add(purchase)
        db.session.commit()

        thread = threading.Thread(
            target=PurchaseService.__process_purchase,
            args=(purchase.id,)
        )
        thread.start()

        return purchase
    
    @staticmethod
    def __process_purchase(purchase_id: int):
        try:
            time.sleep(5) #ovo je da simulira duzu obradu 

            purchase = Purchase.query.get(purchase_id)
            if not purchase:
                return
        
            purchase.status = PurchaseStatus.COMPLETED

            db.session.commit()
            print(f"Kupovina je uspesno zavrsena; ID: {purchase_id}")
        except Exception as e:
            purchase = Purchase.query.get(purchase_id)
            if purchase:
                purchase.status = PurchaseStatus.FAILED
                db.session.commit()
            print(f"Greska u obradi kupovine. ID: {purchase_id} ; ERROR: {e}")
        