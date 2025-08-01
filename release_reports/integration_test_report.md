
# 最終統合テストレポート

## 概要
- **実行日時**: 2025-07-30T12:41:47.523709
- **テスト対象**: http://localhost:8080
- **全体ステータス**: FAIL

## サマリー
- **総テスト数**: 6
- **成功**: 0
- **部分成功**: 0
- **失敗**: 2
- **エラー**: 4
- **成功率**: 0.0%

## テスト結果詳細

### 💥 SERVICE_HEALTH
**ステータス**: ERROR

**エラー**:
- Health check error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF94D14470>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))

### ❌ CORE_SERVICES
**ステータス**: FAIL

**エラー**:
- auth service error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/auth/health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF96086B40>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))
- core-game service error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/game/health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF960860F0>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))
- task-mgmt service error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/tasks/health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF960871D0>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))
- ai-story service error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/story/health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF96087950>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))
- mandala service error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/mandala/health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF960C8110>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))

**詳細**:
- **services**: N/A

### 💥 USER_JOURNEY
**ステータス**: ERROR

**エラー**:
- User journey error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/auth/register (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF960C8B30>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))

### 💥 PERFORMANCE
**ステータス**: ERROR

**エラー**:
- Performance test error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF960876B0>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))

### 💥 SECURITY
**ステータス**: ERROR

**エラー**:
- Security test error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/auth/profile (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF960873B0>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))

### ❌ THERAPEUTIC_SAFETY
**ステータス**: FAIL

**エラー**:
- Content moderation not working properly
- F1 score below target (98%)
- CBT intervention not functioning

**詳細**:
- **content_moderation**: N/A
- **f1_score**: N/A
- **cbt_intervention**: N/A

## 推奨事項

- ❌ 重要な問題が検出されました。本番リリース前に以下の問題を解決してください：
  - Health check error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF94D14470>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))
  - auth service error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/auth/health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF96086B40>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))
  - core-game service error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/game/health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF960860F0>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))
  - task-mgmt service error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/tasks/health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF960871D0>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))
  - ai-story service error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/story/health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF96087950>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))
  - mandala service error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/mandala/health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF960C8110>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))
  - User journey error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/auth/register (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF960C8B30>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))
  - Performance test error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF960876B0>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))
  - Security test error: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/auth/profile (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002CF960873B0>: Failed to establish a new connection: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。'))
  - Content moderation not working properly
  - F1 score below target (98%)
  - CBT intervention not functioning
