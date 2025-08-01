"""
?
API?
"""

import time
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
from functools import wraps
import logging
from collections import defaultdict, deque
import threading

# ログ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """?"""
    endpoint: str
    response_time: float
    timestamp: datetime
    status_code: int
    cache_hit: bool = False
    user_id: Optional[str] = None

@dataclass
class RateLimitInfo:
    """レベル"""
    ip_address: str
    request_count: int
    window_start: datetime
    blocked_until: Optional[datetime] = None

class PerformanceMonitor:
    """?"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.p95_target = 1.2  # 1.2?P95レベル
        self.metrics_lock = threading.Lock()
        
    def record_metric(self, metric: PerformanceMetrics):
        """メイン"""
        with self.metrics_lock:
            self.metrics.append(metric)
            # ?24?
            cutoff = datetime.now() - timedelta(hours=24)
            self.metrics = [m for m in self.metrics if m.timestamp > cutoff]
    
    def get_p95_latency(self, endpoint: Optional[str] = None, 
                       hours: int = 1) -> float:
        """P95レベル"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        with self.metrics_lock:
            filtered_metrics = [
                m for m in self.metrics 
                if m.timestamp > cutoff and (endpoint is None or m.endpoint == endpoint)
            ]
        
        if not filtered_metrics:
            return 0.0
        
        response_times = sorted([m.response_time for m in filtered_metrics])
        p95_index = int(len(response_times) * 0.95)
        return response_times[p95_index] if p95_index < len(response_times) else response_times[-1]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """?"""
        with self.metrics_lock:
            if not self.metrics:
                return {"error": "メイン"}
            
            recent_metrics = [
                m for m in self.metrics 
                if m.timestamp > datetime.now() - timedelta(hours=1)
            ]
            
            if not recent_metrics:
                return {"error": "?"}
            
            response_times = [m.response_time for m in recent_metrics]
            cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
            
            return {
                "total_requests": len(recent_metrics),
                "avg_response_time": sum(response_times) / len(response_times),
                "p95_latency": self.get_p95_latency(),
                "p95_target": self.p95_target,
                "p95_compliance": self.get_p95_latency() <= self.p95_target,
                "cache_hit_rate": cache_hits / len(recent_metrics) if recent_metrics else 0,
                "endpoints": self._get_endpoint_stats(recent_metrics)
            }
    
    def _get_endpoint_stats(self, metrics: List[PerformanceMetrics]) -> Dict[str, Dict]:
        """エラー"""
        endpoint_stats = defaultdict(list)
        
        for metric in metrics:
            endpoint_stats[metric.endpoint].append(metric.response_time)
        
        result = {}
        for endpoint, times in endpoint_stats.items():
            result[endpoint] = {
                "count": len(times),
                "avg_time": sum(times) / len(times),
                "max_time": max(times),
                "min_time": min(times)
            }
        
        return result

class CacheManager:
    """?"""
    
    def __init__(self):
        # メインRedisに
        self.memory_cache: Dict[str, Dict] = {}
        self.cache_ttl = {
            "user_profile": 300,      # 5?
            "mandala_grid": 600,      # 10?
            "story_content": 1800,    # 30?
            "task_list": 180,         # 3?
            "leaderboard": 900        # 15?
        }
        self.cache_lock = threading.Lock()
    
    def get(self, key: str, cache_type: str = "default") -> Optional[Any]:
        """?"""
        with self.cache_lock:
            cache_entry = self.memory_cache.get(key)
            
            if cache_entry is None:
                return None
            
            # TTL?
            ttl = self.cache_ttl.get(cache_type, 300)
            if datetime.now() - cache_entry["timestamp"] > timedelta(seconds=ttl):
                del self.memory_cache[key]
                return None
            
            return cache_entry["data"]
    
    def set(self, key: str, value: Any, cache_type: str = "default"):
        """?"""
        with self.cache_lock:
            self.memory_cache[key] = {
                "data": value,
                "timestamp": datetime.now(),
                "type": cache_type
            }
    
    def invalidate(self, pattern: str = None):
        """?"""
        with self.cache_lock:
            if pattern is None:
                self.memory_cache.clear()
            else:
                keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
                for key in keys_to_remove:
                    del self.memory_cache[key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """?"""
        with self.cache_lock:
            total_entries = len(self.memory_cache)
            type_counts = defaultdict(int)
            
            for entry in self.memory_cache.values():
                type_counts[entry.get("type", "default")] += 1
            
            return {
                "total_entries": total_entries,
                "type_distribution": dict(type_counts),
                "memory_usage_estimate": total_entries * 1024  # ?
            }

class RateLimiter:
    """レベル120req/min/IP?"""
    
    def __init__(self, max_requests: int = 120, window_minutes: int = 1):
        self.max_requests = max_requests
        self.window_seconds = window_minutes * 60
        self.request_history: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, datetime] = {}
        self.lock = threading.Lock()
    
    def is_allowed(self, ip_address: str) -> bool:
        """リスト"""
        current_time = datetime.now()
        
        with self.lock:
            # ?
            if ip_address in self.blocked_ips:
                if current_time < self.blocked_ips[ip_address]:
                    return False
                else:
                    del self.blocked_ips[ip_address]
            
            # リスト
            history = self.request_history[ip_address]
            
            # ?
            cutoff_time = current_time - timedelta(seconds=self.window_seconds)
            while history and history[0] < cutoff_time:
                history.popleft()
            
            # レベル
            if len(history) >= self.max_requests:
                # 1?
                self.blocked_ips[ip_address] = current_time + timedelta(minutes=1)
                logger.warning(f"IP {ip_address} が")
                return False
            
            # リスト
            history.append(current_time)
            return True
    
    def get_rate_limit_info(self, ip_address: str) -> RateLimitInfo:
        """レベル"""
        current_time = datetime.now()
        
        with self.lock:
            history = self.request_history[ip_address]
            cutoff_time = current_time - timedelta(seconds=self.window_seconds)
            
            # ?
            valid_requests = sum(1 for req_time in history if req_time > cutoff_time)
            
            return RateLimitInfo(
                ip_address=ip_address,
                request_count=valid_requests,
                window_start=cutoff_time,
                blocked_until=self.blocked_ips.get(ip_address)
            )
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """レベル"""
        with self.lock:
            active_ips = len(self.request_history)
            blocked_ips = len(self.blocked_ips)
            
            # ?IPを
            top_ips = []
            for ip, history in self.request_history.items():
                if history:
                    top_ips.append((ip, len(history)))
            
            top_ips.sort(key=lambda x: x[1], reverse=True)
            
            return {
                "active_ips": active_ips,
                "blocked_ips": blocked_ips,
                "top_active_ips": top_ips[:10],
                "max_requests_per_window": self.max_requests,
                "window_seconds": self.window_seconds
            }

class QueryOptimizer:
    """デフォルト"""
    
    def __init__(self):
        self.query_cache = CacheManager()
        self.slow_query_threshold = 0.5  # 500ms
        self.slow_queries: List[Dict] = []
        self.query_lock = threading.Lock()
    
    def optimize_user_query(self, user_id: str) -> Dict[str, Any]:
        """ユーザー"""
        cache_key = f"user_optimized_{user_id}"
        cached_result = self.query_cache.get(cache_key, "user_profile")
        
        if cached_result:
            return cached_result
        
        # ?
        start_time = time.time()
        
        # システム
        result = {
            "user_profile": {"uid": user_id, "level": 5, "xp": 1250},
            "active_tasks": [{"id": "task1", "type": "routine", "difficulty": 2}],
            "crystal_progress": {"Self-Discipline": 75, "Empathy": 60},
            "recent_achievements": ["level_up", "task_streak_7"]
        }
        
        query_time = time.time() - start_time
        
        # ストーリー
        if query_time > self.slow_query_threshold:
            with self.query_lock:
                self.slow_queries.append({
                    "query_type": "user_optimized",
                    "user_id": user_id,
                    "execution_time": query_time,
                    "timestamp": datetime.now()
                })
        
        self.query_cache.set(cache_key, result, "user_profile")
        return result
    
    def optimize_mandala_query(self, user_id: str) -> Dict[str, Any]:
        """Mandala?"""
        cache_key = f"mandala_optimized_{user_id}"
        cached_result = self.query_cache.get(cache_key, "mandala_grid")
        
        if cached_result:
            return cached_result
        
        start_time = time.time()
        
        # ?Mandalaデフォルト
        result = {
            "grid": [[None for _ in range(9)] for _ in range(9)],
            "unlocked_cells": 15,
            "current_chapter": "Self-Discipline",
            "next_unlock_requirements": {"xp": 100, "tasks": 3}
        }
        
        query_time = time.time() - start_time
        
        if query_time > self.slow_query_threshold:
            with self.query_lock:
                self.slow_queries.append({
                    "query_type": "mandala_optimized",
                    "user_id": user_id,
                    "execution_time": query_time,
                    "timestamp": datetime.now()
                })
        
        self.query_cache.set(cache_key, result, "mandala_grid")
        return result
    
    def get_slow_query_report(self) -> Dict[str, Any]:
        """ストーリー"""
        with self.query_lock:
            if not self.slow_queries:
                return {"message": "ストーリー"}
            
            # ?1?
            recent_cutoff = datetime.now() - timedelta(hours=1)
            recent_slow = [q for q in self.slow_queries if q["timestamp"] > recent_cutoff]
            
            if not recent_slow:
                return {"message": "?"}
            
            # ?
            avg_time = sum(q["execution_time"] for q in recent_slow) / len(recent_slow)
            max_time = max(q["execution_time"] for q in recent_slow)
            
            query_types = defaultdict(int)
            for query in recent_slow:
                query_types[query["query_type"]] += 1
            
            return {
                "total_slow_queries": len(recent_slow),
                "average_execution_time": avg_time,
                "max_execution_time": max_time,
                "slow_query_threshold": self.slow_query_threshold,
                "query_type_distribution": dict(query_types),
                "recent_slow_queries": recent_slow[-10:]  # ?10?
            }

# デフォルト
def monitor_performance(endpoint_name: str):
    """?"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            cache_hit = False
            status_code = 200
            
            try:
                result = func(*args, **kwargs)
                
                # ?cache_hit?
                if isinstance(result, dict) and result.get("_cache_hit"):
                    cache_hit = True
                    result.pop("_cache_hit", None)
                
                return result
                
            except Exception as e:
                status_code = 500
                logger.error(f"エラー {endpoint_name} で: {e}")
                raise
            
            finally:
                execution_time = time.time() - start_time
                
                metric = PerformanceMetrics(
                    endpoint=endpoint_name,
                    response_time=execution_time,
                    timestamp=datetime.now(),
                    status_code=status_code,
                    cache_hit=cache_hit
                )
                
                # ?
                if hasattr(wrapper, '_monitor'):
                    wrapper._monitor.record_metric(metric)
        
        return wrapper
    return decorator

def rate_limit(max_requests: int = 120):
    """レベル"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # IPアプリ request.remote_addr を
            ip_address = kwargs.get("ip_address", "127.0.0.1")
            
            if hasattr(wrapper, '_rate_limiter'):
                if not wrapper._rate_limiter.is_allowed(ip_address):
                    return {
                        "error": "レベル",
                        "retry_after": 60,
                        "status_code": 429
                    }
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# ?
performance_monitor = PerformanceMonitor()
cache_manager = CacheManager()
rate_limiter = RateLimiter()
query_optimizer = QueryOptimizer()

# API エラー
@monitor_performance("get_user_dashboard")
@rate_limit(120)
def get_user_dashboard(user_id: str, ip_address: str = "127.0.0.1") -> Dict[str, Any]:
    """ユーザー"""
    
    # ?
    cache_key = f"dashboard_{user_id}"
    cached_data = cache_manager.get(cache_key, "user_profile")
    
    if cached_data:
        cached_data["_cache_hit"] = True
        return cached_data
    
    # ?
    user_data = query_optimizer.optimize_user_query(user_id)
    mandala_data = query_optimizer.optimize_mandala_query(user_id)
    
    dashboard_data = {
        "user": user_data["user_profile"],
        "tasks": user_data["active_tasks"],
        "crystals": user_data["crystal_progress"],
        "mandala": mandala_data,
        "achievements": user_data["recent_achievements"],
        "timestamp": datetime.now().isoformat()
    }
    
    # ?
    cache_manager.set(cache_key, dashboard_data, "user_profile")
    
    return dashboard_data

@monitor_performance("get_performance_metrics")
def get_performance_metrics() -> Dict[str, Any]:
    """?"""
    return {
        "performance": performance_monitor.get_performance_summary(),
        "cache": cache_manager.get_cache_stats(),
        "rate_limiting": rate_limiter.get_rate_limit_stats(),
        "slow_queries": query_optimizer.get_slow_query_report(),
        "timestamp": datetime.now().isoformat()
    }

# デフォルト
get_user_dashboard._monitor = performance_monitor
get_user_dashboard._rate_limiter = rate_limiter
get_performance_metrics._monitor = performance_monitor

if __name__ == "__main__":
    print("?")
    
    # ?
    print("\n=== ? ===")
    
    # ?
    for i in range(10):
        result = get_user_dashboard(f"user_{i % 3}")
        print(f"リスト {i+1}: ? = {result.get('_cache_hit', False)}")
        time.sleep(0.1)
    
    # メイン
    print("\n=== ? ===")
    metrics = get_performance_metrics()
    print(json.dumps(metrics, indent=2, ensure_ascii=False, default=str))