#!/usr/bin/env python3
"""
モックFirestoreデータベース実装

ローカルテスト環境で使用するFirestoreのモック実装を提供します。
本番のFirestoreに接続せずに、インメモリでデータを管理します。
"""

import json
import uuid
from typing import Dict, List, Any, Optional, Iterator
from pathlib import Path
from datetime import datetime
from copy import deepcopy


class MockDocumentSnapshot:
    """モックドキュメントスナップショット"""
    
    def __init__(self, doc_id: str, data: Optional[Dict[str, Any]] = None, exists: bool = True):
        self._id = doc_id
        self._data = data or {}
        self._exists = exists
    
    @property
    def id(self) -> str:
        """ドキュメントID"""
        return self._id
    
    @property
    def exists(self) -> bool:
        """ドキュメントの存在確認"""
        return self._exists
    
    def to_dict(self) -> Optional[Dict[str, Any]]:
        """ドキュメントデータを辞書として取得"""
        if not self._exists:
            return None
        return deepcopy(self._data)
    
    def get(self, field_path: str) -> Any:
        """特定フィールドの値を取得"""
        if not self._exists:
            return None
        
        # ネストされたフィールドパスをサポート (例: "user.name")
        keys = field_path.split('.')
        value = self._data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value


class MockDocumentReference:
    """モックドキュメント参照"""
    
    def __init__(self, collection_ref: 'MockCollectionReference', doc_id: str):
        self._collection_ref = collection_ref
        self._id = doc_id
    
    @property
    def id(self) -> str:
        """ドキュメントID"""
        return self._id
    
    @property
    def path(self) -> str:
        """ドキュメントパス"""
        return f"{self._collection_ref.path}/{self._id}"
    
    def get(self) -> MockDocumentSnapshot:
        """ドキュメントを取得"""
        data = self._collection_ref._get_document(self._id)
        exists = data is not None
        return MockDocumentSnapshot(self._id, data, exists)
    
    def set(self, data: Dict[str, Any], merge: bool = False) -> None:
        """ドキュメントを設定"""
        if merge:
            existing_data = self._collection_ref._get_document(self._id) or {}
            existing_data.update(data)
            self._collection_ref._set_document(self._id, existing_data)
        else:
            self._collection_ref._set_document(self._id, data)
    
    def update(self, data: Dict[str, Any]) -> None:
        """ドキュメントを更新"""
        existing_data = self._collection_ref._get_document(self._id)
        if existing_data is None:
            raise ValueError(f"Document {self._id} does not exist")
        existing_data.update(data)
        self._collection_ref._set_document(self._id, existing_data)
    
    def delete(self) -> None:
        """ドキュメントを削除"""
        self._collection_ref._delete_document(self._id)
    
    def collection(self, collection_id: str) -> 'MockCollectionReference':
        """サブコレクションを取得"""
        return MockCollectionReference(
            self._collection_ref._client,
            f"{self.path}/{collection_id}"
        )


class MockQuery:
    """モッククエリ"""
    
    def __init__(self, collection_ref: 'MockCollectionReference'):
        self._collection_ref = collection_ref
        self._filters = []
        self._order_by_field = None
        self._order_direction = 'asc'
        self._limit_count = None
    
    def where(self, field: str, op: str, value: Any) -> 'MockQuery':
        """フィルタ条件を追加"""
        self._filters.append((field, op, value))
        return self
    
    def order_by(self, field: str, direction: str = 'asc') -> 'MockQuery':
        """ソート条件を追加"""
        self._order_by_field = field
        self._order_direction = direction.lower()
        return self
    
    def limit(self, count: int) -> 'MockQuery':
        """取得件数を制限"""
        self._limit_count = count
        return self
    
    def _apply_filters(self, doc_data: Dict[str, Any]) -> bool:
        """フィルタ条件を適用"""
        for field, op, value in self._filters:
            doc_value = doc_data.get(field)
            
            if op == '==':
                if doc_value != value:
                    return False
            elif op == '!=':
                if doc_value == value:
                    return False
            elif op == '<':
                if doc_value is None or doc_value >= value:
                    return False
            elif op == '<=':
                if doc_value is None or doc_value > value:
                    return False
            elif op == '>':
                if doc_value is None or doc_value <= value:
                    return False
            elif op == '>=':
                if doc_value is None or doc_value < value:
                    return False
            elif op == 'in':
                if doc_value not in value:
                    return False
            elif op == 'not-in':
                if doc_value in value:
                    return False
            elif op == 'array-contains':
                if not isinstance(doc_value, list) or value not in doc_value:
                    return False
        
        return True
    
    def stream(self) -> Iterator[MockDocumentSnapshot]:
        """クエリ結果をストリームとして取得"""
        results = []
        
        # 全ドキュメントを取得してフィルタリング
        for doc_id, doc_data in self._collection_ref._get_all_documents().items():
            if self._apply_filters(doc_data):
                results.append((doc_id, doc_data))
        
        # ソート
        if self._order_by_field:
            reverse = self._order_direction == 'desc'
            results.sort(
                key=lambda x: x[1].get(self._order_by_field, ''),
                reverse=reverse
            )
        
        # 件数制限
        if self._limit_count:
            results = results[:self._limit_count]
        
        # スナップショットとして返す
        for doc_id, doc_data in results:
            yield MockDocumentSnapshot(doc_id, doc_data, True)
    
    def get(self) -> List[MockDocumentSnapshot]:
        """クエリ結果をリストとして取得"""
        return list(self.stream())


class MockCollectionReference:
    """モックコレクション参照"""
    
    def __init__(self, client: 'MockFirestoreClient', collection_path: str):
        self._client = client
        self._path = collection_path
    
    @property
    def path(self) -> str:
        """コレクションパス"""
        return self._path
    
    @property
    def id(self) -> str:
        """コレクションID"""
        return self._path.split('/')[-1]
    
    def document(self, doc_id: Optional[str] = None) -> MockDocumentReference:
        """ドキュメント参照を取得"""
        if doc_id is None:
            doc_id = str(uuid.uuid4())
        return MockDocumentReference(self, doc_id)
    
    def add(self, data: Dict[str, Any]) -> MockDocumentReference:
        """ドキュメントを追加"""
        doc_id = str(uuid.uuid4())
        doc_ref = self.document(doc_id)
        doc_ref.set(data)
        return doc_ref
    
    def where(self, field: str, op: str, value: Any) -> MockQuery:
        """クエリを作成"""
        query = MockQuery(self)
        return query.where(field, op, value)
    
    def order_by(self, field: str, direction: str = 'asc') -> MockQuery:
        """ソートクエリを作成"""
        query = MockQuery(self)
        return query.order_by(field, direction)
    
    def limit(self, count: int) -> MockQuery:
        """件数制限クエリを作成"""
        query = MockQuery(self)
        return query.limit(count)
    
    def stream(self) -> Iterator[MockDocumentSnapshot]:
        """全ドキュメントをストリームとして取得"""
        for doc_id, doc_data in self._get_all_documents().items():
            yield MockDocumentSnapshot(doc_id, doc_data, True)
    
    def get(self) -> List[MockDocumentSnapshot]:
        """全ドキュメントをリストとして取得"""
        return list(self.stream())
    
    # 内部メソッド
    def _get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """ドキュメントデータを取得（内部用）"""
        return self._client._get_document(self._path, doc_id)
    
    def _set_document(self, doc_id: str, data: Dict[str, Any]) -> None:
        """ドキュメントデータを設定（内部用）"""
        self._client._set_document(self._path, doc_id, data)
    
    def _delete_document(self, doc_id: str) -> None:
        """ドキュメントを削除（内部用）"""
        self._client._delete_document(self._path, doc_id)
    
    def _get_all_documents(self) -> Dict[str, Dict[str, Any]]:
        """全ドキュメントを取得（内部用）"""
        return self._client._get_all_documents(self._path)


class MockFirestoreClient:
    """モックFirestoreクライアント"""
    
    def __init__(self, persist_data: bool = False, data_file: Optional[str] = None):
        """
        初期化
        
        Args:
            persist_data: データを永続化するかどうか
            data_file: データファイルのパス
        """
        self._data: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._persist_data = persist_data
        self._data_file = Path(data_file) if data_file else Path("./data/mock_firestore.json")
        
        # データファイルが存在する場合は読み込む
        if self._persist_data and self._data_file.exists():
            self._load_data()
    
    def collection(self, collection_id: str) -> MockCollectionReference:
        """コレクション参照を取得"""
        return MockCollectionReference(self, collection_id)
    
    def _get_document(self, collection_path: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """ドキュメントデータを取得"""
        if collection_path not in self._data:
            return None
        return self._data[collection_path].get(doc_id)
    
    def _set_document(self, collection_path: str, doc_id: str, data: Dict[str, Any]) -> None:
        """ドキュメントデータを設定"""
        if collection_path not in self._data:
            self._data[collection_path] = {}
        self._data[collection_path][doc_id] = deepcopy(data)
        
        if self._persist_data:
            self._save_data()
    
    def _delete_document(self, collection_path: str, doc_id: str) -> None:
        """ドキュメントを削除"""
        if collection_path in self._data and doc_id in self._data[collection_path]:
            del self._data[collection_path][doc_id]
            
            if self._persist_data:
                self._save_data()
    
    def _get_all_documents(self, collection_path: str) -> Dict[str, Dict[str, Any]]:
        """コレクション内の全ドキュメントを取得"""
        return self._data.get(collection_path, {})
    
    def _load_data(self) -> bool:
        """データファイルから読み込み"""
        try:
            with open(self._data_file, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
            return True
        except Exception as e:
            print(f"データ読み込みエラー: {e}")
            return False
    
    def _save_data(self) -> bool:
        """データファイルに保存"""
        try:
            self._data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._data_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"データ保存エラー: {e}")
            return False
    
    def load_sample_data(self, data_file: str) -> bool:
        """サンプルデータをロード"""
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)
            
            # サンプルデータをコレクションごとに格納
            for collection_name, documents in sample_data.items():
                if not isinstance(documents, list):
                    continue
                
                for doc_data in documents:
                    # ドキュメントIDを取得（なければ生成）
                    doc_id = doc_data.pop('_id', None) or str(uuid.uuid4())
                    
                    # ドキュメントを設定
                    self._set_document(collection_name, doc_id, doc_data)
            
            print(f"サンプルデータをロードしました: {data_file}")
            return True
        except Exception as e:
            print(f"サンプルデータ読み込みエラー: {e}")
            return False
    
    def clear_all_data(self) -> bool:
        """全データをクリア"""
        try:
            self._data = {}
            if self._persist_data:
                self._save_data()
            return True
        except Exception as e:
            print(f"データクリアエラー: {e}")
            return False
    
    def export_data(self, output_file: str) -> bool:
        """データをエクスポート"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            
            print(f"データをエクスポートしました: {output_file}")
            return True
        except Exception as e:
            print(f"データエクスポートエラー: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """データベース統計情報を取得"""
        stats = {
            'collections': len(self._data),
            'total_documents': sum(len(docs) for docs in self._data.values()),
            'collections_detail': {}
        }
        
        for collection_path, documents in self._data.items():
            stats['collections_detail'][collection_path] = len(documents)
        
        return stats
    
    def import_data(self, data_file: str, merge: bool = False) -> bool:
        """
        データをインポート
        
        Args:
            data_file: インポートするJSONファイルのパス
            merge: 既存データとマージするかどうか（Falseの場合は上書き）
        
        Returns:
            成功した場合True
        """
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            if merge:
                # 既存データとマージ
                for collection_path, documents in imported_data.items():
                    if collection_path not in self._data:
                        self._data[collection_path] = {}
                    self._data[collection_path].update(documents)
            else:
                # 既存データを上書き
                self._data = imported_data
            
            if self._persist_data:
                self._save_data()
            
            print(f"データをインポートしました: {data_file}")
            return True
        except Exception as e:
            print(f"データインポートエラー: {e}")
            return False
    
    def generate_test_data(self, config: Dict[str, Any]) -> bool:
        """
        テストデータを生成
        
        Args:
            config: データ生成設定
                {
                    'users': {'count': 10, 'prefix': 'test_user_'},
                    'tasks': {'count': 50, 'users': ['user_id1', 'user_id2']},
                    ...
                }
        
        Returns:
            成功した場合True
        """
        try:
            # ユーザーデータの生成
            if 'users' in config:
                user_config = config['users']
                count = user_config.get('count', 10)
                prefix = user_config.get('prefix', 'test_user_')
                
                for i in range(count):
                    user_id = f"{prefix}{i:03d}"
                    user_data = {
                        'username': f"テストユーザー{i+1}",
                        'email': f"test{i+1}@example.com",
                        'created_at': datetime.utcnow().isoformat() + 'Z',
                        'player_level': (i % 10) + 1,
                        'total_xp': (i % 10) * 50,
                        'yu_level': (i % 5) + 1,
                        'current_xp': (i % 10) * 5,
                        'xp_to_next_level': 100,
                        'resonance_level': (i % 3) + 1,
                        'crystal_count': (i % 20) + 1
                    }
                    self._set_document('users', user_id, user_data)
            
            # タスクデータの生成
            if 'tasks' in config:
                task_config = config['tasks']
                count = task_config.get('count', 50)
                user_ids = task_config.get('users', [])
                
                if not user_ids:
                    # ユーザーIDが指定されていない場合は、既存ユーザーから取得
                    user_ids = list(self._data.get('users', {}).keys())
                
                if user_ids:
                    task_types = ['one_shot', 'daily', 'weekly']
                    statuses = ['pending', 'in_progress', 'completed']
                    difficulties = [1, 2, 3, 4, 5]
                    
                    for i in range(count):
                        task_id = f"task_{i:03d}"
                        user_id = user_ids[i % len(user_ids)]
                        task_data = {
                            'uid': user_id,
                            'title': f"テストタスク{i+1}",
                            'description': f"これはテスト用のタスクです（{i+1}）",
                            'task_type': task_types[i % len(task_types)],
                            'difficulty': difficulties[i % len(difficulties)],
                            'status': statuses[i % len(statuses)],
                            'created_at': datetime.utcnow().isoformat() + 'Z',
                            'estimated_duration': (i % 6 + 1) * 10,
                            'xp_reward': difficulties[i % len(difficulties)] * 10
                        }
                        self._set_document('tasks', task_id, task_data)
            
            # ムードエントリーの生成
            if 'mood_entries' in config:
                mood_config = config['mood_entries']
                count = mood_config.get('count', 30)
                user_ids = mood_config.get('users', [])
                
                if not user_ids:
                    user_ids = list(self._data.get('users', {}).keys())
                
                if user_ids:
                    for i in range(count):
                        mood_id = f"mood_{i:03d}"
                        user_id = user_ids[i % len(user_ids)]
                        mood_data = {
                            'uid': user_id,
                            'mood_score': (i % 5) + 1,
                            'timestamp': datetime.utcnow().isoformat() + 'Z',
                            'notes': f"テストムードエントリー{i+1}",
                            'energy_level': (i % 5) + 1,
                            'stress_level': (i % 5) + 1
                        }
                        self._set_document('mood_entries', mood_id, mood_data)
            
            # マンダラグリッドの生成
            if 'mandala_grids' in config:
                mandala_config = config['mandala_grids']
                count = mandala_config.get('count', 10)
                user_ids = mandala_config.get('users', [])
                
                if not user_ids:
                    user_ids = list(self._data.get('users', {}).keys())
                
                if user_ids:
                    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
                             '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739']
                    
                    for i in range(count):
                        mandala_id = f"mandala_{i:03d}"
                        user_id = user_ids[i % len(user_ids)]
                        cells = []
                        for j in range(9):
                            cells.append({
                                'position': j,
                                'content': f"目標{j+1}",
                                'color': colors[j % len(colors)]
                            })
                        
                        mandala_data = {
                            'uid': user_id,
                            'grid_size': 9,
                            'cells': cells,
                            'created_at': datetime.utcnow().isoformat() + 'Z',
                            'updated_at': datetime.utcnow().isoformat() + 'Z'
                        }
                        self._set_document('mandala_grids', mandala_id, mandala_data)
            
            print(f"テストデータを生成しました")
            return True
        except Exception as e:
            print(f"テストデータ生成エラー: {e}")
            return False
    
    def backup_data(self, backup_file: Optional[str] = None) -> bool:
        """
        データをバックアップ
        
        Args:
            backup_file: バックアップファイルのパス（指定しない場合はタイムスタンプ付きファイル名）
        
        Returns:
            成功した場合True
        """
        try:
            if backup_file is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = f"./data/backup_firestore_{timestamp}.json"
            
            return self.export_data(backup_file)
        except Exception as e:
            print(f"データバックアップエラー: {e}")
            return False
    
    def restore_data(self, backup_file: str) -> bool:
        """
        バックアップからデータを復元
        
        Args:
            backup_file: バックアップファイルのパス
        
        Returns:
            成功した場合True
        """
        return self.import_data(backup_file, merge=False)
    
    def clear_collection(self, collection_path: str) -> bool:
        """
        特定のコレクションをクリア
        
        Args:
            collection_path: クリアするコレクションのパス
        
        Returns:
            成功した場合True
        """
        try:
            if collection_path in self._data:
                self._data[collection_path] = {}
                if self._persist_data:
                    self._save_data()
                print(f"コレクションをクリアしました: {collection_path}")
            return True
        except Exception as e:
            print(f"コレクションクリアエラー: {e}")
            return False
    
    def seed_data(self, seed_config: Dict[str, str]) -> bool:
        """
        複数のサンプルデータファイルからデータをシード
        
        Args:
            seed_config: シード設定
                {
                    'users': 'path/to/users.json',
                    'tasks': 'path/to/tasks.json',
                    ...
                }
        
        Returns:
            成功した場合True
        """
        try:
            for collection_name, file_path in seed_config.items():
                with open(file_path, 'r', encoding='utf-8') as f:
                    documents = json.load(f)
                
                if isinstance(documents, list):
                    for doc_data in documents:
                        doc_id = doc_data.pop('_id', None) or str(uuid.uuid4())
                        self._set_document(collection_name, doc_id, doc_data)
                elif isinstance(documents, dict):
                    for doc_id, doc_data in documents.items():
                        self._set_document(collection_name, doc_id, doc_data)
            
            print(f"シードデータをロードしました")
            return True
        except Exception as e:
            print(f"シードデータロードエラー: {e}")
            return False


# グローバルインスタンス（シングルトン）
_mock_firestore_instance: Optional[MockFirestoreClient] = None


def get_mock_firestore(persist_data: bool = False, data_file: Optional[str] = None) -> MockFirestoreClient:
    """モックFirestoreクライアントのシングルトンインスタンスを取得"""
    global _mock_firestore_instance
    
    if _mock_firestore_instance is None:
        _mock_firestore_instance = MockFirestoreClient(persist_data, data_file)
    
    return _mock_firestore_instance


def reset_mock_firestore() -> None:
    """モックFirestoreクライアントをリセット"""
    global _mock_firestore_instance
    _mock_firestore_instance = None
