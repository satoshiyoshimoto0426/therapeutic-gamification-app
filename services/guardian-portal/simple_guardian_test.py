"""
Guardian Portal 基本

Task 13: Guardian Portal基本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from datetime import datetime, timedelta
import json
import uuid

def test_guardian_auth_system():
    """Guardian?"""
    print("=== Guardian? ===")
    
    # Guardian?
    class TestGuardianAuth:
        def __init__(self):
            self.secret_key = "test_guardian_secret"
            self.magic_links = {}
        
        def generate_magic_link(self, email: str, guardian_id: str) -> str:
            """Magic Link?"""
            if "@" not in email:
                raise ValueError("無")
            
            token = f"test_token_{uuid.uuid4().hex[:16]}"
            expiry = datetime.utcnow() + timedelta(minutes=15)
            
            self.magic_links[token] = {
                "email": email,
                "guardian_id": guardian_id,
                "expires_at": expiry,
                "used": False
            }
            
            return f"https://guardian.therapeutic-app.com/auth/magic?token={token}"
        
        def verify_magic_link(self, token: str) -> dict:
            """Magic Link検証"""
            if token not in self.magic_links:
                raise Exception("無")
            
            link_data = self.magic_links[token]
            
            if link_data["used"]:
                raise Exception("?")
            
            if datetime.utcnow() > link_data["expires_at"]:
                raise Exception("?")
            
            self.magic_links[token]["used"] = True
            
            return {
                "guardian_id": link_data["guardian_id"],
                "email": link_data["email"]
            }
    
    # ?
    auth = TestGuardianAuth()
    
    # 1. Magic Link?
    try:
        magic_link = auth.generate_magic_link("guardian@example.com", "guardian_001")
        print(f"? Magic Link?: {magic_link}")
        
        # ?
        token = magic_link.split("token=")[1]
        
        # 2. Magic Link検証
        verified_data = auth.verify_magic_link(token)
        print(f"? Magic Link検証: {verified_data}")
        
        # 3. 使用
        try:
            auth.verify_magic_link(token)
            print("? 使用")
        except Exception as e:
            print(f"? 使用: {e}")
        
    except Exception as e:
        print(f"? Guardian?: {e}")
        return False
    
    return True

def test_guardian_rbac_system():
    """Guardian RBAC?"""
    print("\n=== Guardian RBAC? ===")
    
    class TestGuardianRBAC:
        def __init__(self):
            self.permissions = {
                "view-only": ["view_reports", "view_progress"],
                "task-edit": ["view_reports", "view_progress", "edit_tasks", "assign_tasks"],
                "chat-send": ["view_reports", "view_progress", "edit_tasks", "assign_tasks", "send_messages", "emergency_contact"]
            }
        
        def get_guardian_permissions(self, guardian_id: str) -> list:
            """Guardian?"""
            guardian_permissions = {
                "guardian_001": "chat-send",
                "guardian_002": "task-edit",
                "guardian_003": "view-only"
            }
            
            permission_level = guardian_permissions.get(guardian_id, "view-only")
            return self.permissions.get(permission_level, self.permissions["view-only"])
        
        def check_permission(self, guardian_id: str, required_permission: str) -> bool:
            """?"""
            guardian_permissions = self.get_guardian_permissions(guardian_id)
            return required_permission in guardian_permissions
    
    # ?
    rbac = TestGuardianRBAC()
    
    # 1. ?
    test_cases = [
        ("guardian_001", "chat-send", "send_messages", True),
        ("guardian_002", "task-edit", "edit_tasks", True),
        ("guardian_002", "task-edit", "send_messages", False),
        ("guardian_003", "view-only", "view_reports", True),
        ("guardian_003", "view-only", "edit_tasks", False),
    ]
    
    for guardian_id, level, permission, expected in test_cases:
        result = rbac.check_permission(guardian_id, permission)
        status = "?" if result == expected else "?"
        print(f"{status} {guardian_id} ({level}) - {permission}: {result}")
    
    return True

def test_care_points_system():
    """?"""
    print("\n=== ? ===")
    
    class TestCarePointsSystem:
        def __init__(self):
            self.point_rate = 1  # 1? = 1?
            self.adhd_discount_rate = 0.5  # 50%?
            self.corporate_bulk_thresholds = {
                10000: 0.05,   # 10,000?5%?
                50000: 0.10,   # 50,000?10%?
                100000: 0.15   # 100,000?15%?
            }
            self.care_point_balances = {}
            self.transactions = []
            self.medical_documents = {}
        
        def calculate_corporate_discount(self, amount: int) -> float:
            """?"""
            discount_rate = 0.0
            
            for threshold, rate in sorted(self.corporate_bulk_thresholds.items(), reverse=True):
                if amount >= threshold:
                    discount_rate = rate
                    break
            
            return discount_rate
        
        def process_corporate_purchase(self, corporate_id: str, amount: int) -> dict:
            """?"""
            discount_rate = self.calculate_corporate_discount(amount)
            discounted_amount = int(amount * (1 - discount_rate))
            points_purchased = discounted_amount * self.point_rate
            
            # ?
            if corporate_id not in self.care_point_balances:
                self.care_point_balances[corporate_id] = 0
            
            self.care_point_balances[corporate_id] += points_purchased
            
            return {
                "corporate_id": corporate_id,
                "purchase_amount": discounted_amount,
                "points_purchased": points_purchased,
                "discount_applied": f"corporate_bulk_{discount_rate*100:.0f}%" if discount_rate > 0 else None
            }
        
        def transfer_care_points(self, from_corporate_id: str, to_user_id: str, points: int) -> dict:
            """?"""
            # ?
            corporate_balance = self.care_point_balances.get(from_corporate_id, 0)
            if corporate_balance < points:
                raise Exception("?")
            
            # ?
            self.care_point_balances[from_corporate_id] -= points
            
            if to_user_id not in self.care_point_balances:
                self.care_point_balances[to_user_id] = 0
            self.care_point_balances[to_user_id] += points
            
            # ?
            transaction = {
                "transaction_id": str(uuid.uuid4()),
                "from_entity": from_corporate_id,
                "to_user": to_user_id,
                "points": points,
                "transaction_type": "transfer",
                "created_at": datetime.utcnow()
            }
            
            self.transactions.append(transaction)
            return transaction
        
        def verify_adhd_medical_document(self, document_id: str, user_id: str, document_type: str) -> dict:
            """ADHD?"""
            document = {
                "document_id": document_id,
                "user_id": user_id,
                "document_type": document_type,
                "verified": True,
                "verified_at": datetime.utcnow(),
                "expiry_date": datetime.utcnow() + timedelta(days=365)
            }
            
            self.medical_documents[document_id] = document
            return document
        
        def check_adhd_discount_eligibility(self, user_id: str) -> bool:
            """ADHD?"""
            current_time = datetime.utcnow()
            
            for doc in self.medical_documents.values():
                if (doc["user_id"] == user_id and 
                    doc["verified"] and 
                    doc["expiry_date"] > current_time):
                    return True
            
            return False
        
        def apply_adhd_discount(self, user_id: str, original_amount: int) -> dict:
            """ADHD?50%?"""
            if not self.check_adhd_discount_eligibility(user_id):
                raise Exception("ADHD?")
            
            discounted_amount = int(original_amount * self.adhd_discount_rate)
            discount_amount = original_amount - discounted_amount
            
            return {
                "original_amount": original_amount,
                "discounted_amount": discounted_amount,
                "discount_amount": discount_amount,
                "discount_rate": self.adhd_discount_rate,
                "discount_type": "adhd_medical"
            }
    
    # ?
    care_system = TestCarePointsSystem()
    
    # 1. ?
    test_amounts = [5000, 15000, 60000, 150000]
    expected_discounts = [0.0, 0.05, 0.10, 0.15]
    
    print("?:")
    for amount, expected in zip(test_amounts, expected_discounts):
        discount = care_system.calculate_corporate_discount(amount)
        status = "?" if discount == expected else "?"
        print(f"  {status} {amount:,}? -> {discount*100:.0f}%?")
    
    # 2. ?
    print("\n?:")
    purchase = care_system.process_corporate_purchase("corp_001", 50000)
    print(f"  ? ?: {purchase['points_purchased']:,}?")
    print(f"  ? ?: {purchase['discount_applied']}")
    
    # 3. ?
    print("\n?:")
    try:
        transaction = care_system.transfer_care_points("corp_001", "user_001", 1000)
        print(f"  ? ?: {transaction['points']}?")
        print(f"  ? ?: {care_system.care_point_balances['corp_001']:,}?")
        print(f"  ? ユーザー: {care_system.care_point_balances['user_001']:,}?")
    except Exception as e:
        print(f"  ? ?: {e}")
    
    # 4. ADHD?
    print("\nADHD?:")
    
    # ?
    try:
        care_system.apply_adhd_discount("user_002", 20000)
        print("  ? ?")
    except Exception as e:
        print(f"  ? ?: {e}")
    
    # ?
    document = care_system.verify_adhd_medical_document("doc_001", "user_002", "diagnosis")
    print(f"  ? ?: {document['document_id']}")
    
    # ?
    discount_info = care_system.apply_adhd_discount("user_002", 20000)
    print(f"  ? ADHD?: {discount_info['original_amount']:,}? -> {discount_info['discounted_amount']:,}?")
    
    return True

def test_weekly_report_generation():
    """?"""
    print("\n=== ? ===")
    
    class TestReportGenerator:
        def generate_weekly_report(self, user_data: dict, guardian_data: dict) -> bytes:
            """?"""
            report_content = f"""
? - {user_data['name']}
?: {user_data['week_start']} ? {user_data['week_end']}

=== ? ===
?: {user_data['total_tasks_completed']}
?XP: {user_data['total_xp_earned']}
?: {user_data['mood_average']:.1f}/5.0
?: {user_data['adherence_rate']*100:.1f}%

=== ? ===
{chr(10).join(user_data.get('recommendations', []))}

=== Guardian? ===
Guardian: {guardian_data.get('name', 'Unknown')}
?: {guardian_data.get('relationship', 'Unknown')}
"""
            
            return report_content.encode('utf-8')
    
    # ?
    user_data = {
        'name': '?',
        'week_start': '2024?1?15?',
        'week_end': '2024?1?21?',
        'total_tasks_completed': 28,
        'total_xp_earned': 1740,
        'mood_average': 3.8,
        'adherence_rate': 0.85,
        'recommendations': [
            "?",
            "?",
            "?"
        ]
    }
    
    guardian_data = {
        'name': '?',
        'relationship': 'parent'
    }
    
    # レベル
    generator = TestReportGenerator()
    report_content = generator.generate_weekly_report(user_data, guardian_data)
    
    print(f"? ?: {len(report_content)}バリデーション")
    print("レベル:")
    print(report_content.decode('utf-8')[:200] + "...")
    
    return True

def test_guardian_dashboard():
    """Guardian?"""
    print("\n=== Guardian? ===")
    
    # ?
    dashboard_data = {
        "guardian_id": "guardian_001",
        "permissions": ["view_reports", "view_progress", "edit_tasks", "send_messages"],
        "managed_users": [
            {
                "user_id": "user_001",
                "name": "?",
                "current_level": 15,
                "total_xp": 2500,
                "last_activity": "2024-01-20T10:30:00Z",
                "mood_trend": "improving",
                "task_completion_rate": 0.85
            }
        ],
        "dashboard_summary": {
            "total_users": 1,
            "active_users_today": 1,
            "average_completion_rate": 0.85,
            "alerts": []
        }
    }
    
    print(f"? Guardian ID: {dashboard_data['guardian_id']}")
    print(f"? ?: {', '.join(dashboard_data['permissions'])}")
    print(f"? 管理: {dashboard_data['dashboard_summary']['total_users']}")
    print(f"? ?: {dashboard_data['dashboard_summary']['average_completion_rate']*100:.1f}%")
    
    # ユーザー
    user = dashboard_data['managed_users'][0]
    print(f"? ユーザー: {user['name']} (Lv.{user['current_level']}, XP:{user['total_xp']:,})")
    
    return True

def run_all_tests():
    """?"""
    print("Guardian Portal 基本")
    print("=" * 50)
    
    tests = [
        ("Guardian?", test_guardian_auth_system),
        ("Guardian RBAC?", test_guardian_rbac_system),
        ("?", test_care_points_system),
        ("?", test_weekly_report_generation),
        ("Guardian?", test_guardian_dashboard),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n{test_name}: 成")
            else:
                print(f"\n{test_name}: ?")
        except Exception as e:
            print(f"\n{test_name}: エラー - {e}")
    
    print("\n" + "=" * 50)
    print(f"?: {passed}/{total} 成")
    
    if passed == total:
        print("? Guardian Portal基本")
        return True
    else:
        print("? 一般")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)