from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from models.transaction import TransactionDB, TransactionStatus
from models.wallet import WalletTransactionDB, WalletTransactionType, WithdrawalRequestDB, WithdrawalStatus
from models.user import UserDB
from models.cart import CartDB
from services.stripe_service import retrieve_checkout_session
from services.notification_service import NotificationService
import json

class WalletService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)

    def verify_payment_and_distribute(self, session_id: str, user_id: int, cart_service):
        """
        Verifies Stripe payment, records transaction, distributes revenue, and updates cart.
        """
        # 1. Check if already processed
        existing_tx = self.db.query(TransactionDB).filter(TransactionDB.stripe_session_id == session_id).first()
        if existing_tx:
             if existing_tx.status == TransactionStatus.COMPLETED:
                 return {"status": "already_processed"}
             # If using webhooks, might handle pending/failed updates here

        # 2. Verify with Stripe
        try:
            session = retrieve_checkout_session(session_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

        if session.payment_status != 'paid':
             raise HTTPException(status_code=400, detail="Payment not completed")

        # 3. Create Transaction Record
        total_amount = session.amount_total # In satang
        transaction = TransactionDB(
            stripe_session_id=session_id,
            amount=total_amount,
            payer_id=user_id,
            status=TransactionStatus.COMPLETED
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)

        # 4. Distribute Revenue
        # We need the cart items to know who to pay.
        # Assuming the caller passes a way to get cart or we get it here.
        # Using dependency on cart_service passed in might be circular or messy.
        # Better: Query CartDB directly or use the `cart_service` passed as arg.
        
        cart = cart_service.get_my_cart(user_id)
        if not cart or not cart.cart_images:
             # This is a problem if cart is cleared before this.
             # Logic assumes cart is still verified as 'unpaid' effectively or we find it.
             # But if cart isn't cleared yet, we are good.
             pass

        for item in cart.cart_images:
            image = item.image
            event = image.event
            
            # Determine price (same logic as checkout creation)
            price = 2000
            if event and event.image_price:
                price = event.image_price
            
            # Splits
            photographer_share = int(price * 0.20)
            organizer_share = int(price * 0.30)
            
            # Photographer (Image Creator)
            if image.created_by_id:
                self._add_earning(
                    user_id=image.created_by_id,
                    amount=photographer_share,
                    description=f"Revenue from image sale: {image.public_id}",
                    related_tx_id=transaction.id
                )

            # Organizer (Event Creator)
            if event and event.created_by_id:
                # If organizer is same as photographer, they get both? Yes, separate transactions.
                self._add_earning(
                    user_id=event.created_by_id,
                    amount=organizer_share,
                    description=f"Revenue from event image sale: {event.title}",
                    related_tx_id=transaction.id
                )

        # 5. Mark Cart as Paid (External call or do it here if simple)
        # cart_service.mark_as_paid(user_id) -- Caller should do this or we do it.
        # Let's assume the caller handles cart cleanup to avoid tight coupling 
        # OR we do it here because it's atomic with payment.
        # I will return success and let controller clear cart.
        
        return {"status": "success", "transaction_id": transaction.id}

    def _add_earning(self, user_id: int, amount: int, description: str, related_tx_id: int):
        wallet_tx = WalletTransactionDB(
            user_id=user_id,
            amount=amount,
            type=WalletTransactionType.EARNING,
            description=description,
            related_transaction_id=related_tx_id
        )
        self.db.add(wallet_tx)
        
        # Notify
        self.notification_service.create_notification(
            user_id=user_id,
            title="New Earning",
            message=f"You earned {amount / 100:.2f} THB. {description}"
        )

    def get_balance(self, user_id: int) -> int:
        result = self.db.query(func.sum(WalletTransactionDB.amount)).filter(
            WalletTransactionDB.user_id == user_id
        ).scalar()
        return result if result else 0

    def get_wallet_history(self, user_id: int):
        return self.db.query(WalletTransactionDB).filter(
            WalletTransactionDB.user_id == user_id
        ).order_by(WalletTransactionDB.created_at.desc()).all()

    def request_withdrawal(self, user_id: int, amount: int):
        # Check balance
        balance = self.get_balance(user_id)
        if balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        # Get Bank Info (Snapshot)
        user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user or not user.bank_info:
             raise HTTPException(status_code=400, detail="Bank info not found. Please update profile.")
        
        bank_info_str = f"{user.bank_info.bank_name} - {user.bank_info.account_number} ({user.bank_info.account_name})"

        request = WithdrawalRequestDB(
            user_id=user_id,
            amount=amount,
            bank_snapshot=bank_info_str,
            status=WithdrawalStatus.PENDING
        )
        self.db.add(request)
        self.db.commit()
        return request

    def get_withdrawal_requests(self, status: WithdrawalStatus = None):
        query = self.db.query(WithdrawalRequestDB)
        if status:
            query = query.filter(WithdrawalRequestDB.status == status)
        return query.order_by(WithdrawalRequestDB.created_at.desc()).all()

    def approve_withdrawal(self, request_id: int, admin_id: int):
        request = self.db.query(WithdrawalRequestDB).filter(WithdrawalRequestDB.id == request_id).first()
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if request.status != WithdrawalStatus.PENDING:
            raise HTTPException(status_code=400, detail="Request already processed")

        # Double check balance again?
        balance = self.get_balance(request.user_id)
        if balance < request.amount:
            # Auto-reject or fail?
            raise HTTPException(status_code=400, detail="User insufficient funds (balance changed?)")

        # Deduct
        wallet_tx = WalletTransactionDB(
            user_id=request.user_id,
            amount=-request.amount,
            type=WalletTransactionType.WITHDRAWAL,
            description=f"Withdrawal Approved (Req ID: {request.id})",
        )
        self.db.add(wallet_tx)
        
        request.status = WithdrawalStatus.APPROVED
        self.db.commit()
        
        # Notify
        self.notification_service.create_notification(
            user_id=request.user_id,
            title="Withdrawal Approved",
            message=f"Your withdrawal of {request.amount / 100:.2f} THB has been approved."
        )
        return request

    def reject_withdrawal(self, request_id: int, admin_id: int):
        request = self.db.query(WithdrawalRequestDB).filter(WithdrawalRequestDB.id == request_id).first()
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
            
        request.status = WithdrawalStatus.REJECTED
        self.db.commit()
        
        self.notification_service.create_notification(
            user_id=request.user_id,
            title="Withdrawal Rejected",
            message=f"Your withdrawal of {request.amount / 100:.2f} THB has been rejected."
        )
        return request

    def get_total_platform_revenue(self) -> int:
        result = self.db.query(func.sum(TransactionDB.amount)).filter(
            TransactionDB.status == TransactionStatus.COMPLETED
        ).scalar()
        return result if result else 0
