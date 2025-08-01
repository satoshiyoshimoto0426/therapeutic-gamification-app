#!/usr/bin/env python3
"""
セキュリティ監査スクリプト
包括的なセキュリティチェックとペネトレーションテストを実行
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
import socket
import ssl
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityAuditor:
    """セキュリティ監査クラス"""
    
    def __init__(self, target_url: str = "http://localhost:8080"):
        self.target_url = target_url
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "target": target_url,
            "audits": {},
            "summary": {},
            "overall_status": "UNKNOWN"
        }
    
    def run_command(self, command: List[str], timeout: int = 300) -> Tuple[bool, str, str]:
        """コマンド実行"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
    
    def audit_ssl_tls(self) -> Dict:
        """SSL/TLS設定監査"""
        logger.info("SSL/TLS設定監査開始...")
        
        audit_result = {
            "name": "ssl_tls",
            "status": "UNKNOWN",
            "findings": [],
            "recommendations": []
        }
        
        try:
            # URLからホスト名とポートを抽出
            from urllib.parse import urlparse
            parsed_url = urlparse(self.target_url)
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            if parsed_url.scheme == 'https':
                # SSL証明書チェック
                context = ssl.create_default_context()
                
                with socket.create_connection((hostname, port), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        cipher = ssock.cipher()
                        
                        audit_result["findings"].append({
                            "type": "certificate",
                            "subject": cert.get("subject"),
                            "issuer": cert.get("issuer"),
                            "not_after": cert.get("notAfter"),
                            "cipher_suite": cipher[0] if cipher else None,
                            "protocol": cipher[1] if cipher else None
                        })
                        
                        # 証明書有効期限チェック
                        from datetime import datetime
                        not_after = datetime.strptime(cert.get("notAfter"), "%b %d %H:%M:%S %Y %Z")
                        days_until_expiry = (not_after - datetime.now()).days
                        
                        if days_until_expiry < 30:
                            audit_result["findings"].append({
                                "type": "warning",
                                "message": f"SSL certificate expires in {days_until_expiry} days"
                            })
                            audit_result["recommendations"].append("SSL証明書の更新を検討してください")
                
                audit_result["status"] = "PASS"
            else:
                audit_result["findings"].append({
                    "type": "warning",
                    "message": "HTTPS not enabled"
                })
                audit_result["recommendations"].append("本番環境ではHTTPSを有効にしてください")
                audit_result["status"] = "PARTIAL"
                
        except Exception as e:
            audit_result["status"] = "ERROR"
            audit_result["findings"].append({
                "type": "error",
                "message": f"SSL/TLS audit error: {str(e)}"
            })
        
        return audit_result
    
    def audit_headers(self) -> Dict:
        """セキュリティヘッダー監査"""
        logger.info("セキュリティヘッダー監査開始...")
        
        audit_result = {
            "name": "security_headers",
            "status": "UNKNOWN",
            "findings": [],
            "recommendations": []
        }
        
        try:
            response = requests.get(self.target_url, timeout=10)
            headers = response.headers
            
            # 必須セキュリティヘッダーのチェック
            required_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": ["DENY", "SAMEORIGIN"],
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": None,  # HTTPS時のみ
                "Content-Security-Policy": None,
                "Referrer-Policy": None
            }
            
            missing_headers = []
            weak_headers = []
            
            for header, expected_value in required_headers.items():
                if header not in headers:
                    missing_headers.append(header)
                else:
                    header_value = headers[header]
                    if expected_value:
                        if isinstance(expected_value, list):
                            if header_value not in expected_value:
                                weak_headers.append(f"{header}: {header_value}")
                        elif header_value != expected_value:
                            weak_headers.append(f"{header}: {header_value}")
                    
                    audit_result["findings"].append({
                        "type": "header",
                        "name": header,
                        "value": header_value,
                        "status": "present"
                    })
            
            # 結果評価
            if not missing_headers and not weak_headers:
                audit_result["status"] = "PASS"
            elif len(missing_headers) <= 2:  # 2個以下の不足
                audit_result["status"] = "PARTIAL"
                for header in missing_headers:
                    audit_result["recommendations"].append(f"Add {header} header")
            else:
                audit_result["status"] = "FAIL"
                audit_result["recommendations"].append("Implement comprehensive security headers")
            
            if missing_headers:
                audit_result["findings"].append({
                    "type": "missing",
                    "headers": missing_headers
                })
            
            if weak_headers:
                audit_result["findings"].append({
                    "type": "weak",
                    "headers": weak_headers
                })
                
        except Exception as e:
            audit_result["status"] = "ERROR"
            audit_result["findings"].append({
                "type": "error",
                "message": f"Header audit error: {str(e)}"
            })
        
        return audit_result
    
    def audit_authentication(self) -> Dict:
        """認証システム監査"""
        logger.info("認証システム監査開始...")
        
        audit_result = {
            "name": "authentication",
            "status": "UNKNOWN",
            "findings": [],
            "recommendations": []
        }
        
        try:
            # 1. 弱いパスワードテスト
            weak_passwords = ["password", "123456", "admin", "test", ""]
            
            for password in weak_passwords:
                try:
                    response = requests.post(
                        f"{self.target_url}/api/auth/register",
                        json={
                            "username": f"test_{int(time.time())}",
                            "email": f"test_{int(time.time())}@example.com",
                            "password": password
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 201:
                        audit_result["findings"].append({
                            "type": "vulnerability",
                            "message": f"Weak password accepted: {password}",
                            "severity": "high"
                        })
                        audit_result["recommendations"].append("Implement strong password policy")
                        
                except Exception:
                    pass  # 接続エラーは無視
            
            # 2. ブルートフォース攻撃テスト
            brute_force_attempts = []
            for i in range(10):
                try:
                    start_time = time.time()
                    response = requests.post(
                        f"{self.target_url}/api/auth/login",
                        json={"username": "nonexistent", "password": f"wrong{i}"},
                        timeout=5
                    )
                    end_time = time.time()
                    
                    brute_force_attempts.append({
                        "attempt": i + 1,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time
                    })
                    
                    if response.status_code == 429:  # Rate limited
                        break
                        
                except Exception:
                    break
            
            # レート制限の確認
            rate_limited = any(attempt["status_code"] == 429 for attempt in brute_force_attempts)
            
            if rate_limited:
                audit_result["findings"].append({
                    "type": "protection",
                    "message": "Rate limiting detected for login attempts",
                    "severity": "good"
                })
            else:
                audit_result["findings"].append({
                    "type": "vulnerability",
                    "message": "No rate limiting detected for login attempts",
                    "severity": "medium"
                })
                audit_result["recommendations"].append("Implement rate limiting for authentication")
            
            # 3. JWT トークンテスト（もし使用している場合）
            try:
                # 無効なトークンでのアクセス試行
                invalid_tokens = [
                    "invalid.token.here",
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
                    ""
                ]
                
                for token in invalid_tokens:
                    response = requests.get(
                        f"{self.target_url}/api/auth/profile",
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=10
                    )
                    
                    if response.status_code not in [401, 403]:
                        audit_result["findings"].append({
                            "type": "vulnerability",
                            "message": f"Invalid token accepted: {token[:20]}...",
                            "severity": "high"
                        })
                        
            except Exception:
                pass
            
            # 結果評価
            vulnerabilities = [f for f in audit_result["findings"] if f.get("type") == "vulnerability"]
            protections = [f for f in audit_result["findings"] if f.get("type") == "protection"]
            
            if not vulnerabilities and protections:
                audit_result["status"] = "PASS"
            elif len(vulnerabilities) <= 1:
                audit_result["status"] = "PARTIAL"
            else:
                audit_result["status"] = "FAIL"
                
        except Exception as e:
            audit_result["status"] = "ERROR"
            audit_result["findings"].append({
                "type": "error",
                "message": f"Authentication audit error: {str(e)}"
            })
        
        return audit_result    

    def audit_input_validation(self) -> Dict:
        """入力検証監査"""
        logger.info("入力検証監査開始...")
        
        audit_result = {
            "name": "input_validation",
            "status": "UNKNOWN",
            "findings": [],
            "recommendations": []
        }
        
        try:
            # 1. SQLインジェクションテスト
            sql_payloads = [
                "'; DROP TABLE users; --",
                "' OR '1'='1' --",
                "admin'/*",
                "' UNION SELECT * FROM users --",
                "1' AND (SELECT COUNT(*) FROM users) > 0 --"
            ]
            
            sql_vulnerabilities = []
            for payload in sql_payloads:
                try:
                    response = requests.post(
                        f"{self.target_url}/api/auth/login",
                        json={"username": payload, "password": "test"},
                        timeout=10
                    )
                    
                    # 500エラーやデータベースエラーメッセージの検出
                    if response.status_code == 500:
                        sql_vulnerabilities.append(payload)
                    elif "sql" in response.text.lower() or "database" in response.text.lower():
                        sql_vulnerabilities.append(payload)
                        
                except Exception:
                    pass
            
            if sql_vulnerabilities:
                audit_result["findings"].append({
                    "type": "vulnerability",
                    "message": f"Potential SQL injection vulnerabilities: {len(sql_vulnerabilities)}",
                    "payloads": sql_vulnerabilities,
                    "severity": "critical"
                })
                audit_result["recommendations"].append("Implement parameterized queries and input sanitization")
            
            # 2. XSSテスト
            xss_payloads = [
                "<script>alert('xss')</script>",
                "javascript:alert('xss')",
                "<img src=x onerror=alert('xss')>",
                "';alert('xss');//",
                "<svg onload=alert('xss')>"
            ]
            
            xss_vulnerabilities = []
            for payload in xss_payloads:
                try:
                    # タスク作成でXSSテスト
                    response = requests.post(
                        f"{self.target_url}/api/tasks/create",
                        json={
                            "title": payload,
                            "description": "test",
                            "task_type": "routine",
                            "difficulty": 1
                        },
                        timeout=10
                    )
                    
                    # レスポンスにスクリプトタグが含まれているかチェック
                    if payload in response.text and response.status_code == 201:
                        xss_vulnerabilities.append(payload)
                        
                except Exception:
                    pass
            
            if xss_vulnerabilities:
                audit_result["findings"].append({
                    "type": "vulnerability",
                    "message": f"Potential XSS vulnerabilities: {len(xss_vulnerabilities)}",
                    "payloads": xss_vulnerabilities,
                    "severity": "high"
                })
                audit_result["recommendations"].append("Implement output encoding and CSP headers")
            
            # 3. コマンドインジェクションテスト
            command_payloads = [
                "; ls -la",
                "| whoami",
                "&& cat /etc/passwd",
                "`id`",
                "$(whoami)"
            ]
            
            command_vulnerabilities = []
            for payload in command_payloads:
                try:
                    response = requests.post(
                        f"{self.target_url}/api/tasks/create",
                        json={
                            "title": f"test{payload}",
                            "description": "test",
                            "task_type": "routine",
                            "difficulty": 1
                        },
                        timeout=10
                    )
                    
                    # システムコマンドの出力が含まれているかチェック
                    if any(keyword in response.text.lower() for keyword in ["root:", "bin/", "uid=", "gid="]):
                        command_vulnerabilities.append(payload)
                        
                except Exception:
                    pass
            
            if command_vulnerabilities:
                audit_result["findings"].append({
                    "type": "vulnerability",
                    "message": f"Potential command injection vulnerabilities: {len(command_vulnerabilities)}",
                    "payloads": command_vulnerabilities,
                    "severity": "critical"
                })
                audit_result["recommendations"].append("Avoid system command execution with user input")
            
            # 4. パストラバーサルテスト
            path_payloads = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
                "....//....//....//etc/passwd",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
            ]
            
            path_vulnerabilities = []
            for payload in path_payloads:
                try:
                    response = requests.get(
                        f"{self.target_url}/api/files/{payload}",
                        timeout=10
                    )
                    
                    if response.status_code == 200 and ("root:" in response.text or "localhost" in response.text):
                        path_vulnerabilities.append(payload)
                        
                except Exception:
                    pass
            
            if path_vulnerabilities:
                audit_result["findings"].append({
                    "type": "vulnerability",
                    "message": f"Potential path traversal vulnerabilities: {len(path_vulnerabilities)}",
                    "payloads": path_vulnerabilities,
                    "severity": "high"
                })
                audit_result["recommendations"].append("Implement proper file path validation")
            
            # 結果評価
            total_vulnerabilities = len(sql_vulnerabilities) + len(xss_vulnerabilities) + len(command_vulnerabilities) + len(path_vulnerabilities)
            
            if total_vulnerabilities == 0:
                audit_result["status"] = "PASS"
            elif total_vulnerabilities <= 2:
                audit_result["status"] = "PARTIAL"
            else:
                audit_result["status"] = "FAIL"
                
        except Exception as e:
            audit_result["status"] = "ERROR"
            audit_result["findings"].append({
                "type": "error",
                "message": f"Input validation audit error: {str(e)}"
            })
        
        return audit_result
    
    def audit_dependencies(self) -> Dict:
        """依存関係脆弱性監査"""
        logger.info("依存関係脆弱性監査開始...")
        
        audit_result = {
            "name": "dependencies",
            "status": "UNKNOWN",
            "findings": [],
            "recommendations": []
        }
        
        try:
            # Python依存関係のセキュリティチェック
            success, stdout, stderr = self.run_command(["pip", "list", "--format=json"])
            
            if success:
                packages = json.loads(stdout)
                audit_result["findings"].append({
                    "type": "info",
                    "message": f"Found {len(packages)} Python packages"
                })
                
                # safety チェック（もしインストールされている場合）
                success, stdout, stderr = self.run_command(["safety", "check", "--json"], timeout=60)
                
                if success:
                    try:
                        safety_results = json.loads(stdout)
                        vulnerabilities = len(safety_results)
                        
                        if vulnerabilities == 0:
                            audit_result["findings"].append({
                                "type": "protection",
                                "message": "No known vulnerabilities in Python dependencies",
                                "severity": "good"
                            })
                        else:
                            audit_result["findings"].append({
                                "type": "vulnerability",
                                "message": f"Found {vulnerabilities} vulnerabilities in Python dependencies",
                                "details": safety_results,
                                "severity": "high"
                            })
                            audit_result["recommendations"].append("Update vulnerable Python packages")
                            
                    except json.JSONDecodeError:
                        audit_result["findings"].append({
                            "type": "info",
                            "message": "Safety check completed but output format unexpected"
                        })
                else:
                    audit_result["findings"].append({
                        "type": "warning",
                        "message": "Could not run safety check for Python dependencies"
                    })
            
            # Node.js依存関係のセキュリティチェック（フロントエンドがある場合）
            if Path("frontend/package.json").exists():
                success, stdout, stderr = self.run_command(["npm", "audit", "--json"], timeout=60)
                
                if success:
                    try:
                        npm_audit = json.loads(stdout)
                        vulnerabilities = npm_audit.get("metadata", {}).get("vulnerabilities", {})
                        total_vulns = sum(vulnerabilities.values()) if vulnerabilities else 0
                        
                        if total_vulns == 0:
                            audit_result["findings"].append({
                                "type": "protection",
                                "message": "No known vulnerabilities in Node.js dependencies",
                                "severity": "good"
                            })
                        else:
                            audit_result["findings"].append({
                                "type": "vulnerability",
                                "message": f"Found {total_vulns} vulnerabilities in Node.js dependencies",
                                "details": vulnerabilities,
                                "severity": "medium"
                            })
                            audit_result["recommendations"].append("Update vulnerable Node.js packages")
                            
                    except json.JSONDecodeError:
                        audit_result["findings"].append({
                            "type": "warning",
                            "message": "npm audit completed but output format unexpected"
                        })
            
            # 結果評価
            vulnerabilities = [f for f in audit_result["findings"] if f.get("type") == "vulnerability"]
            
            if not vulnerabilities:
                audit_result["status"] = "PASS"
            elif len(vulnerabilities) == 1:
                audit_result["status"] = "PARTIAL"
            else:
                audit_result["status"] = "FAIL"
                
        except Exception as e:
            audit_result["status"] = "ERROR"
            audit_result["findings"].append({
                "type": "error",
                "message": f"Dependencies audit error: {str(e)}"
            })
        
        return audit_result
    
    def audit_configuration(self) -> Dict:
        """設定セキュリティ監査"""
        logger.info("設定セキュリティ監査開始...")
        
        audit_result = {
            "name": "configuration",
            "status": "UNKNOWN",
            "findings": [],
            "recommendations": []
        }
        
        try:
            # 1. デバッグモードチェック
            try:
                response = requests.get(f"{self.target_url}/debug", timeout=10)
                if response.status_code == 200:
                    audit_result["findings"].append({
                        "type": "vulnerability",
                        "message": "Debug endpoint accessible",
                        "severity": "high"
                    })
                    audit_result["recommendations"].append("Disable debug mode in production")
            except Exception:
                pass
            
            # 2. 管理者インターフェースチェック
            admin_paths = ["/admin", "/admin/", "/administrator", "/manage", "/management"]
            
            for path in admin_paths:
                try:
                    response = requests.get(f"{self.target_url}{path}", timeout=10)
                    if response.status_code == 200:
                        audit_result["findings"].append({
                            "type": "warning",
                            "message": f"Admin interface accessible at {path}",
                            "severity": "medium"
                        })
                        audit_result["recommendations"].append("Secure admin interfaces with proper authentication")
                except Exception:
                    pass
            
            # 3. 情報漏洩チェック
            info_paths = ["/info", "/.env", "/config", "/version", "/status"]
            
            for path in info_paths:
                try:
                    response = requests.get(f"{self.target_url}{path}", timeout=10)
                    if response.status_code == 200 and len(response.text) > 10:
                        audit_result["findings"].append({
                            "type": "warning",
                            "message": f"Information disclosure at {path}",
                            "severity": "low"
                        })
                except Exception:
                    pass
            
            # 4. HTTPメソッドチェック
            dangerous_methods = ["PUT", "DELETE", "PATCH", "TRACE", "OPTIONS"]
            
            for method in dangerous_methods:
                try:
                    response = requests.request(method, self.target_url, timeout=10)
                    if response.status_code not in [405, 501]:  # Method Not Allowed
                        audit_result["findings"].append({
                            "type": "warning",
                            "message": f"HTTP {method} method allowed",
                            "severity": "low"
                        })
                except Exception:
                    pass
            
            # 結果評価
            vulnerabilities = [f for f in audit_result["findings"] if f.get("severity") in ["high", "critical"]]
            warnings = [f for f in audit_result["findings"] if f.get("severity") in ["medium", "low"]]
            
            if not vulnerabilities and len(warnings) <= 2:
                audit_result["status"] = "PASS"
            elif not vulnerabilities:
                audit_result["status"] = "PARTIAL"
            else:
                audit_result["status"] = "FAIL"
                
        except Exception as e:
            audit_result["status"] = "ERROR"
            audit_result["findings"].append({
                "type": "error",
                "message": f"Configuration audit error: {str(e)}"
            })
        
        return audit_result    

    def run_all_audits(self) -> Dict:
        """全セキュリティ監査の実行"""
        logger.info("セキュリティ監査開始...")
        
        # 各監査を実行
        audits = [
            self.audit_ssl_tls(),
            self.audit_headers(),
            self.audit_authentication(),
            self.audit_input_validation(),
            self.audit_dependencies(),
            self.audit_configuration()
        ]
        
        # 結果をまとめる
        for audit in audits:
            self.audit_results["audits"][audit["name"]] = audit
        
        # サマリー作成
        self.create_summary()
        
        return self.audit_results
    
    def create_summary(self):
        """監査結果サマリー作成"""
        total_audits = len(self.audit_results["audits"])
        passed_audits = sum(1 for a in self.audit_results["audits"].values() if a.get("status") == "PASS")
        partial_audits = sum(1 for a in self.audit_results["audits"].values() if a.get("status") == "PARTIAL")
        failed_audits = sum(1 for a in self.audit_results["audits"].values() if a.get("status") == "FAIL")
        error_audits = sum(1 for a in self.audit_results["audits"].values() if a.get("status") == "ERROR")
        
        # 脆弱性の重要度別集計
        critical_vulns = 0
        high_vulns = 0
        medium_vulns = 0
        low_vulns = 0
        
        for audit in self.audit_results["audits"].values():
            for finding in audit.get("findings", []):
                severity = finding.get("severity", "").lower()
                if severity == "critical":
                    critical_vulns += 1
                elif severity == "high":
                    high_vulns += 1
                elif severity == "medium":
                    medium_vulns += 1
                elif severity == "low":
                    low_vulns += 1
        
        self.audit_results["summary"] = {
            "total_audits": total_audits,
            "passed_audits": passed_audits,
            "partial_audits": partial_audits,
            "failed_audits": failed_audits,
            "error_audits": error_audits,
            "success_rate": passed_audits / total_audits if total_audits > 0 else 0,
            "vulnerabilities": {
                "critical": critical_vulns,
                "high": high_vulns,
                "medium": medium_vulns,
                "low": low_vulns,
                "total": critical_vulns + high_vulns + medium_vulns + low_vulns
            }
        }
        
        # 全体ステータス決定
        if critical_vulns > 0:
            self.audit_results["overall_status"] = "CRITICAL"
        elif failed_audits > 0 or high_vulns > 0:
            self.audit_results["overall_status"] = "FAIL"
        elif partial_audits > 0 or medium_vulns > 0:
            self.audit_results["overall_status"] = "PARTIAL"
        else:
            self.audit_results["overall_status"] = "PASS"
    
    def generate_report(self) -> str:
        """セキュリティ監査レポート生成"""
        report = f"""
# セキュリティ監査レポート

## 概要
- **監査日時**: {self.audit_results['timestamp']}
- **監査対象**: {self.audit_results['target']}
- **全体ステータス**: {self.audit_results['overall_status']}

## サマリー
- **総監査項目**: {self.audit_results['summary']['total_audits']}
- **成功**: {self.audit_results['summary']['passed_audits']}
- **部分成功**: {self.audit_results['summary']['partial_audits']}
- **失敗**: {self.audit_results['summary']['failed_audits']}
- **エラー**: {self.audit_results['summary']['error_audits']}
- **成功率**: {self.audit_results['summary']['success_rate']:.1%}

## 脆弱性サマリー
- **Critical**: {self.audit_results['summary']['vulnerabilities']['critical']}
- **High**: {self.audit_results['summary']['vulnerabilities']['high']}
- **Medium**: {self.audit_results['summary']['vulnerabilities']['medium']}
- **Low**: {self.audit_results['summary']['vulnerabilities']['low']}
- **Total**: {self.audit_results['summary']['vulnerabilities']['total']}

## 監査結果詳細

"""
        
        for audit_name, audit_result in self.audit_results["audits"].items():
            status_icon = {
                "PASS": "✅",
                "PARTIAL": "⚠️",
                "FAIL": "❌",
                "ERROR": "💥",
                "UNKNOWN": "❓"
            }.get(audit_result.get("status", "UNKNOWN"), "❓")
            
            report += f"### {status_icon} {audit_result.get('name', audit_name).upper()}\n"
            report += f"**ステータス**: {audit_result.get('status', 'UNKNOWN')}\n\n"
            
            # 発見事項
            if audit_result.get("findings"):
                report += "**発見事項**:\n"
                for finding in audit_result["findings"]:
                    severity = finding.get("severity", "")
                    severity_icon = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                        "good": "✅"
                    }.get(severity.lower(), "")
                    
                    report += f"- {severity_icon} {finding.get('message', 'N/A')}"
                    if severity:
                        report += f" ({severity.upper()})"
                    report += "\n"
                report += "\n"
            
            # 推奨事項
            if audit_result.get("recommendations"):
                report += "**推奨事項**:\n"
                for recommendation in audit_result["recommendations"]:
                    report += f"- {recommendation}\n"
                report += "\n"
        
        # 全体的な推奨事項
        report += "## 全体的な推奨事項\n\n"
        
        if self.audit_results["overall_status"] == "PASS":
            report += "- ✅ セキュリティ監査に合格しました。定期的な監査を継続してください。\n"
        elif self.audit_results["overall_status"] == "PARTIAL":
            report += "- ⚠️ いくつかの改善点が見つかりました。以下の対応を検討してください：\n"
            report += "  - セキュリティヘッダーの追加・強化\n"
            report += "  - 設定の見直し\n"
            report += "  - 依存関係の更新\n"
        elif self.audit_results["overall_status"] == "FAIL":
            report += "- ❌ 重要なセキュリティ問題が検出されました。本番リリース前に以下を対応してください：\n"
            report += "  - 高リスク脆弱性の修正\n"
            report += "  - 認証・認可システムの強化\n"
            report += "  - 入力検証の実装\n"
        else:  # CRITICAL
            report += "- 🚨 **緊急**: クリティカルな脆弱性が検出されました。即座に対応が必要です：\n"
            report += "  - システムの一時停止を検討\n"
            report += "  - セキュリティ専門家への相談\n"
            report += "  - 全面的なセキュリティ見直し\n"
        
        report += "\n## 次のステップ\n\n"
        report += "1. 高リスク脆弱性の優先修正\n"
        report += "2. セキュリティ設定の強化\n"
        report += "3. 定期的なセキュリティ監査の実施\n"
        report += "4. セキュリティ意識向上のための教育\n"
        
        return report

def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="セキュリティ監査実行")
    parser.add_argument("--target", default="http://localhost:8080", help="監査対象URL")
    parser.add_argument("--output", help="レポート出力ファイル")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="出力形式")
    
    args = parser.parse_args()
    
    try:
        # セキュリティ監査実行
        auditor = SecurityAuditor(args.target)
        results = auditor.run_all_audits()
        
        # 結果出力
        if args.format == "json":
            output_content = json.dumps(results, indent=2, ensure_ascii=False)
        else:
            output_content = auditor.generate_report()
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_content)
            logger.info(f"レポート出力: {args.output}")
        else:
            print(output_content)
        
        # 終了コード決定
        if results["overall_status"] == "PASS":
            sys.exit(0)
        elif results["overall_status"] == "PARTIAL":
            sys.exit(1)
        elif results["overall_status"] == "FAIL":
            sys.exit(2)
        else:  # CRITICAL
            sys.exit(3)
            
    except Exception as e:
        logger.error(f"セキュリティ監査エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()