from __future__ import annotations
import uuid
from datetime import datetime
from typing import Dict, List
from .rbac_models import (
    PermissionLevel, Permission, Role, UserRole, ResourceType, Action
)

class RBACSystem:
    def __init__(self):
        self.roles: Dict[str, Role] = self._init_default_roles()
        self.user_roles: Dict[str, List[UserRole]] = {}

    def _init_default_roles(self) -> Dict[str, Role]:
        def rid():
            return str(uuid.uuid4())
        view = Role(
            role_id=rid(),
            name="Guardian View Only",
            description="ユーザーデータの閲覧のみ可能",
            permission_level=PermissionLevel.VIEW_ONLY,
            permissions=[
                Permission(ResourceType.USER_PROFILE, {Action.READ}),
                Permission(ResourceType.TASK_DATA, {Action.READ}),
                Permission(ResourceType.MOOD_DATA, {Action.READ}),
                Permission(ResourceType.REPORTS, {Action.READ}),
            ],
        )
        task_edit = Role(
            role_id=rid(),
            name="Guardian Task Editor",
            description="タスクの編集が可能",
            permission_level=PermissionLevel.TASK_EDIT,
            permissions=[
                Permission(ResourceType.USER_PROFILE, {Action.READ}),
                Permission(ResourceType.TASK_DATA, {Action.READ, Action.WRITE}),
                Permission(ResourceType.MOOD_DATA, {Action.READ}),
                Permission(ResourceType.REPORTS, {Action.READ}),
            ],
        )
        chat_send = Role(
            role_id=rid(),
            name="Guardian Chat Sender",
            description="チャットメッセージの送信が可能",
            permission_level=PermissionLevel.CHAT_SEND,
            permissions=[
                Permission(ResourceType.USER_PROFILE, {Action.READ}),
                Permission(ResourceType.TASK_DATA, {Action.READ, Action.WRITE}),
                Permission(ResourceType.MOOD_DATA, {Action.READ}),
                Permission(ResourceType.CHAT_MESSAGES, {Action.READ, Action.WRITE}),
                Permission(ResourceType.REPORTS, {Action.READ}),
            ],
        )
        return {
            PermissionLevel.VIEW_ONLY.value: view,
            PermissionLevel.TASK_EDIT.value: task_edit,
            PermissionLevel.CHAT_SEND.value: chat_send,
        }

    def _role_from_level(self, level: PermissionLevel) -> Role:
        return self.roles[level.value]

    def grant_role(self, user_id: str, guardian_id: str, level: PermissionLevel, granted_by: str) -> bool:
        role = self._role_from_level(level)
        assignment = UserRole(
            assignment_id=str(uuid.uuid4()),
            guardian_id=guardian_id,
            user_id=user_id,
            role=role,
            granted_by=granted_by,
        )
        self.user_roles.setdefault(user_id, []).append(assignment)
        return True

    def revoke_role(self, user_id: str, guardian_id: str, level: PermissionLevel) -> bool:
        roles = self.user_roles.get(user_id, [])
        found = False
        for ur in roles:
            if ur.guardian_id == guardian_id and ur.role.permission_level == level and ur.is_active:
                ur.is_active = False
                found = True
        return found

    def check_permission(self, guardian_id: str, user_id: str, resource: ResourceType, action: Action) -> bool:
        for ur in self.user_roles.get(user_id, []):
            if not ur.is_active:
                continue
            if ur.guardian_id != guardian_id:
                continue
            for p in ur.role.permissions:
                if p.resource_type == resource and action in p.actions:
                    return True
        return False

    def get_user_guardians(self, user_id: str) -> List[str]:
        return [ur.guardian_id for ur in self.user_roles.get(user_id, []) if ur.is_active]

    def get_guardian_users(self, guardian_id: str) -> List[str]:
        users: List[str] = []
        for uid, roles in self.user_roles.items():
            if any(ur.guardian_id == guardian_id and ur.is_active for ur in roles):
                users.append(uid)
        return users

    def get_permission_summary(self, guardian_id: str, user_id: str) -> Dict:
        perms = []
        for ur in self.user_roles.get(user_id, []):
            if ur.guardian_id != guardian_id or not ur.is_active:
                continue
            perms.extend(ur.role.permissions)
        has_access = len(perms) > 0
        return {
            "has_access": has_access,
            "resources": list({p.resource_type.value for p in perms}),
        }

    def export_roles_data(self) -> Dict:
        return {
            "roles": {k: v.to_public_dict() for k, v in self.roles.items()},
            "active_assignments": sum(len(v) for v in self.user_roles.values()),
            "user_roles_count": len(self.user_roles),
        }

    def cleanup_expired_roles(self) -> int:
        count = 0
        now = datetime.utcnow()
        for roles in self.user_roles.values():
            for ur in roles:
                if ur.is_active and ur.expires_at and ur.expires_at < now:
                    ur.is_active = False
                    count += 1
        return count
