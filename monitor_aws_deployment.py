#!/usr/bin/env python3
"""
AWS デプロイ監視スクリプト
デプロイ後のサービス状態とログを監視
"""

import boto3
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, List

class AWSMonitor:
    def __init__(self, region='ap-northeast-1'):
        self.region = region
        self.ecs = boto3.client('ecs', region_name=region)
        self.elbv2 = boto3.client('elbv2', region_name=region)
        self.logs = boto3.client('logs', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        
        self.cluster_name = 'therapeutic-app-cluster'
        self.service_name = 'therapeutic-app-service'
        self.log_group = '/ecs/therapeutic-app'
    
    def print_header(self, text: str):
        """ヘッダーを表示"""
        print(f"\n{'='*70}")
        print(f"  {text}")
        print(f"{'='*70}\n")
    
    def get_service_status(self) -> Dict:
        """ECSサービスの状態を取得"""
        try:
            response = self.ecs.describe_services(
                cluster=self.cluster_name,
                services=[self.service_name]
            )
            
            if response['services']:
                return response['services'][0]
            return None
            
        except Exception as e:
            print(f"❌ サービス状態取得エラー: {e}")
            return None
    
    def get_task_health(self) -> List[Dict]:
        """タスクのヘルス状態を取得"""
        try:
            # 実行中のタスクを取得
            tasks_response = self.ecs.list_tasks(
                cluster=self.cluster_name,
                serviceName=self.service_name,
                desiredStatus='RUNNING'
            )
            
            if not tasks_response['taskArns']:
                return []
            
            # タスクの詳細を取得
            tasks_detail = self.ecs.describe_tasks(
                cluster=self.cluster_name,
                tasks=tasks_response['taskArns']
            )
            
            return tasks_detail['tasks']
            
        except Exception as e:
            print(f"❌ タスク情報取得エラー: {e}")
            return []
    
    def get_alb_health(self) -> Dict:
        """ALBのヘルス状態を取得"""
        try:
            # ALBを取得
            albs = self.elbv2.describe_load_balancers(
                Names=['therapeutic-app-alb']
            )
            
            if not albs['LoadBalancers']:
                return None
            
            alb = albs['LoadBalancers'][0]
            
            # ターゲットグループを取得
            target_groups = self.elbv2.describe_target_groups(
                LoadBalancerArn=alb['LoadBalancerArn']
            )
            
            health_info = {
                'alb': alb,
                'target_groups': []
            }
            
            # 各ターゲットグループのヘルスをチェック
            for tg in target_groups['TargetGroups']:
                health = self.elbv2.describe_target_health(
                    TargetGroupArn=tg['TargetGroupArn']
                )
                health_info['target_groups'].append({
                    'name': tg['TargetGroupName'],
                    'health': health['TargetHealthDescriptions']
                })
            
            return health_info
            
        except Exception as e:
            print(f"❌ ALB情報取得エラー: {e}")
            return None
    
    def get_recent_logs(self, minutes: int = 5) -> List[str]:
        """最近のログを取得"""
        try:
            # ログストリームを取得
            streams = self.logs.describe_log_streams(
                logGroupName=self.log_group,
                orderBy='LastEventTime',
                descending=True,
                limit=5
            )
            
            if not streams['logStreams']:
                return []
            
            # 最新のログストリームからログを取得
            stream_name = streams['logStreams'][0]['logStreamName']
            
            start_time = int((datetime.now() - timedelta(minutes=minutes)).timestamp() * 1000)
            
            events = self.logs.get_log_events(
                logGroupName=self.log_group,
                logStreamName=stream_name,
                startTime=start_time,
                limit=50
            )
            
            return [event['message'] for event in events['events']]
            
        except Exception as e:
            print(f"❌ ログ取得エラー: {e}")
            return []
    
    def get_metrics(self) -> Dict:
        """CloudWatchメトリクスを取得"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=10)
            
            # CPU使用率
            cpu_response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/ECS',
                MetricName='CPUUtilization',
                Dimensions=[
                    {'Name': 'ServiceName', 'Value': self.service_name},
                    {'Name': 'ClusterName', 'Value': self.cluster_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average', 'Maximum']
            )
            
            # メモリ使用率
            memory_response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/ECS',
                MetricName='MemoryUtilization',
                Dimensions=[
                    {'Name': 'ServiceName', 'Value': self.service_name},
                    {'Name': 'ClusterName', 'Value': self.cluster_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average', 'Maximum']
            )
            
            return {
                'cpu': cpu_response['Datapoints'],
                'memory': memory_response['Datapoints']
            }
            
        except Exception as e:
            print(f"❌ メトリクス取得エラー: {e}")
            return {'cpu': [], 'memory': []}
    
    def display_service_status(self):
        """サービス状態を表示"""
        self.print_header("ECSサービス状態")
        
        service = self.get_service_status()
        
        if not service:
            print("❌ サービスが見つかりません")
            return
        
        status = service['status']
        running = service['runningCount']
        desired = service['desiredCount']
        pending = service['pendingCount']
        
        print(f"サービス名: {service['serviceName']}")
        print(f"ステータス: {status}")
        print(f"実行中タスク: {running}/{desired}")
        print(f"起動中タスク: {pending}")
        
        if running == desired and status == 'ACTIVE':
            print(f"\n✅ サービスは正常に稼働しています")
        elif running < desired:
            print(f"\n⚠️  一部のタスクが起動していません")
        else:
            print(f"\n⚠️  サービスに問題がある可能性があります")
        
        # デプロイメント情報
        if service.get('deployments'):
            print(f"\nデプロイメント:")
            for deployment in service['deployments']:
                print(f"  - ステータス: {deployment['status']}")
                print(f"    実行中: {deployment['runningCount']}")
                print(f"    タスク定義: {deployment['taskDefinition'].split('/')[-1]}")
    
    def display_task_health(self):
        """タスクのヘルス状態を表示"""
        self.print_header("タスクヘルス状態")
        
        tasks = self.get_task_health()
        
        if not tasks:
            print("実行中のタスクがありません")
            return
        
        for i, task in enumerate(tasks, 1):
            task_id = task['taskArn'].split('/')[-1]
            status = task['lastStatus']
            health = task.get('healthStatus', 'UNKNOWN')
            
            print(f"タスク {i}:")
            print(f"  ID: {task_id}")
            print(f"  ステータス: {status}")
            print(f"  ヘルス: {health}")
            
            # コンテナ情報
            for container in task.get('containers', []):
                print(f"  コンテナ: {container['name']}")
                print(f"    ステータス: {container.get('lastStatus', 'UNKNOWN')}")
                
                if container.get('networkInterfaces'):
                    ip = container['networkInterfaces'][0].get('privateIpv4Address')
                    print(f"    IP: {ip}")
            
            print()
    
    def display_alb_health(self):
        """ALBのヘルス状態を表示"""
        self.print_header("ロードバランサー状態")
        
        health_info = self.get_alb_health()
        
        if not health_info:
            print("ロードバランサー情報が取得できません")
            return
        
        alb = health_info['alb']
        print(f"ALB名: {alb['LoadBalancerName']}")
        print(f"DNS: {alb['DNSName']}")
        print(f"ステータス: {alb['State']['Code']}")
        
        print(f"\nターゲットグループ:")
        for tg in health_info['target_groups']:
            print(f"\n  {tg['name']}:")
            
            if not tg['health']:
                print(f"    ターゲットなし")
                continue
            
            healthy = sum(1 for t in tg['health'] if t['TargetHealth']['State'] == 'healthy')
            total = len(tg['health'])
            
            print(f"    ヘルシー: {healthy}/{total}")
            
            for target in tg['health']:
                state = target['TargetHealth']['State']
                target_id = target['Target']['Id']
                
                icon = "✅" if state == 'healthy' else "❌"
                print(f"    {icon} {target_id}: {state}")
                
                if state != 'healthy' and target['TargetHealth'].get('Reason'):
                    print(f"       理由: {target['TargetHealth']['Reason']}")
    
    def display_recent_logs(self, minutes: int = 5):
        """最近のログを表示"""
        self.print_header(f"最近{minutes}分のログ")
        
        logs = self.get_recent_logs(minutes)
        
        if not logs:
            print("ログが見つかりません")
            return
        
        for log in logs[-20:]:  # 最新20件
            print(log.strip())
    
    def display_metrics(self):
        """メトリクスを表示"""
        self.print_header("パフォーマンスメトリクス")
        
        metrics = self.get_metrics()
        
        if metrics['cpu']:
            cpu_data = sorted(metrics['cpu'], key=lambda x: x['Timestamp'])
            latest_cpu = cpu_data[-1] if cpu_data else None
            
            if latest_cpu:
                print(f"CPU使用率:")
                print(f"  平均: {latest_cpu.get('Average', 0):.2f}%")
                print(f"  最大: {latest_cpu.get('Maximum', 0):.2f}%")
        else:
            print("CPU使用率: データなし")
        
        if metrics['memory']:
            memory_data = sorted(metrics['memory'], key=lambda x: x['Timestamp'])
            latest_memory = memory_data[-1] if memory_data else None
            
            if latest_memory:
                print(f"\nメモリ使用率:")
                print(f"  平均: {latest_memory.get('Average', 0):.2f}%")
                print(f"  最大: {latest_memory.get('Maximum', 0):.2f}%")
        else:
            print("\nメモリ使用率: データなし")
    
    def monitor_continuous(self, interval: int = 30):
        """継続的に監視"""
        print(f"\n🔄 {interval}秒ごとに更新します (Ctrl+Cで終了)")
        
        try:
            while True:
                print(f"\n{'='*70}")
                print(f"  更新時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*70}")
                
                self.display_service_status()
                self.display_task_health()
                self.display_alb_health()
                self.display_metrics()
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n監視を終了します")
    
    def run_once(self):
        """1回だけ状態を表示"""
        self.display_service_status()
        self.display_task_health()
        self.display_alb_health()
        self.display_metrics()
        self.display_recent_logs()


def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         AWS デプロイ監視ツール                            ║
    ║   治療的ゲーミフィケーションアプリケーション              ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    monitor = AWSMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        monitor.monitor_continuous(interval)
    else:
        monitor.run_once()
        
        print(f"\n💡 ヒント:")
        print(f"   継続監視: python monitor_aws_deployment.py --continuous [秒]")
        print(f"   例: python monitor_aws_deployment.py --continuous 30")


if __name__ == '__main__':
    main()
