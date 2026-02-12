import time
import threading #ovo za asinhronu obranu koristim
from flask import current_app
from app.Extensions.db import db
from app.Domain.enums.PurchaseStatus import PurchaseStatus
from app.Domain.models.Purchase import Purchase
from app.Domain.models.Flight import Flight
from app.Services.EmailService import EmailService
from app.Services.PassengerMailTemplates import purchase_completed_body

class PurchaseService:
    @staticmethod
    def start_purchase(user_id: int, flight_id: int, user_email: str = None):
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

        app = current_app._get_current_object()
        thread = threading.Thread(
            target=PurchaseService.__process_purchase,
            args=(app, purchase.id, user_email,)
        )
        thread.start()

        return purchase
    
    @staticmethod
    def __process_purchase(app, purchase_id: int, user_email: str = None):
        with app.app_context():
            try:
                time.sleep(5) #ovo je da simulira duzu obradu 

                purchase = Purchase.query.get(purchase_id)
                if not purchase:
                    return

                if purchase.status != PurchaseStatus.IN_PROGRESS:
                    return
            
                purchase.status = PurchaseStatus.COMPLETED

                db.session.commit()
                if user_email:
                    EmailService.send(
                        to=user_email,
                        subject="Kupovina karte uspesna",
                        body=purchase_completed_body(purchase.flight, purchase.id, purchase.ticket_price)
                    )
                print(f"Kupovina je uspesno zavrsena; ID: {purchase_id}")
            except Exception as e:
                purchase = Purchase.query.get(purchase_id)
                if purchase:
                    purchase.status = PurchaseStatus.FAILED
                    db.session.commit()
                print(f"Greska u obradi kupovine. ID: {purchase_id} ; ERROR: {e}")

    @staticmethod
    def cancel_purchase(purchase_id: int):
        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            raise ValueError("Purchase not found")

        if purchase.status == PurchaseStatus.CANCELLED:
            return purchase

        if purchase.status == PurchaseStatus.FAILED:
            raise ValueError("Cannot cancel a failed purchase")

        purchase.status = PurchaseStatus.CANCELLED
        db.session.commit()
        return purchase
        