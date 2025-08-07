from __future__ import annotations
from enum import StrEnum
from typing import Set, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class PermissionLevel(StrEnum):
    VIEW_ONLY = "view_only"
    TASK_EDIT = "task_edit"
    CHAT_SEND = "chat_send"

class Action(StrEnum):
    READ = "read"
    WRITE = "write"

class ResourceType(StrEnum):
    USER_PROFILE = "user_profile"
    TASK_DATA = "task_data"
    MOOD_DATA = "mood_data"
    CHAT_MESSAGES = "chat_messages"
    REPORTS = "reports"

class Permission(BaseModel):
    resource_type: ResourceType
    actions: Set[Action]
    conditions: Dict = Field(default_factory=dict)

    def __init__(self, *args, **kwargs):
        if args:
            if "resource_type" not in kwargs and len(args) >= 1:
                kwargs["resource_type"] = args[0]
            if "actions" not in kwargs and len(args) >= 2:
                kwargs["actions"] = args[1]
            if "conditions" not in kwargs and len(args) >= 3:
                kwargs["conditions"] = args[2]
        super().__init__(**kwargs)

class Role(BaseModel):
    role_id: str
    name: str
    description: str
    permission_level: PermissionLevel
    permissions: List[Permission]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    def to_public_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "permissions": [
                {"resource_type": p.resource_type.value, "actions": [a.value for a in p.actions]}
                for p in self.permissions
            ],
        }

class UserRole(BaseModel):
    assignment_id: str
    guardian_id: str
    user_id: str
    role: Role
    granted_by: str
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = True
