from sqlalchemy.orm import Session, joinedload
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

        # 3. Load Cart first (to get items and link to transaction)
        cart = cart_service.get_my_cart(user_id)
        if not cart or not cart.cart_images:
             raise HTTPException(status_code=404, detail="Cart is empty or not found")

        # 4. Create Transaction Record
        total_amount = session.amount_total # In satang
        transaction = TransactionDB(
            stripe_session_id=session_id,
            amount=total_amount,
            payer_id=user_id,
            cart_id=cart.id,
            status=TransactionStatus.COMPLETED
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)

        # 5. Distribute Revenue (Consolidated)
        # Group earnings by (user_id, description_template) to avoid multiple micro-transactions
        photographer_earnings = {} # (user_id, public_id) -> amount
        organizer_earnings = {}    # (user_id, event_title) -> amount

        for item in cart.cart_images:
            image = item.image
            event = image.event
            
            price = 2000
            if event and event.image_price:
                price = event.image_price
            
            p_share = int(price * 0.20)
            o_share = int(price * 0.30)
            
            # Photographer
            if image.created_by_id:
                key = (image.created_by_id, image.public_id)
                photographer_earnings[key] = photographer_earnings.get(key, 0) + p_share

            # Organizer
            if event and event.created_by_id:
                key = (event.created_by_id, event.title)
                organizer_earnings[key] = organizer_earnings.get(key, 0) + o_share

        # Record Consolidated Photographer Earnings
        for (p_id, p_public_id), amount in photographer_earnings.items():
            self._add_earning(
                user_id=p_id,
                amount=amount,
                description=f"Revenue from image sale: {p_public_id} (Cart: {cart.id})",
                related_tx_id=transaction.id
            )

        # Record Consolidated Organizer Earnings
        for (o_id, e_title), amount in organizer_earnings.items():
            self._add_earning(
                user_id=o_id,
                amount=amount,
                description=f"Revenue from event image sale: {e_title} (Cart: {cart.id})",
                related_tx_id=transaction.id
            )

        # 6. Record Super Admin Share (50%)
        system_share = int(total_amount * 0.50)
        super_admins = self.db.query(UserDB).filter(UserDB.role == "super-admin").all()
        for admin in super_admins:
            self._add_earning(
                user_id=admin.id,
                amount=system_share,
                description=f"Platform revenue share (50%) from sale (Cart: {cart.id})",
                related_tx_id=transaction.id
            )

        self.db.commit()
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
        
        # Notify Super Admins
        super_admins = self.db.query(UserDB).filter(UserDB.role == "super-admin").all()
        for admin in super_admins:
             self.notification_service.create_notification(
                user_id=admin.id,
                title="New Withdrawal Request",
                message=f"User {user.first_name} {user.last_name} requested a withdrawal of {amount / 100:.2f} THB."
            )
            
        return request

    def get_withdrawal_requests(self, status: WithdrawalStatus = None):
        query = self.db.query(WithdrawalRequestDB).options(joinedload(WithdrawalRequestDB.user))
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
        # Total Sales (100%)
        total_sales = self.db.query(func.sum(TransactionDB.amount)).filter(
            TransactionDB.status == TransactionStatus.COMPLETED
        ).scalar() or 0
        
        # Total Approved Withdrawals
        total_withdrawals = self.db.query(func.sum(WithdrawalRequestDB.amount)).filter(
            WithdrawalRequestDB.status == WithdrawalStatus.APPROVED
        ).scalar() or 0
        
        # Net Platform Revenue/Balance as requested: "keep it as 100% but deduct when approve withdraw req"
        return total_sales - total_withdrawals

    def deduct_balance(self, admin_id: int, user_id: int, amount: int):
        # Check balance
        balance = self.get_balance(user_id)
        if balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        # Deduct
        wallet_tx = WalletTransactionDB(
            user_id=user_id,
            amount=-amount,
            type=WalletTransactionType.ADMIN_DEDUCTION,
            description="Revenue deduction by Admin",
        )
        self.db.add(wallet_tx)
        
        self.db.commit()
        
        # Notify
        self.notification_service.create_notification(
            user_id=user_id,
            title="Revenue Deducted",
            message=f"Admin has deducted {amount / 100:.2f} THB from your wallet."
        )
        return wallet_tx
