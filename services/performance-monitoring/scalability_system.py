"""
ストーリー
Cloud Run自動99.95%アプリ
"""

import time
import json
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict, deque
import random

# ログ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """?"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DOWN = "down"

class Region(Enum):
    """リスト"""
    ASIA_NORTHEAST1 = "asia-northeast1"  # ?
    US_CENTRAL1 = "us-central1"          # アプリ
    EUROPE_WEST1 = "europe-west1"       # ?

@dataclass
class ServiceHealth:
    """?"""
    service_name: str
    region: Region
    status: ServiceStatus
    response_time: float
    cpu_usage: float
    memory_usage: float
    request_count: int
    error_rate: float
    timestamp: datetime

@dataclass
class ScalingMetrics:
    """ストーリー"""
    current_instances: int
    target_instances: int
    cpu_utilization: float
    memory_utilization: float
    request_rate: float
    scaling_decision: str
    timestamp: datetime

class CloudRunScaler:
    """Cloud Run自動"""
    
    def __init__(self):
        self.min_instances = 1
        self.max_instances = 100
        self.target_cpu_utilization = 70.0  # 70%
        self.target_memory_utilization = 80.0  # 80%
        self.scale_up_threshold = 80.0
        self.scale_down_threshold = 50.0
        self.current_instances = 2
        self.scaling_history: List[ScalingMetrics] = []
        self.lock = threading.Lock()
    
    def evaluate_scaling(self, cpu_usage: float, memory_usage: float, 
                        request_rate: float) -> ScalingMetrics:
        """ストーリー"""
        with self.lock:
            target_instances = self.current_instances
            scaling_decision = "no_change"
            
            # CPU使用
            if cpu_usage > self.scale_up_threshold:
                # ストーリー
                scale_factor = cpu_usage / self.target_cpu_utilization
                target_instances = min(self.max_instances, 
                                     int(self.current_instances * scale_factor))
                scaling_decision = f"scale_up_cpu_{cpu_usage:.1f}%"
                
            elif cpu_usage < self.scale_down_threshold and self.current_instances > self.min_instances:
                # ストーリー
                scale_factor = cpu_usage / self.target_cpu_utilization
                target_instances = max(self.min_instances,
                                     int(self.current_instances * scale_factor))
                scaling_decision = f"scale_down_cpu_{cpu_usage:.1f}%"
            
            # メイン
            if memory_usage > self.target_memory_utilization:
                memory_scale_factor = memory_usage / self.target_memory_utilization
                memory_target = int(self.current_instances * memory_scale_factor)
                if memory_target > target_instances:
                    target_instances = min(self.max_instances, memory_target)
                    scaling_decision = f"scale_up_memory_{memory_usage:.1f}%"
            
            # リスト
            requests_per_instance = request_rate / max(self.current_instances, 1)
            if requests_per_instance > 100:  # ?100req/s?
                request_scale_factor = requests_per_instance / 50  # ?50req/s
                request_target = int(self.current_instances * request_scale_factor)
                if request_target > target_instances:
                    target_instances = min(self.max_instances, request_target)
                    scaling_decision = f"scale_up_requests_{requests_per_instance:.1f}req/s"
            
            metrics = ScalingMetrics(
                current_instances=self.current_instances,
                target_instances=target_instances,
                cpu_utilization=cpu_usage,
                memory_utilization=memory_usage,
                request_rate=request_rate,
                scaling_decision=scaling_decision,
                timestamp=datetime.now()
            )
            
            # ストーリー
            if target_instances != self.current_instances:
                logger.info(f"ストーリー: {self.current_instances} -> {target_instances} ({scaling_decision})")
                self.current_instances = target_instances
            
            self.scaling_history.append(metrics)
            
            # ?24?
            cutoff = datetime.now() - timedelta(hours=24)
            self.scaling_history = [m for m in self.scaling_history if m.timestamp > cutoff]
            
            return metrics
    
    def get_scaling_stats(self) -> Dict[str, Any]:
        """ストーリー"""
        with self.lock:
            if not self.scaling_history:
                return {"message": "ストーリー"}
            
            recent_history = [
                m for m in self.scaling_history 
                if m.timestamp > datetime.now() - timedelta(hours=1)
            ]
            
            if not recent_history:
                return {"message": "?"}
            
            scaling_events = [m for m in recent_history if m.scaling_decision != "no_change"]
            
            return {
                "current_instances": self.current_instances,
                "min_instances": self.min_instances,
                "max_instances": self.max_instances,
                "recent_scaling_events": len(scaling_events),
                "avg_cpu_utilization": sum(m.cpu_utilization for m in recent_history) / len(recent_history),
                "avg_memory_utilization": sum(m.memory_utilization for m in recent_history) / len(recent_history),
                "avg_request_rate": sum(m.request_rate for m in recent_history) / len(recent_history),
                "scaling_decisions": [m.scaling_decision for m in scaling_events[-10:]]
            }

class MultiRegionFailover:
    """?"""
    
    def __init__(self):
        self.regions = {
            Region.ASIA_NORTHEAST1: {"priority": 1, "healthy": True, "latency": 50},
            Region.US_CENTRAL1: {"priority": 2, "healthy": True, "latency": 150},
            Region.EUROPE_WEST1: {"priority": 3, "healthy": True, "latency": 200}
        }
        self.current_primary = Region.ASIA_NORTHEAST1
        self.failover_history: List[Dict] = []
        self.health_checks: Dict[Region, List[ServiceHealth]] = defaultdict(list)
        self.lock = threading.Lock()
    
    def update_region_health(self, region: Region, health: ServiceHealth):
        """リスト"""
        with self.lock:
            self.health_checks[region].append(health)
            
            # ?10?
            self.health_checks[region] = self.health_checks[region][-10:]
            
            # リスト
            recent_checks = self.health_checks[region][-3:]  # ?3?
            if len(recent_checks) >= 3:
                unhealthy_count = sum(1 for h in recent_checks 
                                    if h.status in [ServiceStatus.UNHEALTHY, ServiceStatus.DOWN])
                
                if unhealthy_count >= 2:  # 3?2?
                    self.regions[region]["healthy"] = False
                    logger.warning(f"リスト {region.value} が")
                else:
                    self.regions[region]["healthy"] = True
    
    def check_failover_needed(self) -> Optional[Region]:
        """?"""
        with self.lock:
            # ?
            if not self.regions[self.current_primary]["healthy"]:
                # ?
                sorted_regions = sorted(
                    self.regions.items(),
                    key=lambda x: x[1]["priority"]
                )
                
                for region, info in sorted_regions:
                    if info["healthy"] and region != self.current_primary:
                        return region
            
            return None
    
    def execute_failover(self, target_region: Region) -> bool:
        """?"""
        with self.lock:
            if target_region not in self.regions:
                return False
            
            if not self.regions[target_region]["healthy"]:
                return False
            
            old_primary = self.current_primary
            self.current_primary = target_region
            
            failover_event = {
                "timestamp": datetime.now(),
                "from_region": old_primary.value,
                "to_region": target_region.value,
                "reason": "health_check_failure",
                "duration_seconds": 0  # 実装
            }
            
            self.failover_history.append(failover_event)
            
            logger.info(f"?: {old_primary.value} -> {target_region.value}")
            
            return True
    
    def get_failover_stats(self) -> Dict[str, Any]:
        """?"""
        with self.lock:
            recent_failovers = [
                f for f in self.failover_history
                if f["timestamp"] > datetime.now() - timedelta(hours=24)
            ]
            
            region_health = {}
            for region, info in self.regions.items():
                recent_health = self.health_checks[region][-5:] if self.health_checks[region] else []
                avg_response_time = (
                    sum(h.response_time for h in recent_health) / len(recent_health)
                    if recent_health else 0
                )
                
                region_health[region.value] = {
                    "healthy": info["healthy"],
                    "priority": info["priority"],
                    "avg_response_time": avg_response_time,
                    "recent_checks": len(recent_health)
                }
            
            return {
                "current_primary": self.current_primary.value,
                "region_health": region_health,
                "failovers_24h": len(recent_failovers),
                "recent_failovers": recent_failovers[-5:],
                "total_regions": len(self.regions)
            }

class UptimeMonitor:
    """99.95%アプリ"""
    
    def __init__(self):
        self.uptime_target = 99.95  # 99.95%
        self.check_interval = 30  # 30?
        self.uptime_history: List[Dict] = []
        self.downtime_events: List[Dict] = []
        self.current_status = ServiceStatus.HEALTHY
        self.lock = threading.Lock()
    
    def record_uptime_check(self, is_up: bool, response_time: float = 0.0, 
                           error_message: str = None):
        """アプリ"""
        with self.lock:
            check_record = {
                "timestamp": datetime.now(),
                "is_up": is_up,
                "response_time": response_time,
                "error_message": error_message
            }
            
            self.uptime_history.append(check_record)
            
            # ?
            if not is_up and self.current_status == ServiceStatus.HEALTHY:
                # ?
                downtime_event = {
                    "start_time": datetime.now(),
                    "end_time": None,
                    "duration_seconds": 0,
                    "error_message": error_message
                }
                self.downtime_events.append(downtime_event)
                self.current_status = ServiceStatus.DOWN
                logger.error(f"?: {error_message}")
                
            elif is_up and self.current_status == ServiceStatus.DOWN:
                # ?
                if self.downtime_events:
                    last_event = self.downtime_events[-1]
                    if last_event["end_time"] is None:
                        last_event["end_time"] = datetime.now()
                        last_event["duration_seconds"] = (
                            last_event["end_time"] - last_event["start_time"]
                        ).total_seconds()
                        logger.info(f"?: {last_event['duration_seconds']:.1f}?")
                
                self.current_status = ServiceStatus.HEALTHY
            
            # ?30?
            cutoff = datetime.now() - timedelta(days=30)
            self.uptime_history = [h for h in self.uptime_history if h["timestamp"] > cutoff]
            self.downtime_events = [d for d in self.downtime_events if d["start_time"] > cutoff]
    
    def calculate_uptime_percentage(self, hours: int = 24) -> float:
        """アプリ"""
        with self.lock:
            cutoff = datetime.now() - timedelta(hours=hours)
            recent_checks = [h for h in self.uptime_history if h["timestamp"] > cutoff]
            
            if not recent_checks:
                return 100.0
            
            up_count = sum(1 for h in recent_checks if h["is_up"])
            return (up_count / len(recent_checks)) * 100
    
    def get_uptime_stats(self) -> Dict[str, Any]:
        """アプリ"""
        with self.lock:
            uptime_24h = self.calculate_uptime_percentage(24)
            uptime_7d = self.calculate_uptime_percentage(24 * 7)
            uptime_30d = self.calculate_uptime_percentage(24 * 30)
            
            # ?
            recent_downtime = [
                d for d in self.downtime_events
                if d["start_time"] > datetime.now() - timedelta(days=7)
            ]
            
            total_downtime_7d = sum(
                d.get("duration_seconds", 0) for d in recent_downtime
            )
            
            return {
                "current_status": self.current_status.value,
                "uptime_target": self.uptime_target,
                "uptime_24h": uptime_24h,
                "uptime_7d": uptime_7d,
                "uptime_30d": uptime_30d,
                "target_compliance_24h": uptime_24h >= self.uptime_target,
                "target_compliance_7d": uptime_7d >= self.uptime_target,
                "downtime_events_7d": len(recent_downtime),
                "total_downtime_7d_seconds": total_downtime_7d,
                "avg_response_time": self._calculate_avg_response_time(),
                "recent_downtime_events": recent_downtime[-5:]
            }
    
    def _calculate_avg_response_time(self) -> float:
        """?"""
        recent_checks = [
            h for h in self.uptime_history
            if h["timestamp"] > datetime.now() - timedelta(hours=1) and h["is_up"]
        ]
        
        if not recent_checks:
            return 0.0
        
        return sum(h["response_time"] for h in recent_checks) / len(recent_checks)

class ScalabilityManager:
    """ストーリー"""
    
    def __init__(self):
        self.scaler = CloudRunScaler()
        self.failover = MultiRegionFailover()
        self.uptime_monitor = UptimeMonitor()
        self.monitoring_active = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """?"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("ストーリー")
    
    def stop_monitoring(self):
        """?"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("ストーリー")
    
    def _monitoring_loop(self):
        """?"""
        while self.monitoring_active:
            try:
                # システム
                cpu_usage = random.uniform(30, 90)
                memory_usage = random.uniform(40, 85)
                request_rate = random.uniform(10, 200)
                
                # ストーリー
                scaling_metrics = self.scaler.evaluate_scaling(
                    cpu_usage, memory_usage, request_rate
                )
                
                # ヘルパー
                for region in Region:
                    is_healthy = random.random() > 0.05  # 95%の
                    status = ServiceStatus.HEALTHY if is_healthy else ServiceStatus.UNHEALTHY
                    
                    health = ServiceHealth(
                        service_name="therapeutic-app",
                        region=region,
                        status=status,
                        response_time=random.uniform(0.1, 2.0),
                        cpu_usage=cpu_usage,
                        memory_usage=memory_usage,
                        request_count=int(request_rate),
                        error_rate=random.uniform(0, 0.05),
                        timestamp=datetime.now()
                    )
                    
                    self.failover.update_region_health(region, health)
                
                # ?
                failover_target = self.failover.check_failover_needed()
                if failover_target:
                    self.failover.execute_failover(failover_target)
                
                # アプリ
                is_up = random.random() > 0.001  # 99.9%の
                self.uptime_monitor.record_uptime_check(
                    is_up, 
                    random.uniform(0.1, 1.0),
                    None if is_up else "Connection timeout"
                )
                
                time.sleep(30)  # 30?
                
            except Exception as e:
                logger.error(f"?: {e}")
                time.sleep(5)
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """?"""
        return {
            "scaling": self.scaler.get_scaling_stats(),
            "failover": self.failover.get_failover_stats(),
            "uptime": self.uptime_monitor.get_uptime_stats(),
            "timestamp": datetime.now().isoformat(),
            "monitoring_active": self.monitoring_active
        }
    
    def simulate_load_test(self, duration_seconds: int = 60):
        """?"""
        logger.info(f"?: {duration_seconds}?")
        
        start_time = time.time()
        test_results = []
        
        while time.time() - start_time < duration_seconds:
            # ?
            cpu_usage = random.uniform(70, 95)
            memory_usage = random.uniform(60, 90)
            request_rate = random.uniform(100, 500)
            
            scaling_result = self.scaler.evaluate_scaling(
                cpu_usage, memory_usage, request_rate
            )
            
            test_results.append({
                "timestamp": datetime.now(),
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "request_rate": request_rate,
                "instances": scaling_result.current_instances,
                "scaling_decision": scaling_result.scaling_decision
            })
            
            time.sleep(1)
        
        logger.info("?")
        
        return {
            "duration_seconds": duration_seconds,
            "total_samples": len(test_results),
            "max_instances": max(r["instances"] for r in test_results),
            "min_instances": min(r["instances"] for r in test_results),
            "scaling_events": len([r for r in test_results if r["scaling_decision"] != "no_change"]),
            "avg_cpu": sum(r["cpu_usage"] for r in test_results) / len(test_results),
            "avg_memory": sum(r["memory_usage"] for r in test_results) / len(test_results),
            "avg_request_rate": sum(r["request_rate"] for r in test_results) / len(test_results),
            "final_instances": test_results[-1]["instances"] if test_results else 0
        }

# ?
scalability_manager = ScalabilityManager()

if __name__ == "__main__":
    print("ストーリー")
    
    # ?
    scalability_manager.start_monitoring()
    
    try:
        # 10?
        print("10?...")
        time.sleep(10)
        
        # ?
        stats = scalability_manager.get_comprehensive_stats()
        print("\n=== ストーリー ===")
        print(json.dumps(stats, indent=2, ensure_ascii=False, default=str))
        
        # ?
        print("\n=== ? ===")
        load_test_result = scalability_manager.simulate_load_test(10)
        print(json.dumps(load_test_result, indent=2, ensure_ascii=False, default=str))
        
    finally:
        # ?
        scalability_manager.stop_monitoring()
        print("\n?")