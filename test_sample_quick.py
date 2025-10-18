#!/usr/bin/env python3
"""サンプルデータ管理機能の簡易テスト"""

import sys
from mock_database import MockFirestoreClient

print("=== サンプルデータ管理機能テスト ===\n")

# 1. サンプルデータロードのテスト
print("1. サンプルデータロードのテスト...")
client = MockFirestoreClient(persist_data=False)
result = client.load_sample_data('test_data/sample_data.json')
if result:
    stats = client.get_stats()
    print(f"   ✓ ロード成功")
    print(f"   ✓ コレクション数: {stats['collections']}")
    print(f"   ✓ 総ドキュメント数: {stats['total_documents']}")
else:
    print("   ✗ ロード失敗")
    sys.exit(1)

# 2. テストデータ生成のテスト
print("\n2. テストデータ生成のテスト...")
client2 = MockFirestoreClient(persist_data=False)
config = {
    'users': {'count': 3, 'prefix': 'gen_user_'},
    'tasks': {'count': 5, 'users': []},
}
result = client2.generate_test_data(config)
if result:
    users = client2.collection('users').get()
    tasks = client2.collection('tasks').get()
    print(f"   ✓ 生成成功")
    print(f"   ✓ ユーザー数: {len(users)}")
    print(f"   ✓ タスク数: {len(tasks)}")
else:
    print("   ✗ 生成失敗")
    sys.exit(1)

# 3. エクスポート/インポートのテスト
print("\n3. エクスポート/インポートのテスト...")
import tempfile
import os

with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
    export_file = tmp.name

try:
    client3 = MockFirestoreClient(persist_data=False)
    client3.collection('users').document('test_001').set({'name': 'テスト'})
    
    # エクスポート
    result = client3.export_data(export_file)
    if not result:
        print("   ✗ エクスポート失敗")
        sys.exit(1)
    
    # インポート
    client4 = MockFirestoreClient(persist_data=False)
    result = client4.import_data(export_file, merge=False)
    if result:
        doc = client4.collection('users').document('test_001').get()
        if doc.exists:
            print(f"   ✓ エクスポート/インポート成功")
        else:
            print("   ✗ データが見つかりません")
            sys.exit(1)
    else:
        print("   ✗ インポート失敗")
        sys.exit(1)
finally:
    if os.path.exists(export_file):
        os.unlink(export_file)

print("\n✅ 全てのテストが成功しました！")
print("\nTask 2.2 の実装が完了:")
print("  ✓ JSONファイルからのサンプルデータロード")
print("  ✓ テストデータの生成機能")
print("  ✓ データのエクスポート/インポート機能")
