"""
GDPR準拠
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import json

def test_gdpr_system():
    """GDPR準拠"""
    try:
        from main import GDPRComplianceSystem
        from privacy_by_design import PrivacyLevel
        
        print("=== GDPR準拠 ? ===\n")
        
        # システム
        print("1. システム...")
        gdpr_system = GDPRComplianceSystem()
        print("? システム")
        
        # ユーザー
        print("\n2. ユーザー...")
        test_user_id = "test_user_simple_001"
        birth_date = datetime.now() - timedelta(days=25*365)  # 25?
        
        registration_result = gdpr_system.register_user(
            test_user_id, birth_date, PrivacyLevel.ENHANCED
        )
        
        if registration_result["success"]:
            print("? ユーザー")
            print(f"  - ユーザーID: {registration_result['user_id']}")
            print(f"  - ?: {registration_result['age_group']}")
        else:
            print("? ユーザー")
            return False
        
        # ?
        print("\n3. ?...")
        consent_result = gdpr_system.request_consent(
            test_user_id, "therapeutic_data", "therapeutic_support"
        )
        
        if consent_result["success"]:
            print("? ?")
            print(f"  - ?ID: {consent_result['consent_id']}")
        else:
            print("? ?")
        
        # ?
        print("\n4. ?...")
        rights_result = gdpr_system.exercise_data_subject_right(
            test_user_id, "access", "?"
        )
        
        if rights_result["success"]:
            print("? ?")
            print(f"  - ?ID: {rights_result['request_id']}")
            print(f"  - ?: {rights_result['right_type']}")
        else:
            print("? ?")
        
        # デフォルト
        print("\n5. デフォルト...")
        export_result = gdpr_system.export_personal_data(
            test_user_id, "json", "all_data"
        )
        
        if export_result["success"]:
            print("? デフォルト")
            print(f"  - ?: {export_result.get('file_size', 'N/A')} bytes")
            print(f"  - ?: {export_result.get('checksum', 'N/A')[:16]}...")
        else:
            print("? デフォルト")
        
        # プレビュー
        print("\n6. プレビュー...")
        dashboard_result = gdpr_system.get_privacy_dashboard(test_user_id)
        
        if dashboard_result["success"]:
            print("? プレビュー")
            print(f"  - プレビュー: {dashboard_result['privacy_settings']['privacy_level']}")
            print(f"  - ?: {dashboard_result['consent_management']['total_consents']}")
        else:
            print("? プレビュー")
        
        # コア
        print("\n7. コア...")
        compliance_result = gdpr_system.run_compliance_check()
        
        if compliance_result["success"]:
            print("? コア")
            result = compliance_result["compliance_result"]
            print(f"  - ?: {result['rules_checked']}")
            print(f"  - 検証: {result['violations_found']}")
            print(f"  - ?: {result['overall_status']}")
        else:
            print("? コア")
        
        # システム
        print("\n8. システム...")
        health_result = gdpr_system.get_system_health()
        
        if health_result["success"]:
            print("? システム")
            health = health_result["health_status"]
            print(f"  - ?: {health['overall_health']}")
            print(f"  - ?: {health['metrics']['total_audit_logs']}")
            print(f"  - アプリ: {health['metrics']['active_violations']}")
        else:
            print("? システム")
        
        print("\n=== ? ===")
        print("? ?")
        return True
        
    except ImportError as e:
        print(f"? ?: {e}")
        print("?")
        return False
    
    except Exception as e:
        print(f"? ?: {e}")
        return False


def test_individual_components():
    """?"""
    print("\n=== ? ===\n")
    
    try:
        # プレビュー
        print("1. プレビュー...")
        from privacy_protection_system import PrivacyProtectionSystem
        privacy_system = PrivacyProtectionSystem()
        
        classification = privacy_system.classify_data("therapeutic_data")
        if classification:
            print(f"? デフォルト: {classification.category.value}")
        else:
            print("? デフォルト")
        
        # ?
        print("\n2. ?...")
        from audit_logging import AuditLoggingSystem, AuditEventType
        audit_system = AuditLoggingSystem()
        
        log_id = audit_system.log_data_access(
            user_id="test_user",
            actor_id="system",
            data_categories=["test_data"],
            action_description="?"
        )
        
        if log_id:
            print(f"? ?: {log_id[:16]}...")
        else:
            print("? ?")
        
        # デフォルト
        print("\n3. デフォルト...")
        from data_portability import DataPortabilityEngine, ExportFormat, DataPortabilityScope
        portability_engine = DataPortabilityEngine()
        
        request_id = portability_engine.create_portability_request(
            "test_user", DataPortabilityScope.ALL_DATA, ExportFormat.JSON
        )
        
        if request_id:
            print(f"? ?: {request_id[:16]}...")
        else:
            print("? ?")
        
        print("\n? ?")
        return True
        
    except Exception as e:
        print(f"? ?: {e}")
        return False


if __name__ == "__main__":
    print("GDPR準拠 - ?\n")
    
    # メイン
    main_test_success = test_gdpr_system()
    
    # ?
    component_test_success = test_individual_components()
    
    # ?
    print(f"\n{'='*50}")
    print("?:")
    print(f"メイン: {'? 成' if main_test_success else '? ?'}")
    print(f"?: {'? 成' if component_test_success else '? ?'}")
    
    if main_test_success and component_test_success:
        print("\n? ?")
        print("GDPR準拠")
    else:
        print("\n?  一般")
        print("システム")