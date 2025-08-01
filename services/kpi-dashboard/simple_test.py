"""
KPI Dashboard Service ?
"""
import asyncio
import json
from datetime import datetime, date, timedelta
from main import KPIDashboardEngine, UserState

async def test_kpi_dashboard():
    """KPI?"""
    print("=== KPI Dashboard Service ? ===")
    
    # KPI?
    dashboard = KPIDashboardEngine()
    print(f"? ?")
    print(f"  - メイン: {len(dashboard.kpi_metrics)}")
    print(f"  - ?: {len(dashboard.user_data)}")
    
    # ?
    print("\n=== ? ===")
    critical_metrics = [m for m in dashboard.kpi_metrics.values() if m.is_critical]
    for metric in critical_metrics:
        print(f"? {metric.name}")
        print(f"  - ?: {metric.current_value:.3f} {metric.unit}")
        print(f"  - ?: {metric.target_value:.3f} {metric.unit}")
        achievement = (metric.current_value / metric.target_value * 100) if metric.target_value > 0 else 0
        print(f"  - ?: {achievement:.1f}%")
    
    # KPI計算
    print("\n=== KPI計算 ===")
    calculation_result = await dashboard.calculate_kpi_metrics()
    print(f"? KPI計算")
    print(f"  - ?: {calculation_result['metrics_updated']}")
    print(f"  - ?: {calculation_result['alerts_generated']}")
    
    # ?
    print("\n=== ? ===")
    summary = await dashboard.get_dashboard_summary()
    print(f"? ?: {summary['overall_health_score']:.3f}")
    print(f"? ?: {summary['total_users']}")
    print(f"? アプリ: {len(summary['active_alerts'])}")
    
    # ?
    print("\n=== ? ===")
    for metric_id, metric_data in summary['critical_metrics'].items():
        print(f"? {metric_data['name']}")
        print(f"  ?: {metric_data['current_value']:.3f} {metric_data['unit']}")
        print(f"  ?: {metric_data['target_value']:.3f} {metric_data['unit']}")
        print(f"  ?: {metric_data['achievement_rate']:.1f}%")
        print(f"  ?: {metric_data['trend']}")
    
    # アプリ
    if summary['active_alerts']:
        print("\n=== アプリ ===")
        for alert in summary['active_alerts']:
            print(f"?  {alert['severity'].upper()}: {alert['message']}")
            print(f"   メイン: {alert['metric_name']}")
            print(f"   ?: {alert['created_at']}")
    else:
        print("\n? アプリ")
    
    # ?
    if summary['summary_insights']:
        print("\n=== システム ===")
        for i, insight in enumerate(summary['summary_insights'], 1):
            print(f"{i}. {insight}")
    
    # ?
    print("\n=== ? ===")
    d1_details = await dashboard.get_metric_details("d1_retention")
    print(f"? D1リスト")
    print(f"  - ?: {len(d1_details['historical_data'])}")
    print(f"  - ?: {d1_details['trend_analysis']['trend']}")
    print(f"  - ?: {d1_details['trend_analysis']['change_rate']:.3f}")
    
    # ユーザー
    print("\n=== ユーザー ===")
    state_counts = {}
    for user in dashboard.user_data.values():
        state = user.current_state.value
        state_counts[state] = state_counts.get(state, 0) + 1
    
    total_users = len(dashboard.user_data)
    for state, count in state_counts.items():
        percentage = (count / total_users) * 100
        print(f"  {state}: {count}? ({percentage:.1f}%)")
    
    # ?
    print("\n=== ? ===")
    paying_users = [u for u in dashboard.user_data.values() if u.revenue_generated > 0]
    total_revenue = sum(u.revenue_generated for u in dashboard.user_data.values())
    avg_revenue_per_paying_user = total_revenue / len(paying_users) if paying_users else 0
    
    print(f"  ?: ?{total_revenue:.0f}")
    print(f"  ?: {len(paying_users)}?")
    print(f"  ?: {len(paying_users)/total_users*100:.1f}%")
    print(f"  ?: ?{avg_revenue_per_paying_user:.0f}")
    
    # 治療
    print("\n=== 治療 ===")
    efficacy_users = [u for u in dashboard.user_data.values() 
                     if u.therapeutic_progress.get("self_efficacy", 0) > 0]
    avg_efficacy = sum(u.therapeutic_progress.get("self_efficacy", 0) 
                      for u in efficacy_users) / len(efficacy_users) if efficacy_users else 0
    
    cbt_users = [u for u in dashboard.user_data.values() 
                if u.therapeutic_progress.get("cbt_engagement", 0) > 0]
    
    print(f"  自動: {len(efficacy_users)}?")
    print(f"  ?: {avg_efficacy:.3f}")
    print(f"  CBT?: {len(cbt_users)}?")
    print(f"  CBT?: {len(cbt_users)/total_users*100:.1f}%")
    
    print("\n=== ? ===")
    return True

def test_api_endpoints():
    """API エラー"""
    print("\n=== API エラー ===")
    
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    
    # ?
    response = client.get("/kpi/dashboard")
    assert response.status_code == 200
    print("? GET /kpi/dashboard")
    
    # メイン
    response = client.get("/kpi/metrics")
    assert response.status_code == 200
    print("? GET /kpi/metrics")
    
    # ?
    response = client.get("/kpi/metrics/d1_retention")
    assert response.status_code == 200
    print("? GET /kpi/metrics/d1_retention")
    
    # アプリ
    response = client.get("/kpi/alerts")
    assert response.status_code == 200
    print("? GET /kpi/alerts")
    
    # KPI計算
    response = client.post("/kpi/calculate")
    assert response.status_code == 200
    print("? POST /kpi/calculate")
    
    # システム
    response = client.get("/kpi/health")
    assert response.status_code == 200
    print("? GET /kpi/health")
    
    print("? ?APIエラー")

if __name__ == "__main__":
    # ?
    asyncio.run(test_kpi_dashboard())
    
    # API ?
    test_api_endpoints()
    
    print("\n? KPI Dashboard Service ?")