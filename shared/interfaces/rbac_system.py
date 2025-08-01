"""
RBAC System Interface

Role-Based Access Control システムのインターフェース定義
Requirements: 6.1
"""

from typing import Dict, List, Optional, Set, Any
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class PermissionLevel(str, Enum):
    """権限レベル"""
    VIEW_ONLY = "view_only"     # 閲覧のみ
    TASK_EDIT = "task_edit"     # タスク編集可能
    CHAT_SEND = "chat_send"     # チャット送信可能


class ResourceType(str, Enum):
    """リソースタイプ"""
    USER_PROFILE = "user_profile"       # ユーザープロファイル
    TASK_DATA = "task_data"            # タスクデータ
    MOOD_DATA = "mood_data"            # 気分データ
    STORY_DATA = "story_data"          # ストーリーデータ
    MANDALA_DATA = "mandala_data"      # Mandalaデータ
    CHAT_MESSAGES = "chat_messages"    # チャットメッセージ
    REPORTS = "reports"                # レポート


class Action(str, Enum):
    """アクション"""
    READ = "read"           # 読み取り
    WRITE = "write"         # 書き込み
    DELETE = "delete"       # 削除
    EXECUTE = "execute"     # 実行


class Permission(BaseModel):
    """権限定義"""
    resource_type: ResourceType
    actions: Set[Action]
    conditions: Dict[str, Any] = {}  # 条件（時間制限など）


class Role(BaseModel):
    """ロール定義"""
    role_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    permissions: List[Permission] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class UserRole(BaseModel):
    """ユーザーロール割り当て"""
    assignment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    guardian_id: str
    user_id: str
    role: Role
    granted_by: str
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = True


class RBACSystem:
    """RBAC システム"""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, List[UserRole]] = {}  # user_id -> roles
        self.guardian_roles: Dict[str, List[UserRole]] = {}  # guardian_id -> roles
        
        # デフォルトロール初期化
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """デフォルトロール初期化"""
        # 閲覧専用ロール
        view_only_role = Role(
            name="Guardian View Only",
            description="ユーザーデータの閲覧のみ可能",
            permissions=[
                Permission(
                    resource_type=ResourceType.USER_PROFILE,
                    actions={Action.READ}
                ),
                Permission(
                    resource_type=ResourceType.TASK_DATA,
                    actions={Action.READ}
                ),
                Permission(
                    resource_type=ResourceType.MOOD_DATA,
                    actions={Action.READ}
                ),
                Permission(
                    resource_type=ResourceType.REPORTS,
                    actions={Action.READ}
                )
            ]
        )
        
        # タスク編集ロール
        task_edit_role = Role(
            name="Guardian Task Editor",
            description="タスクの編集が可能",
            permissions=[
                Permission(
                    resource_type=ResourceType.USER_PROFILE,
                    actions={Action.READ}
                ),
                Permission(
                    resource_type=ResourceType.TASK_DATA,
                    actions={Action.READ, Action.WRITE}
                ),
                Permission(
                    resource_type=ResourceType.MOOD_DATA,
                    actions={Action.READ}
                ),
                Permission(
                    resource_type=ResourceType.REPORTS,
                    actions={Action.READ}
                )
            ]
        )
        
        # チャット送信ロール
        chat_send_role = Role(
            name="Guardian Chat Sender",
            description="チャットメッセージの送信が可能",
            permissions=[
                Permission(
                    resource_type=ResourceType.USER_PROFILE,
                    actions={Action.READ}
                ),
                Permission(
                    resource_type=ResourceType.TASK_DATA,
                    actions={Action.READ, Action.WRITE}
                ),
                Permission(
                    resource_type=ResourceType.MOOD_DATA,
                    actions={Action.READ}
                ),
                Permission(
                    resource_type=ResourceType.CHAT_MESSAGES,
                    actions={Action.READ, Action.WRITE}
                ),
                Permission(
                    resource_type=ResourceType.REPORTS,
                    actions={Action.READ}
                )
            ]
        )
        
        self.roles[PermissionLevel.VIEW_ONLY.value] = view_only_role
        self.roles[PermissionLevel.TASK_EDIT.value] = task_edit_role
        self.roles[PermissionLevel.CHAT_SEND.value] = chat_send_role
    
    def grant_role(
        self,
        guardian_id: str,
        user_id: str,
        permission_level: PermissionLevel,
        granted_by: str,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """ロール付与"""
        try:
            role = self.roles.get(permission_level.value)
            if not role:
                return False
            
            user_role = UserRole(
                guardian_id=guardian_id,
                user_id=user_id,
                role=role,
                granted_by=granted_by,
                expires_at=expires_at
            )
            
            # ユーザーロール記録
            if user_id not in self.user_roles:
                self.user_roles[user_id] = []
            self.user_roles[user_id].append(user_role)
            
            # ガーディアンロール記録
            if guardian_id not in self.guardian_roles:
                self.guardian_roles[guardian_id] = []
            self.guardian_roles[guardian_id].append(user_role)
            
            return True
            
        except Exception:
            return False
    
    def revoke_role(self, guardian_id: str, user_id: str) -> bool:
        """ロール取り消し"""
        try:
            # ユーザーロールから削除
            if user_id in self.user_roles:
                self.user_roles[user_id] = [
                    role for role in self.user_roles[user_id]
                    if role.guardian_id != guardian_id
                ]
            
            # ガーディアンロールから削除
            if guardian_id in self.guardian_roles:
                self.guardian_roles[guardian_id] = [
                    role for role in self.guardian_roles[guardian_id]
                    if role.user_id != user_id
                ]
            
            return True
            
        except Exception:
            return False
    
    def check_permission(
        self,
        guardian_id: str,
        user_id: str,
        resource_type: ResourceType,
        action: Action
    ) -> bool:
        """権限チェック"""
        try:
            # ガーディアンのロール取得
            guardian_roles = self.guardian_roles.get(guardian_id, [])
            
            for user_role in guardian_roles:
                # 対象ユーザーのロールかチェック
                if user_role.user_id != user_id:
                    continue
                
                # アクティブかチェック
                if not user_role.is_active:
                    continue
                
                # 有効期限チェック
                if user_role.expires_at and datetime.utcnow() > user_role.expires_at:
                    continue
                
                # 権限チェック
                for permission in user_role.role.permissions:
                    if (permission.resource_type == resource_type and 
                        action in permission.actions):
                        return True
            
            return False
            
        except Exception:
            return False
    
    def get_user_guardians(self, user_id: str) -> List[Dict[str, Any]]:
        """ユーザーのガーディアン一覧取得"""
        guardians = []
        
        user_roles = self.user_roles.get(user_id, [])
        
        for user_role in user_roles:
            if not user_role.is_active:
                continue
            
            if user_role.expires_at and datetime.utcnow() > user_role.expires_at:
                continue
            
            guardians.append({
                "guardian_id": user_role.guardian_id,
                "permission_level": user_role.role.name,
                "role_name": user_role.role.description,
                "granted_at": user_role.granted_at.isoformat(),
                "expires_at": user_role.expires_at.isoformat() if user_role.expires_at else None
            })
        
        return guardians
    
    def get_guardian_users(self, guardian_id: str) -> List[Dict[str, Any]]:
        """ガーディアンの管理ユーザー一覧取得"""
        users = []
        
        guardian_roles = self.guardian_roles.get(guardian_id, [])
        
        for user_role in guardian_roles:
            if not user_role.is_active:
                continue
            
            if user_role.expires_at and datetime.utcnow() > user_role.expires_at:
                continue
            
            # 許可されたアクション一覧生成
            allowed_actions = {}
            for permission in user_role.role.permissions:
                resource = permission.resource_type.value
                actions = [action.value for action in permission.actions]
                allowed_actions[resource] = actions
            
            users.append({
                "user_id": user_role.user_id,
                "permission_level": user_role.role.name,
                "role_name": user_role.role.description,
                "granted_at": user_role.granted_at.isoformat(),
                "expires_at": user_role.expires_at.isoformat() if user_role.expires_at else None,
                "allowed_actions": allowed_actions
            })
        
        return users
    
    def get_permission_summary(self, guardian_id: str, user_id: str) -> Dict[str, Any]:
        """権限サマリー取得"""
        summary = {
            "guardian_id": guardian_id,
            "user_id": user_id,
            "has_access": False,
            "permissions": {},
            "expires_at": None
        }
        
        guardian_roles = self.guardian_roles.get(guardian_id, [])
        
        for user_role in guardian_roles:
            if user_role.user_id != user_id or not user_role.is_active:
                continue
            
            if user_role.expires_at and datetime.utcnow() > user_role.expires_at:
                continue
            
            summary["has_access"] = True
            summary["expires_at"] = user_role.expires_at.isoformat() if user_role.expires_at else None
            
            # 権限詳細
            for permission in user_role.role.permissions:
                resource = permission.resource_type.value
                actions = [action.value for action in permission.actions]
                summary["permissions"][resource] = actions
            
            break  # 最初の有効なロールのみ使用
        
        return summary
    
    def cleanup_expired_roles(self) -> int:
        """期限切れロールのクリーンアップ"""
        cleaned_count = 0
        current_time = datetime.utcnow()
        
        # ユーザーロールのクリーンアップ
        for user_id in list(self.user_roles.keys()):
            original_count = len(self.user_roles[user_id])
            self.user_roles[user_id] = [
                role for role in self.user_roles[user_id]
                if not role.expires_at or role.expires_at > current_time
            ]
            cleaned_count += original_count - len(self.user_roles[user_id])
            
            # 空のリストは削除
            if not self.user_roles[user_id]:
                del self.user_roles[user_id]
        
        # ガーディアンロールのクリーンアップ
        for guardian_id in list(self.guardian_roles.keys()):
            original_count = len(self.guardian_roles[guardian_id])
            self.guardian_roles[guardian_id] = [
                role for role in self.guardian_roles[guardian_id]
                if not role.expires_at or role.expires_at > current_time
            ]
            cleaned_count += original_count - len(self.guardian_roles[guardian_id])
            
            # 空のリストは削除
            if not self.guardian_roles[guardian_id]:
                del self.guardian_roles[guardian_id]
        
        return cleaned_count
    
    def export_roles_data(self) -> Dict[str, Any]:
        """ロールデータエクスポート"""
        return {
            "roles": {
                role_id: {
                    "name": role.name,
                    "description": role.description,
                    "permissions": [
                        {
                            "resource_type": perm.resource_type.value,
                            "actions": [action.value for action in perm.actions]
                        }
                        for perm in role.permissions
                    ]
                }
                for role_id, role in self.roles.items()
            },
            "active_assignments": len([
                role for roles in self.user_roles.values() 
                for role in roles if role.is_active
            ]),
            "total_users": len(self.user_roles),
            "total_guardians": len(self.guardian_roles)
        }


# グローバルインスタンス
rbac_system = RBACSystem()