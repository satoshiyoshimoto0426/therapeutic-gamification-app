"""
Guardian Portal の
"""

from main import guardian_auth, guardian_rbac
from care_points_system import care_points_system

def test_basic_functionality():
    """基本"""
    print("=== Guardian Portal 基本 ===")
    
    # 1. Magic Link?
    print("\n1. Magic Link?")
    try:
        magic_link = guardian_auth.generate_magic_link(
            "test@example.com", 
            "guardian_001"
        )
        print(f"? Magic Link?: {magic_link[:50]}...")
    except Exception as e:
        print(f"? Magic Link?: {e}")
    
    # 2. JWT ?
    print("\n2. JWT ?")
    try:
        token = guardian_auth.create_guardian_jwt(
            "guardian_001", 
            ["view_reports", "edit_tasks"]
        )
        payload = guardian_auth.verify_guardian_jwt(token)
        print(f"? JWT?: {payload['guardian_id']}")
    except Exception as e:
        print(f"? JWT?: {e}")
    
    # 3. ?
    print("\n3. ?")
    try:
        # view-only?
        view_only_perms = guardian_rbac.get_guardian_permissions("guardian_003")
        has_view = guardian_rbac.check_permission("guardian_003", "view_reports")
        has_edit = guardian_rbac.check_permission("guardian_003", "edit_tasks")
        
        print(f"? view-only?: view_reports={has_view}, edit_tasks={has_edit}")
        
        # chat-send?
        chat_perms = guardian_rbac.get_guardian_permissions("guardian_001")
        has_chat = guardian_rbac.check_permission("guardian_001", "send_messages")
        
        print(f"? chat-send?: send_messages={has_chat}")
    except Exception as e:
        print(f"? ?: {e}")
    
    # 4. ?
    print("\n4. ?")
    try:
        # ?
        discount = care_points_system.calculate_corporate_discount(50000)
        print(f"? 50,000?: {discount*100}%")
        
        # ?
        purchase = care_points_system.process_corporate_purchase(
            "corp_001", 10000, "pi_test_123"
        )
        print(f"? ?: {purchase.points_purchased}?")
        
        # ?
        transaction = care_points_system.transfer_care_points(
            "corp_001", "user_001", 500
        )
        print(f"? ?: {transaction.points}?")
        
        # ?
        corp_balance = care_points_system.get_care_point_balance("corp_001")
        user_balance = care_points_system.get_care_point_balance("user_001")
        print(f"? ? - ?: {corp_balance}, ユーザー: {user_balance}")
        
    except Exception as e:
        print(f"? ?: {e}")
    
    # 5. ADHD?
    print("\n5. ADHD?")
    try:
        # ?
        document = care_points_system.verify_adhd_medical_document(
            "doc_001", "user_001", "diagnosis", "doctor_001"
        )
        print(f"? ?: {document.document_id}")
        
        # ?
        eligible = care_points_system.check_adhd_discount_eligibility("user_001")
        print(f"? ADHD?: {eligible}")
        
        # ?
        if eligible:
            discount_info = care_points_system.apply_adhd_discount("user_001", 20000)
            print(f"? ADHD?: {discount_info['discounted_amount']}?")
        
    except Exception as e:
        print(f"? ADHD?: {e}")
    
    print("\n=== ? ===")

if __name__ == "__main__":
    test_basic_functionality()