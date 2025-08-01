"""
?
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json
import uuid

# ?
from main import app, guardian_auth, guardian_rbac
from care_points_system import care_points_system, DiscountType

client = TestClient(app)

class TestCarePointsSystem:
    """?"""
    
    def setup_method(self):
        """?"""
        # ?
        care_points_system.care_point_balances.clear()
        care_points_system.transactions.clear()
        care_points_system.medical_documents.clear()
    
    def test_corporate_discount_calculation(self):
        """?"""
        # 10,000? - ?
        discount = care_points_system.calculate_corporate_discount(5000)
        assert discount == 0.0
        
        # 10,000? - 5%?
        discount = care_points_system.calculate_corporate_discount(15000)
        assert discount == 0.05
        
        # 50,000? - 10%?
        discount = care_points_system.calculate_corporate_discount(60000)
        assert discount == 0.10
        
        # 100,000? - 15%?
        discount = care_points_system.calculate_corporate_discount(150000)
        assert discount == 0.15
    
    def test_stripe_payment_intent_creation(self):
        """Stripe?"""
        amount = 10000
        corporate_id = "corp_001"
        discount_rate = 0.05
        
        payment_intent = care_points_system.create_stripe_payment_intent(
            amount, corporate_id, discount_rate
        )
        
        assert payment_intent["amount"] == 9500  # 5%?
        assert payment_intent["currency"] == "jpy"
        assert payment_intent["metadata"]["corporate_id"] == corporate_id
        assert payment_intent["metadata"]["discount_rate"] == discount_rate
    
    def test_corporate_purchase_processing(self):
        """?"""
        corporate_id = "corp_001"
        amount = 10000
        payment_intent_id = "pi_test_123"
        
        purchase = care_points_system.process_corporate_purchase(
            corporate_id, amount, payment_intent_id
        )
        
        assert purchase.corporate_id == corporate_id
        assert purchase.purchase_amount == amount
        assert purchase.points_purchased == amount  # 1? = 1?
        assert purchase.stripe_payment_intent_id == payment_intent_id
        
        # ?
        balance = care_points_system.get_care_point_balance(corporate_id)
        assert balance == amount
    
    def test_care_points_transfer(self):
        """?"""
        corporate_id = "corp_001"
        user_id = "user_001"
        points = 500
        
        # ?
        care_points_system.care_point_balances[corporate_id] = 1000
        
        transaction = care_points_system.transfer_care_points(
            corporate_id, user_id, points
        )
        
        assert transaction.from_entity == corporate_id
        assert transaction.to_user == user_id
        assert transaction.points == points
        assert transaction.transaction_type == "transfer"
        
        # ?
        corporate_balance = care_points_system.get_care_point_balance(corporate_id)
        user_balance = care_points_system.get_care_point_balance(user_id)
        
        assert corporate_balance == 500  # 1000 - 500
        assert user_balance == 500
    
    def test_care_points_transfer_insufficient_balance(self):
        """?"""
        corporate_id = "corp_001"
        user_id = "user_001"
        points = 1000
        
        # ?
        care_points_system.care_point_balances[corporate_id] = 500
        
        with pytest.raises(Exception) as exc_info:
            care_points_system.transfer_care_points(corporate_id, user_id, points)
        
        assert "?" in str(exc_info.value)
    
    def test_adhd_medical_document_verification(self):
        """ADHD?"""
        document_id = "doc_001"
        user_id = "user_001"
        document_type = "diagnosis"
        verifier_id = "doctor_001"
        
        document = care_points_system.verify_adhd_medical_document(
            document_id, user_id, document_type, verifier_id
        )
        
        assert document.document_id == document_id
        assert document.user_id == user_id
        assert document.document_type == document_type
        assert document.verified is True
        assert document.verified_by == verifier_id
        assert document.expiry_date is not None
    
    def test_adhd_discount_eligibility_check(self):
        """ADHD?"""
        user_id = "user_001"
        
        # ?
        eligible = care_points_system.check_adhd_discount_eligibility(user_id)
        assert eligible is False
        
        # ?
        document_id = "doc_001"
        care_points_system.verify_adhd_medical_document(
            document_id, user_id, "diagnosis", "doctor_001"
        )
        
        # ?
        eligible = care_points_system.check_adhd_discount_eligibility(user_id)
        assert eligible is True
    
    def test_adhd_discount_application(self):
        """ADHD?"""
        user_id = "user_001"
        original_amount = 10000
        
        # ?
        document_id = "doc_001"
        care_points_system.verify_adhd_medical_document(
            document_id, user_id, "diagnosis", "doctor_001"
        )
        
        # ?
        discount_info = care_points_system.apply_adhd_discount(user_id, original_amount)
        
        assert discount_info["original_amount"] == original_amount
        assert discount_info["discounted_amount"] == 5000  # 50%?
        assert discount_info["discount_amount"] == 5000
        assert discount_info["discount_rate"] == 0.5
        assert discount_info["discount_type"] == "adhd_medical"
    
    def test_adhd_discount_application_without_eligibility(self):
        """?ADHD?"""
        user_id = "user_001"
        original_amount = 10000
        
        # ?
        with pytest.raises(Exception) as exc_info:
            care_points_system.apply_adhd_discount(user_id, original_amount)
        
        assert "?" in str(exc_info.value)
    
    def test_stripe_coupon_creation_for_adhd(self):
        """ADHD?Stripe?"""
        user_id = "user_001"
        
        # ?
        document_id = "doc_001"
        care_points_system.verify_adhd_medical_document(
            document_id, user_id, "diagnosis", "doctor_001"
        )
        
        # ?
        coupon = care_points_system.create_stripe_coupon_for_adhd(user_id)
        
        assert coupon["percent_off"] == 50
        assert coupon["duration"] == "once"
        assert coupon["max_redemptions"] == 1
        assert coupon["metadata"]["user_id"] == user_id
        assert coupon["metadata"]["discount_type"] == "adhd_medical"

class TestCarePointsAPI:
    """?API?"""
    
    def setup_method(self):
        """?"""
        # ?JWT?
        self.token = guardian_auth.create_guardian_jwt(
            "guardian_001",
            ["view_reports", "view_progress", "edit_tasks", "send_messages"]
        )
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # ?
        care_points_system.care_point_balances.clear()
        care_points_system.transactions.clear()
        care_points_system.medical_documents.clear()
    
    def test_corporate_purchase_initiation(self):
        """?"""
        response = client.post(
            "/care-points/corporate/purchase",
            json={
                "corporate_id": "corp_001",
                "amount": 15000
            },
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "payment_intent" in data
        assert data["discount_rate"] == 0.05  # 15,000?5%?
        assert data["discounted_amount"] == 14250  # 5%?
    
    def test_corporate_purchase_confirmation(self):
        """?"""
        response = client.post(
            "/care-points/corporate/confirm?payment_intent_id=pi_test_123&corporate_id=corp_001",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "purchase" in data
        assert "new_balance" in data
    
    def test_care_points_transfer_api(self):
        """?API?"""
        # ?
        care_points_system.care_point_balances["corp_001"] = 1000
        
        response = client.post(
            "/care-points/transfer",
            json={
                "from_corporate_id": "corp_001",
                "to_user_id": "user_001",
                "points": 500,
                "message": "?"
            },
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["transaction"]["points"] == 500
        assert data["corporate_balance"] == 500
        assert data["user_balance"] == 500
    
    def test_care_point_balance_retrieval(self):
        """?"""
        # ?
        care_points_system.care_point_balances["corp_001"] = 1500
        
        response = client.get(
            "/care-points/balance/corp_001",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["entity_id"] == "corp_001"
        assert data["balance"] == 1500
    
    def test_transaction_history_retrieval(self):
        """?"""
        # ?
        care_points_system.care_point_balances["corp_001"] = 1000
        care_points_system.transfer_care_points("corp_001", "user_001", 300)
        care_points_system.transfer_care_points("corp_001", "user_002", 200)
        
        response = client.get(
            "/care-points/transactions/corp_001",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["entity_id"] == "corp_001"
        assert len(data["transactions"]) == 2
        assert data["total_count"] == 2
    
    def test_adhd_document_verification_api(self):
        """ADHD?API?"""
        response = client.post(
            "/care-points/adhd/verify-document",
            json={
                "user_id": "user_001",
                "document_type": "diagnosis",
                "document_data": "base64_encoded_document_data",
                "verifier_id": "doctor_001"
            },
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["document"]["user_id"] == "user_001"
        assert data["document"]["verified"] is True
    
    def test_adhd_discount_application_api(self):
        """ADHD?API?"""
        # ま
        care_points_system.verify_adhd_medical_document(
            "doc_001", "user_001", "diagnosis", "doctor_001"
        )
        
        response = client.post(
            "/care-points/adhd/apply-discount",
            json={
                "user_id": "user_001",
                "original_amount": 20000
            },
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["discount_info"]["discounted_amount"] == 10000  # 50%?
        assert "stripe_coupon" in data
    
    def test_adhd_eligibility_check_api(self):
        """ADHD?API?"""
        # ?
        response = client.get(
            "/care-points/adhd/eligibility/user_001",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] is False
        assert data["discount_rate"] == 0.0
        
        # ?
        care_points_system.verify_adhd_medical_document(
            "doc_001", "user_001", "diagnosis", "doctor_001"
        )
        
        response = client.get(
            "/care-points/adhd/eligibility/user_001",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] is True
        assert data["discount_rate"] == 0.5
    
    def test_insufficient_permissions(self):
        """?"""
        # view-only?
        view_only_token = guardian_auth.create_guardian_jwt(
            "guardian_view_only",
            ["view_reports", "view_progress"]
        )
        view_only_headers = {"Authorization": f"Bearer {view_only_token}"}
        
        # ?
        response = client.post(
            "/care-points/corporate/purchase",
            json={"corporate_id": "corp_001", "amount": 10000},
            headers=view_only_headers
        )
        assert response.status_code == 403
        
        # ?
        response = client.post(
            "/care-points/transfer",
            json={
                "from_corporate_id": "corp_001",
                "to_user_id": "user_001",
                "points": 500
            },
            headers=view_only_headers
        )
        assert response.status_code == 403
        
        # ?
        response = client.get(
            "/care-points/balance/corp_001",
            headers=view_only_headers
        )
        assert response.status_code == 200

class TestIntegrationScenarios:
    """?"""
    
    def setup_method(self):
        """?"""
        self.token = guardian_auth.create_guardian_jwt(
            "guardian_001",
            ["view_reports", "view_progress", "edit_tasks", "send_messages"]
        )
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        care_points_system.care_point_balances.clear()
        care_points_system.transactions.clear()
        care_points_system.medical_documents.clear()
    
    def test_complete_care_points_workflow(self):
        """?"""
        # 1. ?
        purchase_response = client.post(
            "/care-points/corporate/purchase",
            json={"corporate_id": "corp_001", "amount": 50000},
            headers=self.headers
        )
        assert purchase_response.status_code == 200
        
        # 2. ?
        confirm_response = client.post(
            "/care-points/corporate/confirm?payment_intent_id=pi_test_123&corporate_id=corp_001",
            headers=self.headers
        )
        assert confirm_response.status_code == 200
        
        # 3. ユーザー
        transfer_response = client.post(
            "/care-points/transfer",
            json={
                "from_corporate_id": "corp_001",
                "to_user_id": "user_001",
                "points": 1000,
                "message": "?"
            },
            headers=self.headers
        )
        assert transfer_response.status_code == 200
        
        # 4. ?
        balance_response = client.get(
            "/care-points/balance/user_001",
            headers=self.headers
        )
        assert balance_response.status_code == 200
        assert balance_response.json()["balance"] == 1000
        
        # 5. ?
        history_response = client.get(
            "/care-points/transactions/corp_001",
            headers=self.headers
        )
        assert history_response.status_code == 200
        assert len(history_response.json()["transactions"]) == 1
    
    def test_adhd_discount_complete_workflow(self):
        """ADHD?"""
        # 1. ADHD?
        verify_response = client.post(
            "/care-points/adhd/verify-document",
            json={
                "user_id": "user_001",
                "document_type": "diagnosis",
                "document_data": "base64_encoded_document",
                "verifier_id": "doctor_001"
            },
            headers=self.headers
        )
        assert verify_response.status_code == 200
        
        # 2. ?
        eligibility_response = client.get(
            "/care-points/adhd/eligibility/user_001",
            headers=self.headers
        )
        assert eligibility_response.status_code == 200
        assert eligibility_response.json()["eligible"] is True
        
        # 3. ?
        discount_response = client.post(
            "/care-points/adhd/apply-discount",
            json={
                "user_id": "user_001",
                "original_amount": 30000
            },
            headers=self.headers
        )
        assert discount_response.status_code == 200
        discount_data = discount_response.json()
        assert discount_data["discount_info"]["discounted_amount"] == 15000
        assert "stripe_coupon" in discount_data

def run_tests():
    """?"""
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    run_tests()