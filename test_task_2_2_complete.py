#!/usr/bin/env python3
"""
Task 2.2: サンプルデータ管理機能の完全テスト

要件 2.3 の検証:
- JSONファイルからのサンプルデータロード
- テストデータの生成機能
- データのエクスポート/インポート機能
"""

import json
import os
import sys
import tempfile
import shutil
from mock_database import MockFirestoreClient


def test_all_features():
    """全機能を統合テスト"""
    print("=" * 70)
    print("Task 2.2: サンプルデータ管理機能の完全テスト")
    print("=" * 70)
    
    all_passed = True
    
    # テスト1: サンプルデータロード
    print("\n[テスト 1/7] サンプルデータロード")
    print("-" * 70)
    try:
        client = MockFirestoreClient(persist_data=False)
        result = client.load_sample_data('test_data/sample_data.json')
        assert result, "サンプルデータのロードに失敗"
        
        stats = client.get_stats()
        assert stats['collections'] > 0, "コレクションがロードされていません"
        assert stats['total_documents'] > 0, "ドキュメントがロードされていません"
        
        print(f"  ✓ コレクション数: {stats['collections']}")
        print(f"  ✓ 総ドキュメント数: {stats['total_documents']}")
        print(f"  ✓ コレクション詳細: {stats['collections_detail']}")
        print("  ✅ 成功")
    except Exception as e:
        print(f"  ❌ 失敗: {e}")
        all_passed = False
    
    # テスト2: テストデータ生成
    print("\n[テスト 2/7] テストデータ生成")
    print("-" * 70)
    try:
        client = MockFirestoreClient(persist_data=False)
        config = {
            'users': {'count': 5, 'prefix': 'gen_user_'},
            'tasks': {'count': 15, 'users': []},
            'mood_entries': {'count': 10, 'users': []},
            'mandala_grids': {'count': 3, 'users': []}
        }
        result = client.generate_test_data(config)
        assert result, "テストデータの生成に失敗"
        
        users = client.collection('users').get()
        tasks = client.collection('tasks').get()
        mood_entries = client.collection('mood_entries').get()
        mandala_grids = client.collection('mandala_grids').get()
        
        assert len(users) == 5, f"ユーザー数が不正: {len(users)}"
        assert len(tasks) == 15, f"タスク数が不正: {len(tasks)}"
        assert len(mood_entries) == 10, f"ムードエントリー数が不正: {len(mood_entries)}"
        assert len(mandala_grids) == 3, f"マンダラグリッド数が不正: {len(mandala_grids)}"
        
        print(f"  ✓ ユーザー: {len(users)}件")
        print(f"  ✓ タスク: {len(tasks)}件")
        print(f"  ✓ ムードエントリー: {len(mood_entries)}件")
        print(f"  ✓ マンダラグリッド: {len(mandala_grids)}件")
        print("  ✅ 成功")
    except Exception as e:
        print(f"  ❌ 失敗: {e}")
        all_passed = False
    
    # テスト3: データエクスポート/インポート
    print("\n[テスト 3/7] データエクスポート/インポート")
    print("-" * 70)
    export_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            export_file = tmp.name
        
        # エクスポート
        client1 = MockFirestoreClient(persist_data=False)
        client1.collection('users').document('export_test').set({
            'username': 'エクスポートテスト',
            'email': 'export@test.com'
        })
        result = client1.export_data(export_file)
        assert result, "エクスポートに失敗"
        assert os.path.exists(export_file), "エクスポートファイルが作成されていません"
        print(f"  ✓ エクスポート成功: {export_file}")
        
        # インポート
        client2 = MockFirestoreClient(persist_data=False)
        result = client2.import_data(export_file, merge=False)
        assert result, "インポートに失敗"
        
        doc = client2.collection('users').document('export_test').get()
        assert doc.exists, "インポートされたドキュメントが見つかりません"
        assert doc.to_dict()['username'] == 'エクスポートテスト'
        print(f"  ✓ インポート成功")
        print("  ✅ 成功")
    except Exception as e:
        print(f"  ❌ 失敗: {e}")
        all_passed = False
    finally:
        if export_file and os.path.exists(export_file):
            os.unlink(export_file)
    
    # テスト4: バックアップ/復元
    print("\n[テスト 4/7] バックアップ/復元")
    print("-" * 70)
    backup_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            backup_file = tmp.name
        
        client = MockFirestoreClient(persist_data=False)
        client.collection('users').document('backup_test').set({
            'username': 'バックアップテスト'
        })
        
        # バックアップ
        result = client.backup_data(backup_file)
        assert result, "バックアップに失敗"
        print(f"  ✓ バックアップ成功: {backup_file}")
        
        # データクリア
        client.clear_all_data()
        stats = client.get_stats()
        assert stats['total_documents'] == 0, "データがクリアされていません"
        print(f"  ✓ データクリア成功")
        
        # 復元
        result = client.restore_data(backup_file)
        assert result, "復元に失敗"
        
        doc = client.collection('users').document('backup_test').get()
        assert doc.exists, "復元されたドキュメントが見つかりません"
        print(f"  ✓ 復元成功")
        print("  ✅ 成功")
    except Exception as e:
        print(f"  ❌ 失敗: {e}")
        all_passed = False
    finally:
        if backup_file and os.path.exists(backup_file):
            os.unlink(backup_file)
    
    # テスト5: シードデータ
    print("\n[テスト 5/7] シードデータ")
    print("-" * 70)
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        users_file = os.path.join(temp_dir, 'users.json')
        tasks_file = os.path.join(temp_dir, 'tasks.json')
        
        # シードファイル作成
        users_data = [
            {'_id': 'seed_001', 'username': 'シードユーザー1'},
            {'_id': 'seed_002', 'username': 'シードユーザー2'}
        ]
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False)
        
        tasks_data = [
            {'_id': 'task_001', 'title': 'シードタスク1'},
            {'_id': 'task_002', 'title': 'シードタスク2'}
        ]
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, ensure_ascii=False)
        
        # シードデータロード
        client = MockFirestoreClient(persist_data=False)
        seed_config = {
            'users': users_file,
            'tasks': tasks_file
        }
        result = client.seed_data(seed_config)
        assert result, "シードデータのロードに失敗"
        
        users = client.collection('users').get()
        tasks = client.collection('tasks').get()
        assert len(users) == 2, f"ユーザー数が不正: {len(users)}"
        assert len(tasks) == 2, f"タスク数が不正: {len(tasks)}"
        
        print(f"  ✓ シードユーザー: {len(users)}件")
        print(f"  ✓ シードタスク: {len(tasks)}件")
        print("  ✅ 成功")
    except Exception as e:
        print(f"  ❌ 失敗: {e}")
        all_passed = False
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    # テスト6: コレクションクリア
    print("\n[テスト 6/7] コレクションクリア")
    print("-" * 70)
    try:
        client = MockFirestoreClient(persist_data=False)
        client.collection('users').document('user_001').set({'username': 'ユーザー1'})
        client.collection('users').document('user_002').set({'username': 'ユーザー2'})
        client.collection('tasks').document('task_001').set({'title': 'タスク1'})
        
        # usersコレクションをクリア
        result = client.clear_collection('users')
        assert result, "コレクションクリアに失敗"
        
        users = client.collection('users').get()
        tasks = client.collection('tasks').get()
        assert len(users) == 0, "usersコレクションがクリアされていません"
        assert len(tasks) == 1, "tasksコレクションが影響を受けています"
        
        print(f"  ✓ usersコレクションクリア成功")
        print(f"  ✓ tasksコレクションは保持: {len(tasks)}件")
        print("  ✅ 成功")
    except Exception as e:
        print(f"  ❌ 失敗: {e}")
        all_passed = False
    
    # テスト7: データマージ
    print("\n[テスト 7/7] データマージ")
    print("-" * 70)
    merge_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            merge_file = tmp.name
        
        client = MockFirestoreClient(persist_data=False)
        client.collection('users').document('user_001').set({
            'username': '既存ユーザー'
        })
        
        # マージ用データ作成
        merge_data = {
            'users': {
                'user_002': {'username': '新規ユーザー'}
            },
            'tasks': {
                'task_001': {'title': '新規タスク'}
            }
        }
        with open(merge_file, 'w', encoding='utf-8') as f:
            json.dump(merge_data, f, ensure_ascii=False)
        
        # マージ
        result = client.import_data(merge_file, merge=True)
        assert result, "マージに失敗"
        
        users = client.collection('users').get()
        tasks = client.collection('tasks').get()
        assert len(users) == 2, f"ユーザー数が不正: {len(users)}"
        assert len(tasks) == 1, f"タスク数が不正: {len(tasks)}"
        
        # 既存データが保持されていることを確認
        user1 = client.collection('users').document('user_001').get()
        assert user1.exists and user1.to_dict()['username'] == '既存ユーザー'
        
        print(f"  ✓ 既存データ保持: {len(users)}件")
        print(f"  ✓ 新規データ追加: {len(tasks)}件")
        print("  ✅ 成功")
    except Exception as e:
        print(f"  ❌ 失敗: {e}")
        all_passed = False
    finally:
        if merge_file and os.path.exists(merge_file):
            os.unlink(merge_file)
    
    # 結果サマリー
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 全てのテストが成功しました！")
        print("=" * 70)
        print("\nTask 2.2 の実装が完了しました:")
        print("  ✓ JSONファイルからのサンプルデータロード (load_sample_data)")
        print("  ✓ テストデータの生成機能 (generate_test_data)")
        print("  ✓ データのエクスポート/インポート機能 (export_data/import_data)")
        print("  ✓ バックアップ/復元機能 (backup_data/restore_data)")
        print("  ✓ シードデータ機能 (seed_data)")
        print("  ✓ コレクションクリア機能 (clear_collection)")
        print("  ✓ データマージ機能 (import with merge=True)")
        print("\n要件 2.3 を満たしています ✅")
        return True
    else:
        print("❌ 一部のテストが失敗しました")
        print("=" * 70)
        return False


if __name__ == '__main__':
    success = test_all_features()
    sys.exit(0 if success else 1)
