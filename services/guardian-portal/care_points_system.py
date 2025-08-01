"""
?

?ADHD?
"""

import stripe
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)

# Stripe設定
stripe.api_key = "sk_test_dummy_key"

class DiscountType(Enum):
    ADHD_MEDICAL = "adhd_medical"
    CORPORATE_BULK = "corporate_bulk"
    SEASONAL = "seasonal"

class CarePointTransaction(BaseModel):
    transaction_id: str
    from_entity: str  # ?ID or システム
    to_user: str      # ユーザーID
    points: int
    transaction_type: str  # "purchase", "transfer", "bonus"
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class CorporatePurchase(BaseModel):
    corporate_id: str
    purchase_amount: int  # ?
    points_purchased: int
    discount_applied: Optional[str] = None
    stripe_payment_intent_id: str
    created_at: datetime

class ADHDMedicalDocument(BaseModel):
    document_id: str
    user_id: str
    document_type: str  # "diagnosis", "prescription", "therapy_record"
    verified: bool
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None  # ?ID
    expiry_date: Optional[datetime] = None

class CarePointsSystem:
    def __init__(self):
        self.point_rate = 1  # 1? = 1?
        self.adhd_discount_rate = 0.5  # 50%?
        self.corporate_bulk_thresholds = {
            10000: 0.05,   # 10,000?5%?
            50000: 0.10,   # 50,000?10%?
            100000: 0.15   # 100,000?15%?
        }
        self.care_point_balances = {}  # 実装Firestoreを
        self.transactions = []         # 実装Firestoreを
        self.medical_documents = {}    # 実装Firestoreを
    
    def calculate_corporate_discount(self, amount: int) -> float:
        """?"""
        discount_rate = 0.0
        
        for threshold, rate in sorted(self.corporate_bulk_thresholds.items(), reverse=True):
            if amount >= threshold:
                discount_rate = rate
                break
        
        return discount_rate
    
    def create_stripe_payment_intent(self, amount: int, corporate_id: str, 
                                   discount_rate: float = 0.0) -> Dict[str, Any]:
        """Stripe?"""
        try:
            # ?
            discounted_amount = int(amount * (1 - discount_rate))
            
            # Stripe?
            payment_intent = {
                "id": f"pi_{uuid.uuid4().hex[:24]}",
                "amount": discounted_amount,
                "currency": "jpy",
                "status": "requires_payment_method",
                "client_secret": f"pi_{uuid.uuid4().hex[:24]}_secret",
                "metadata": {
                    "corporate_id": corporate_id,
                    "original_amount": amount,
                    "discount_rate": discount_rate
                }
            }
            
            logger.info(f"Payment intent created: {payment_intent['id']}")
            return payment_intent
            
        except Exception as e:
            logger.error(f"Stripe payment intent creation failed: {e}")
            raise HTTPException(
                status_code=500, 
                detail="?"
            )
    
    def process_corporate_purchase(self, corporate_id: str, amount: int, 
                                 payment_intent_id: str) -> CorporatePurchase:
        """?"""
        try:
            # ?
            discount_rate = self.calculate_corporate_discount(amount)
            discounted_amount = int(amount * (1 - discount_rate))
            
            # ?
            points_purchased = discounted_amount * self.point_rate
            
            # ?
            purchase = CorporatePurchase(
                corporate_id=corporate_id,
                purchase_amount=discounted_amount,
                points_purchased=points_purchased,
                discount_applied=f"corporate_bulk_{discount_rate*100:.0f}%" if discount_rate > 0 else None,
                stripe_payment_intent_id=payment_intent_id,
                created_at=datetime.utcnow()
            )
            
            # ?
            if corporate_id not in self.care_point_balances:
                self.care_point_balances[corporate_id] = 0
            
            self.care_point_balances[corporate_id] += points_purchased
            
            logger.info(f"Corporate purchase completed: {corporate_id}, {points_purchased} points")
            return purchase
            
        except Exception as e:
            logger.error(f"Corporate purchase processing failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="?"
            )
    
    def transfer_care_points(self, from_corporate_id: str, to_user_id: str, 
                           points: int, metadata: Optional[Dict[str, Any]] = None) -> CarePointTransaction:
        """?"""
        try:
            # ?
            corporate_balance = self.care_point_balances.get(from_corporate_id, 0)
            if corporate_balance < points:
                raise HTTPException(
                    status_code=400,
                    detail="?"
                )
            
            # ?
            self.care_point_balances[from_corporate_id] -= points
            
            if to_user_id not in self.care_point_balances:
                self.care_point_balances[to_user_id] = 0
            self.care_point_balances[to_user_id] += points
            
            # ?
            transaction = CarePointTransaction(
                transaction_id=str(uuid.uuid4()),
                from_entity=from_corporate_id,
                to_user=to_user_id,
                points=points,
                transaction_type="transfer",
                created_at=datetime.utcnow(),
                metadata=metadata
            )
            
            self.transactions.append(transaction)
            
            logger.info(f"Care points transferred: {from_corporate_id} -> {to_user_id}, {points} points")
            return transaction
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Care points transfer failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="?"
            )
    
    def verify_adhd_medical_document(self, document_id: str, user_id: str, 
                                   document_type: str, verifier_id: str) -> ADHDMedicalDocument:
        """ADHD?"""
        try:
            # 文字
            document = ADHDMedicalDocument(
                document_id=document_id,
                user_id=user_id,
                document_type=document_type,
                verified=True,
                verified_at=datetime.utcnow(),
                verified_by=verifier_id,
                expiry_date=datetime.utcnow() + timedelta(days=365)  # 1?
            )
            
            self.medical_documents[document_id] = document
            
            logger.info(f"ADHD medical document verified: {document_id} for user {user_id}")
            return document
            
        except Exception as e:
            logger.error(f"ADHD document verification failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="?"
            )
    
    def check_adhd_discount_eligibility(self, user_id: str) -> bool:
        """ADHD?"""
        try:
            # ユーザー
            current_time = datetime.utcnow()
            
            for doc in self.medical_documents.values():
                if (doc.user_id == user_id and 
                    doc.verified and 
                    doc.expiry_date and 
                    doc.expiry_date > current_time):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"ADHD discount eligibility check failed: {e}")
            return False
    
    def apply_adhd_discount(self, user_id: str, original_amount: int) -> Dict[str, Any]:
        """ADHD?50%?"""
        try:
            if not self.check_adhd_discount_eligibility(user_id):
                raise HTTPException(
                    status_code=400,
                    detail="ADHD?"
                )
            
            discounted_amount = int(original_amount * self.adhd_discount_rate)
            discount_amount = original_amount - discounted_amount
            
            return {
                "original_amount": original_amount,
                "discounted_amount": discounted_amount,
                "discount_amount": discount_amount,
                "discount_rate": self.adhd_discount_rate,
                "discount_type": "adhd_medical"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"ADHD discount application failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="ADHD?"
            )
    
    def get_care_point_balance(self, entity_id: str) -> int:
        """?"""
        return self.care_point_balances.get(entity_id, 0)
    
    def get_transaction_history(self, entity_id: str, limit: int = 50) -> List[CarePointTransaction]:
        """?"""
        entity_transactions = [
            t for t in self.transactions 
            if t.from_entity == entity_id or t.to_user == entity_id
        ]
        
        # ?
        entity_transactions.sort(key=lambda x: x.created_at, reverse=True)
        
        return entity_transactions[:limit]
    
    def create_stripe_coupon_for_adhd(self, user_id: str) -> Dict[str, Any]:
        """ADHD?Stripe?"""
        try:
            if not self.check_adhd_discount_eligibility(user_id):
                raise HTTPException(
                    status_code=400,
                    detail="ADHD?"
                )
            
            # Stripe?
            coupon = {
                "id": f"adhd_discount_{user_id}_{uuid.uuid4().hex[:8]}",
                "percent_off": 50,
                "duration": "once",
                "max_redemptions": 1,
                "metadata": {
                    "user_id": user_id,
                    "discount_type": "adhd_medical",
                    "created_at": datetime.utcnow().isoformat()
                }
            }
            
            logger.info(f"ADHD Stripe coupon created: {coupon['id']} for user {user_id}")
            return coupon
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"ADHD Stripe coupon creation failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="ADHD?"
            )

# ?
care_points_system = CarePointsSystem()

# APIリスト/レベル
class CorporatePurchaseRequest(BaseModel):
    corporate_id: str
    amount: int  # ?
    payment_method_id: Optional[str] = None

class CarePointTransferRequest(BaseModel):
    from_corporate_id: str
    to_user_id: str
    points: int
    message: Optional[str] = None

class ADHDDocumentVerificationRequest(BaseModel):
    user_id: str
    document_type: str
    document_data: str  # Base64エラー
    verifier_id: str

class ADHDDiscountRequest(BaseModel):
    user_id: str
    original_amount: int