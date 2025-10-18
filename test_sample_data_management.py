#!/usr/bin/env python3
"""
サンプルデータ管理機能のテスト

Task 2.2の実装を検証します。
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from mock_database import MockFirestoreClient, get_mock_firestore, reset_mock_firestore


def test_load_sample_data():
    """サンプルデータのロード機能をテスト"""
    print("\n=== サンプルデータロードのテスト ===")
    
    # モックFirestoreクライアントを作成
    client = MockFirestoreClient(persist_data=False)
    
    # サンプルデータをロード
    result = client.load_sample_data('test_data/sample_data.json')
    assert result, "サンプルデータのロードに失敗しました"
    
    # データが正しくロードされたか確認
    stats = client.get_stats()
    print(f"✓ ロードされたコレクション数: {stats['collections']}")
    print(f"✓ 総ドキュメント数: {stats['total_documents']}")
    print(f"✓ コレクション詳細: {stats['collections_detail']}")
    
    # 特定のコレクションを確認
    users = client.collection('users').get()
    assert len(users) > 0, "ユーザーデータがロードされていません"
    print(f"✓ ユーザー数: {len(users)}")
    
    tasks = client.collection('tasks').get()
    assert len(tasks) > 0, "タスクデータがロードされていません"
    print(f"✓ タスク数: {len(tasks)}")
    
    print("✅ サンプルデータロードテスト成功")
    return True


def test_generate_test_data():
    """テストデータ生成機能をテスト"""
    print("\n=== テストデータ生成のテスト ===")
    
    # モックFirestoreクライアントを作成
    client = MockFirestoreClient(persist_data=False)
    
    # テストデータ生成設定
    config = {
        'users': {
            'count': 5,
            'prefix': 'gen_user_'
        },
        'tasks': {
            'count': 15,
            'users': []  # 自動的に生成されたユーザーを使用
        },
        'mood_entries': {
            'count': 10,
            'users': []
        },
        'mandala_grids': {
            'count': 3,
            'users': []
        }
    }
    
    # テストデータを生成
    result = client.generate_test_data(config)
    assert result, "テストデータの生成に失敗しました"
    
    # 生成されたデータを確認
    stats = client.get_stats()
    print(f"✓ 生成されたコレクション数: {stats['collections']}")
    print(f"✓ 総ドキュメント数: {stats['total_documents']}")
    print(f"✓ コレクション詳細: {stats['collections_detail']}")
    
    # 各コレクションのドキュメント数を確認
    users = client.collection('users').get()
    assert len(users) == 5, f"ユーザー数が期待値と異なります: {len(users)} != 5"
    print(f"✓ 生成されたユーザー数: {len(users)}")
    
    tasks = client.collection('tasks').get()
    assert len(tasks) == 15, f"タスク数が期待値と異なります: {len(tasks)} != 15"
    print(f"✓ 生成されたタスク数: {len(tasks)}")
    
    mood_entries = client.collection('mood_entries').get()
    assert len(mood_entries) == 10, f"ムードエントリー数が期待値と異なります: {len(mood_entries)} != 10"
    print(f"✓ 生成されたムードエントリー数: {len(mood_entries)}")
    
    mandala_grids = client.collection('mandala_grids').get()
    assert len(mandala_grids) == 3, f"マンダラグリッド数が期待値と異なります: {len(mandala_grids)} != 3"
    print(f"✓ 生成されたマンダラグリッド数: {len(mandala_grids)}")
    
    print("✅ テストデータ生成テスト成功")
    return True


def test_export_import_data():
    """データのエクスポート/インポート機能をテスト"""
    print("\n=== データエクスポート/インポートのテスト ===")
    
    # 一時ファイルを使用
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        export_file = tmp_file.name
    
    try:
        # モックFirestoreクライアントを作成してデータを追加
        client1 = MockFirestoreClient(persist_data=False)
        
        # テストデータを追加
        client1.collection('users').document('user_001').set({
            'username': 'エクスポートテストユーザー',
            'email': 'export@example.com'
        })
        client1.collection('tasks').document('task_001').set({
            'uid': 'user_001',
            'title': 'エクスポートテストタスク'
        })
        
        # データをエクスポート
        result = client1.export_data(export_file)
        assert result, "データのエクスポートに失敗しました"
        print(f"✓ データをエクスポートしました: {export_file}")
        
        # エクスポートファイルが存在することを確認
        assert os.path.exists(export_file), "エクスポートファイルが作成されていません"
        
        # 新しいクライアントを作成してインポート
        client2 = MockFirestoreClient(persist_data=False)
        result = client2.import_data(export_file, merge=False)
        assert result, "データのインポートに失敗しました"
        print(f"✓ データをインポートしました")
        
        # インポートされたデータを確認
        user_doc = client2.collection('users').document('user_001').get()
        assert user_doc.exists, "ユーザードキュメントがインポートされていません"
        assert user_doc.to_dict()['username'] == 'エクスポートテストユーザー'
        print(f"✓ ユーザーデータが正しくインポートされました")
        
        task_doc = client2.collection('tasks').document('task_001').get()
        assert task_doc.exists, "タスクドキュメントがインポートされていません"
        assert task_doc.to_dict()['title'] == 'エクスポートテストタスク'
        print(f"✓ タスクデータが正しくインポートされました")
        
        print("✅ データエクスポート/インポートテスト成功")
        return True
        
    finally:
        # 一時ファイルを削除
        if os.path.exists(export_file):
            os.unlink(export_file)


def test_backup_restore_data():
    """データのバックアップ/復元機能をテスト"""
    print("\n=== データバックアップ/復元のテスト ===")
    
    # 一時ファイルを使用
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        backup_file = tmp_file.name
    
    try:
        # モックFirestoreクライアントを作成してデータを追加
        client1 = MockFirestoreClient(persist_data=False)
        
        # テストデータを追加
        client1.collection('users').document('user_backup').set({
            'username': 'バックアップテストユーザー',
            'email': 'backup@example.com'
        })
        
        # データをバックアップ
        result = client1.backup_data(backup_file)
        assert result, "データのバックアップに失敗しました"
        print(f"✓ データをバックアップしました: {backup_file}")
        
        # データをクリア
        client1.clear_all_data()
        stats = client1.get_stats()
        assert stats['total_documents'] == 0, "データがクリアされていません"
        print(f"✓ データをクリアしました")
        
        # バックアップから復元
        result = client1.restore_data(backup_file)
        assert result, "データの復元に失敗しました"
        print(f"✓ データを復元しました")
        
        # 復元されたデータを確認
        user_doc = client1.collection('users').document('user_backup').get()
        assert user_doc.exists, "ユーザードキュメントが復元されていません"
        assert user_doc.to_dict()['username'] == 'バックアップテストユーザー'
        print(f"✓ データが正しく復元されました")
        
        print("✅ データバックアップ/復元テスト成功")
        return True
        
    finally:
        # 一時ファイルを削除
        if os.path.exists(backup_file):
            os.unlink(backup_file)


def test_seed_data():
    """シードデータ機能をテスト"""
    print("\n=== シードデータのテスト ===")
    
    # 一時的なシードファイルを作成
    temp_dir = tempfile.mkdtemp()
    users_file = os.path.join(temp_dir, 'users.json')
    tasks_file = os.path.join(temp_dir, 'tasks.json')
    
    try:
        # ユーザーシードデータ
        users_data = [
            {'_id': 'seed_user_001', 'username': 'シードユーザー1', 'email': 'seed1@example.com'},
            {'_id': 'seed_user_002', 'username': 'シードユーザー2', 'email': 'seed2@example.com'}
        ]
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False)
        
        # タスクシードデータ
        tasks_data = [
            {'_id': 'seed_task_001', 'uid': 'seed_user_001', 'title': 'シードタスク1'},
            {'_id': 'seed_task_002', 'uid': 'seed_user_002', 'title': 'シードタスク2'}
        ]
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, ensure_ascii=False)
        
        # モックFirestoreクライアントを作成
        client = MockFirestoreClient(persist_data=False)
        
        # シードデータをロード
        seed_config = {
            'users': users_file,
            'tasks': tasks_file
        }
        result = client.seed_data(seed_config)
        assert result, "シードデータのロードに失敗しました"
        print(f"✓ シードデータをロードしました")
        
        # シードデータを確認
        users = client.collection('users').get()
        assert len(users) == 2, f"ユーザー数が期待値と異なります: {len(users)} != 2"
        print(f"✓ シードユーザー数: {len(users)}")
        
        tasks = client.collection('tasks').get()
        assert len(tasks) == 2, f"タスク数が期待値と異なります: {len(tasks)} != 2"
        print(f"✓ シードタスク数: {len(tasks)}")
        
        # 特定のドキュメントを確認
        user_doc = client.collection('users').document('seed_user_001').get()
        assert user_doc.exists, "シードユーザーが存在しません"
        assert user_doc.to_dict()['username'] == 'シードユーザー1'
        print(f"✓ シードデータが正しくロードされました")
        
        print("✅ シードデータテスト成功")
        return True
        
    finally:
        # 一時ファイルを削除
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_clear_collection():
    """コレクションクリア機能をテスト"""
    print("\n=== コレクションクリアのテスト ===")
    
    # モックFirestoreクライアントを作成
    client = MockFirestoreClient(persist_data=False)
    
    # テストデータを追加
    client.collection('users').document('user_001').set({'username': 'ユーザー1'})
    client.collection('users').document('user_002').set({'username': 'ユーザー2'})
    client.collection('tasks').document('task_001').set({'title': 'タスク1'})
    
    # 初期状態を確認
    stats = client.get_stats()
    print(f"✓ 初期コレクション数: {stats['collections']}")
    print(f"✓ 初期ドキュメント数: {stats['total_documents']}")
    
    # usersコレクションをクリア
    result = client.clear_collection('users')
    assert result, "コレクションのクリアに失敗しました"
    print(f"✓ usersコレクションをクリアしました")
    
    # クリア後の状態を確認
    users = client.collection('users').get()
    assert len(users) == 0, "usersコレクションがクリアされていません"
    print(f"✓ usersコレクションが空になりました")
    
    # tasksコレクションは残っていることを確認
    tasks = client.collection('tasks').get()
    assert len(tasks) == 1, "tasksコレクションが影響を受けています"
    print(f"✓ tasksコレクションは影響を受けていません")
    
    print("✅ コレクションクリアテスト成功")
    return True


def test_data_merge():
    """データマージ機能をテスト"""
    print("\n=== データマージのテスト ===")
    
    # 一時ファイルを使用
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        merge_file = tmp_file.name
    
    try:
        # モックFirestoreクライアントを作成して初期データを追加
        client = MockFirestoreClient(persist_data=False)
        client.collection('users').document('user_001').set({
            'username': '既存ユーザー',
            'email': 'existing@example.com'
        })
        
        # マージ用のデータを作成
        merge_data = {
            'users': {
                'user_002': {
                    'username': '新規ユーザー',
                    'email': 'new@example.com'
                }
            },
            'tasks': {
                'task_001': {
                    'title': '新規タスク'
                }
            }
        }
        
        with open(merge_file, 'w', encoding='utf-8') as f:
            json.dump(merge_data, f, ensure_ascii=False)
        
        # データをマージ
        result = client.import_data(merge_file, merge=True)
        assert result, "データのマージに失敗しました"
        print(f"✓ データをマージしました")
        
        # マージ後のデータを確認
        users = client.collection('users').get()
        assert len(users) == 2, f"ユーザー数が期待値と異なります: {len(users)} != 2"
        print(f"✓ ユーザー数: {len(users)} (既存+新規)")
        
        # 既存データが残っていることを確認
        user1_doc = client.collection('users').document('user_001').get()
        assert user1_doc.exists, "既存ユーザーが失われています"
        assert user1_doc.to_dict()['username'] == '既存ユーザー'
        print(f"✓ 既存データが保持されています")
        
        # 新規データが追加されていることを確認
        user2_doc = client.collection('users').document('user_002').get()
        assert user2_doc.exists, "新規ユーザーが追加されていません"
        assert user2_doc.to_dict()['username'] == '新規ユーザー'
        print(f"✓ 新規データが追加されました")
        
        # 新しいコレクションが追加されていることを確認
        tasks = client.collection('tasks').get()
        assert len(tasks) == 1, "新規コレクションが追加されていません"
        print(f"✓ 新規コレクションが追加されました")
        
        print("✅ データマージテスト成功")
        return True
        
    finally:
        # 一時ファイルを削除
        if os.path.exists(merge_file):
            os.unlink(merge_file)


def run_all_tests():
    """全テストを実行"""
    print("=" * 60)
    print("サンプルデータ管理機能テストスイート")
    print("Task 2.2 の実装検証")
    print("=" * 60)
    
    tests = [
        ("サンプルデータロード", test_load_sample_data),
        ("テストデータ生成", test_generate_test_data),
        ("エクスポート/インポート", test_export_import_data),
        ("バックアップ/復元", test_backup_restore_data),
        ("シードデータ", test_seed_data),
        ("コレクションクリア", test_clear_collection),
        ("データマージ", test_data_merge)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name}テスト失敗: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_name}テストエラー: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"テスト結果: {passed}件成功, {failed}件失敗")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 全てのテストが成功しました！")
        print("\nTask 2.2 の実装が完了しました:")
        print("✓ JSONファイルからのサンプルデータロード")
        print("✓ テストデータの生成機能")
        print("✓ データのエクスポート/インポート機能")
        print("✓ バックアップ/復元機能")
        print("✓ シードデータ機能")
        print("✓ コレクションクリア機能")
        print("✓ データマージ機能")
        return True
    else:
        print(f"\n⚠️ {failed}件のテストが失敗しました")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
