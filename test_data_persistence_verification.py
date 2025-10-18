#!/usr/bin/env python3
"""
データ永続化機能の検証テスト

タスク2.3の実装を検証します：
- ローカルファイルへのデータ保存
- セッション間でのデータ保持
- データクリーンアップ機能
"""

import json
import os
import tempfile
from pathlib import Path
from mock_database import MockFirestoreClient, reset_mock_firestore


def test_data_persistence():
    """データ永続化のテスト"""
    print("=" * 60)
    print("データ永続化機能のテスト")
    print("=" * 60)
    
    # 一時ファイルを使用
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = os.path.join(temp_dir, "test_firestore.json")
        
        # テスト1: データの保存
        print("\n[テスト1] データの保存")
        print("-" * 60)
        
        client1 = MockFirestoreClient(persist_data=True, data_file=data_file)
        
        # テストデータを追加
        client1.collection('users').document('user001').set({
            'username': 'テストユーザー1',
            'email': 'test1@example.com',
            'level': 5
        })
        
        client1.collection('tasks').document('task001').set({
            'title': 'テストタスク1',
            'status': 'pending',
            'difficulty': 3
        })
        
        # ファイルが作成されたことを確認
        assert os.path.exists(data_file), "データファイルが作成されていません"
        print(f"✓ データファイルが作成されました: {data_file}")
        
        # ファイル内容を確認
        with open(data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert 'users' in saved_data, "usersコレクションが保存されていません"
        assert 'tasks' in saved_data, "tasksコレクションが保存されていません"
        print(f"✓ コレクション数: {len(saved_data)}")
        print(f"✓ usersドキュメント数: {len(saved_data['users'])}")
        print(f"✓ tasksドキュメント数: {len(saved_data['tasks'])}")
        
        # テスト2: セッション間でのデータ保持
        print("\n[テスト2] セッション間でのデータ保持")
        print("-" * 60)
        
        # 新しいクライアントインスタンスを作成（セッションをシミュレート）
        client2 = MockFirestoreClient(persist_data=True, data_file=data_file)
        
        # データが復元されているか確認
        user_doc = client2.collection('users').document('user001').get()
        assert user_doc.exists, "ユーザードキュメントが復元されていません"
        user_data = user_doc.to_dict()
        assert user_data['username'] == 'テストユーザー1', "ユーザーデータが正しく復元されていません"
        print(f"✓ ユーザーデータが復元されました: {user_data['username']}")
        
        task_doc = client2.collection('tasks').document('task001').get()
        assert task_doc.exists, "タスクドキュメントが復元されていません"
        task_data = task_doc.to_dict()
        assert task_data['title'] == 'テストタスク1', "タスクデータが正しく復元されていません"
        print(f"✓ タスクデータが復元されました: {task_data['title']}")
        
        # 追加データを保存
        client2.collection('users').document('user002').set({
            'username': 'テストユーザー2',
            'email': 'test2@example.com',
            'level': 3
        })
        
        # テスト3: データの更新と永続化
        print("\n[テスト3] データの更新と永続化")
        print("-" * 60)
        
        # データを更新
        client2.collection('users').document('user001').update({
            'level': 10,
            'last_login': '2024-01-01T00:00:00Z'
        })
        
        # 新しいセッションで更新が反映されているか確認
        client3 = MockFirestoreClient(persist_data=True, data_file=data_file)
        updated_user = client3.collection('users').document('user001').get()
        updated_data = updated_user.to_dict()
        assert updated_data['level'] == 10, "更新されたデータが永続化されていません"
        print(f"✓ 更新されたレベル: {updated_data['level']}")
        print(f"✓ 追加されたフィールド: last_login = {updated_data.get('last_login')}")
        
        # テスト4: データクリーンアップ機能
        print("\n[テスト4] データクリーンアップ機能")
        print("-" * 60)
        
        # 統計情報を取得
        stats_before = client3.get_stats()
        print(f"クリーンアップ前:")
        print(f"  - コレクション数: {stats_before['collections']}")
        print(f"  - 総ドキュメント数: {stats_before['total_documents']}")
        
        # 特定のコレクションをクリア
        client3.clear_collection('tasks')
        
        stats_after_partial = client3.get_stats()
        print(f"\ntasksコレクションクリア後:")
        print(f"  - コレクション数: {stats_after_partial['collections']}")
        print(f"  - 総ドキュメント数: {stats_after_partial['total_documents']}")
        assert stats_after_partial['total_documents'] < stats_before['total_documents'], \
            "コレクションクリアが機能していません"
        print(f"✓ tasksコレクションがクリアされました")
        
        # 全データをクリア
        client3.clear_all_data()
        
        stats_after_clear = client3.get_stats()
        print(f"\n全データクリア後:")
        print(f"  - コレクション数: {stats_after_clear['collections']}")
        print(f"  - 総ドキュメント数: {stats_after_clear['total_documents']}")
        assert stats_after_clear['total_documents'] == 0, "全データクリアが機能していません"
        print(f"✓ 全データがクリアされました")
        
        # クリア後のファイルを確認
        with open(data_file, 'r', encoding='utf-8') as f:
            cleared_data = json.load(f)
        assert len(cleared_data) == 0, "ファイルが正しくクリアされていません"
        print(f"✓ データファイルも空になりました")
        
        # テスト5: バックアップと復元
        print("\n[テスト5] バックアップと復元")
        print("-" * 60)
        
        # テストデータを再度追加
        client4 = MockFirestoreClient(persist_data=True, data_file=data_file)
        client4.collection('users').document('user003').set({
            'username': 'バックアップテスト',
            'email': 'backup@example.com'
        })
        
        # バックアップを作成
        backup_file = os.path.join(temp_dir, "backup_test.json")
        success = client4.backup_data(backup_file)
        assert success, "バックアップの作成に失敗しました"
        assert os.path.exists(backup_file), "バックアップファイルが作成されていません"
        print(f"✓ バックアップが作成されました: {backup_file}")
        
        # データをクリア
        client4.clear_all_data()
        assert client4.get_stats()['total_documents'] == 0, "データがクリアされていません"
        print(f"✓ データをクリアしました")
        
        # バックアップから復元
        success = client4.restore_data(backup_file)
        assert success, "バックアップからの復元に失敗しました"
        
        restored_user = client4.collection('users').document('user003').get()
        assert restored_user.exists, "復元されたデータが見つかりません"
        restored_data = restored_user.to_dict()
        assert restored_data['username'] == 'バックアップテスト', "復元されたデータが正しくありません"
        print(f"✓ バックアップから復元されました: {restored_data['username']}")
        
        # テスト6: データのエクスポートとインポート
        print("\n[テスト6] データのエクスポートとインポート")
        print("-" * 60)
        
        # エクスポート
        export_file = os.path.join(temp_dir, "export_test.json")
        success = client4.export_data(export_file)
        assert success, "エクスポートに失敗しました"
        print(f"✓ データをエクスポートしました: {export_file}")
        
        # 新しいクライアントでインポート（マージモード）
        client5 = MockFirestoreClient(persist_data=True, data_file=data_file)
        client5.collection('users').document('user004').set({
            'username': '既存ユーザー',
            'email': 'existing@example.com'
        })
        
        # マージモードでインポート
        success = client5.import_data(export_file, merge=True)
        assert success, "インポートに失敗しました"
        
        # 両方のユーザーが存在することを確認
        user3 = client5.collection('users').document('user003').get()
        user4 = client5.collection('users').document('user004').get()
        assert user3.exists and user4.exists, "マージインポートが正しく機能していません"
        print(f"✓ マージモードでインポートされました")
        print(f"  - user003: {user3.to_dict()['username']}")
        print(f"  - user004: {user4.to_dict()['username']}")
        
    print("\n" + "=" * 60)
    print("✓ 全てのテストが成功しました！")
    print("=" * 60)


def test_persistence_without_flag():
    """永続化フラグがfalseの場合のテスト"""
    print("\n" + "=" * 60)
    print("永続化無効時の動作テスト")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = os.path.join(temp_dir, "no_persist.json")
        
        # 永続化を無効にしたクライアント
        client = MockFirestoreClient(persist_data=False, data_file=data_file)
        
        # データを追加
        client.collection('users').document('user001').set({
            'username': 'テストユーザー',
            'email': 'test@example.com'
        })
        
        # ファイルが作成されていないことを確認
        assert not os.path.exists(data_file), "永続化が無効なのにファイルが作成されました"
        print("✓ 永続化が無効の場合、ファイルは作成されません")
        
        # メモリ内ではデータが存在することを確認
        user = client.collection('users').document('user001').get()
        assert user.exists, "メモリ内のデータが見つかりません"
        print("✓ メモリ内ではデータが正常に動作します")
    
    print("=" * 60)


def test_auto_save_on_operations():
    """各操作で自動保存されることを確認"""
    print("\n" + "=" * 60)
    print("自動保存機能のテスト")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = os.path.join(temp_dir, "auto_save.json")
        
        client = MockFirestoreClient(persist_data=True, data_file=data_file)
        
        # 追加操作
        print("\n[追加操作]")
        client.collection('users').document('user001').set({'name': 'User1'})
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert 'user001' in data.get('users', {}), "追加操作後に保存されていません"
        print("✓ 追加操作後に自動保存されました")
        
        # 更新操作
        print("\n[更新操作]")
        client.collection('users').document('user001').update({'name': 'Updated User1'})
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data['users']['user001']['name'] == 'Updated User1', "更新操作後に保存されていません"
        print("✓ 更新操作後に自動保存されました")
        
        # 削除操作
        print("\n[削除操作]")
        client.collection('users').document('user001').delete()
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert 'user001' not in data.get('users', {}), "削除操作後に保存されていません"
        print("✓ 削除操作後に自動保存されました")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    try:
        test_data_persistence()
        test_persistence_without_flag()
        test_auto_save_on_operations()
        
        print("\n" + "=" * 60)
        print("🎉 タスク2.3の全ての機能が正常に動作しています！")
        print("=" * 60)
        print("\n実装された機能:")
        print("  ✓ ローカルファイルへのデータ保存")
        print("  ✓ セッション間でのデータ保持")
        print("  ✓ データクリーンアップ機能")
        print("  ✓ バックアップと復元")
        print("  ✓ データのエクスポート/インポート")
        print("  ✓ 自動保存機能")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ テスト失敗: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
