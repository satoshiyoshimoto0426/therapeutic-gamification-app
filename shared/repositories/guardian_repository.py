"""
Guardian repository for managing guardian-user relationships and RBAC permissions
Handles guardian links, care points, and permission management
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from google.cloud import firestore

from .base_repository import BaseRepository
from ..interfaces.core_types import GuardianLink, GuardianPermission
from ..utils.exceptions import ValidationError, NotFoundError


class GuardianRepository(BaseRepository[GuardianLink]):
    """Repository for guardian-user relationships"""
    
    def __init__(self, db_client: firestore.Client):
        super().__init__(db_client, "guardian_links")
    
    def _to_entity(self, doc_data: Dict[str, Any], doc_id: str = None) -> GuardianLink:
        """Convert Firestore document to GuardianLink entity"""
        return GuardianLink(
            guardian_id=doc_data["guardian_id"],
            user_id=doc_data["user_id"],
            permission_level=GuardianPermission(doc_data["permission_level"]),
            created_at=doc_data["created_at"],
            approved_by_user=doc_data.get("approved_by_user", False),
            care_points=doc_data.get("care_points", 0)
        )
    
    def _to_document(self, entity: GuardianLink) -> Dict[str, Any]:
        """Convert GuardianLink entity to Firestore document"""
        return {
            "guardian_id": entity.guardian_id,
            "user_id": entity.user_id,
            "permission_level": entity.permission_level.value,
            "created_at": entity.created_at,
            "approved_by_user": entity.approved_by_user,
            "care_points": entity.care_points
        }
    
    async def create_guardian_link(self, guardian_id: str, user_id: str, 
                                 permission_level: GuardianPermission,
                                 relationship_type: str = "guardian") -> str:
        """Create new guardian link (requires user approval)"""
        try:
            # Check if link already exists
            existing_link = await self.get_guardian_link(guardian_id, user_id)
            if existing_link:
                raise ValidationError("Guardian link already exists")
            
            # Validate that guardian and user are different
            if guardian_id == user_id:
                raise ValidationError("Guardian cannot be the same as user")
            
            guardian_link = GuardianLink(
                guardian_id=guardian_id,
                user_id=user_id,
                permission_level=permission_level,
                created_at=datetime.utcnow(),
                approved_by_user=False,  # Requires user approval
                care_points=0
            )
            
            # Use composite key as document ID for easy lookup
            document_id = f"{guardian_id}_{user_id}"
            
            doc_data = self._to_document(guardian_link)
            doc_data["relationship_type"] = relationship_type
            doc_data["link_id"] = document_id
            
            doc_ref = self.collection_ref.document(document_id)
            doc_ref.set(doc_data)
            
            self.logger.info(f"Created guardian link: {guardian_id} -> {user_id}")
            return document_id
            
        except Exception as e:
            self.logger.error(f"Failed to create guardian link: {str(e)}")
            raise
    
    async def get_guardian_link(self, guardian_id: str, user_id: str) -> Optional[GuardianLink]:
        """Get specific guardian link"""
        try:
            document_id = f"{guardian_id}_{user_id}"
            doc_ref = self.collection_ref.document(document_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            return self._to_entity(doc.to_dict(), doc.id)
            
        except Exception as e:
            self.logger.error(f"Failed to get guardian link {guardian_id} -> {user_id}: {str(e)}")
            raise
    
    async def approve_guardian_link(self, guardian_id: str, user_id: str) -> bool:
        """User approves guardian link"""
        try:
            document_id = f"{guardian_id}_{user_id}"
            
            updates = {
                "approved_by_user": True,
                "approved_at": datetime.utcnow()
            }
            
            result = await self.update(document_id, updates)
            
            if result:
                self.logger.info(f"Approved guardian link: {guardian_id} -> {user_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to approve guardian link: {str(e)}")
            raise
    
    async def reject_guardian_link(self, guardian_id: str, user_id: str) -> bool:
        """User rejects guardian link (deletes it)"""
        try:
            document_id = f"{guardian_id}_{user_id}"
            result = await self.delete(document_id)
            
            if result:
                self.logger.info(f"Rejected guardian link: {guardian_id} -> {user_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to reject guardian link: {str(e)}")
            raise
    
    async def get_user_guardians(self, user_id: str, approved_only: bool = True) -> List[Dict[str, Any]]:
        """Get all guardians for a user"""
        try:
            query = self.collection_ref.where("user_id", "==", user_id)
            
            if approved_only:
                query = query.where("approved_by_user", "==", True)
            
            docs = query.get()
            
            guardians = []
            for doc in docs:
                data = doc.to_dict()
                guardian_info = {
                    "guardian_id": data["guardian_id"],
                    "permission_level": data["permission_level"],
                    "relationship_type": data.get("relationship_type", "guardian"),
                    "care_points": data.get("care_points", 0),
                    "created_at": data["created_at"],
                    "approved_by_user": data.get("approved_by_user", False)
                }
                guardians.append(guardian_info)
            
            return guardians
            
        except Exception as e:
            self.logger.error(f"Failed to get guardians for user {user_id}: {str(e)}")
            raise
    
    async def get_guardian_users(self, guardian_id: str, approved_only: bool = True) -> List[Dict[str, Any]]:
        """Get all users under a guardian's care"""
        try:
            query = self.collection_ref.where("guardian_id", "==", guardian_id)
            
            if approved_only:
                query = query.where("approved_by_user", "==", True)
            
            docs = query.get()
            
            users = []
            for doc in docs:
                data = doc.to_dict()
                user_info = {
                    "user_id": data["user_id"],
                    "permission_level": data["permission_level"],
                    "relationship_type": data.get("relationship_type", "guardian"),
                    "care_points": data.get("care_points", 0),
                    "created_at": data["created_at"],
                    "approved_by_user": data.get("approved_by_user", False)
                }
                users.append(user_info)
            
            return users
            
        except Exception as e:
            self.logger.error(f"Failed to get users for guardian {guardian_id}: {str(e)}")
            raise
    
    async def update_permission_level(self, guardian_id: str, user_id: str, 
                                    new_permission: GuardianPermission) -> bool:
        """Update guardian's permission level (only user can do this)"""
        try:
            document_id = f"{guardian_id}_{user_id}"
            
            # Verify link exists and is approved
            link = await self.get_guardian_link(guardian_id, user_id)
            if not link:
                raise NotFoundError("Guardian link not found")
            
            if not link.approved_by_user:
                raise ValidationError("Guardian link not approved by user")
            
            updates = {
                "permission_level": new_permission.value,
                "permission_updated_at": datetime.utcnow()
            }
            
            result = await self.update(document_id, updates)
            
            if result:
                self.logger.info(f"Updated permission for {guardian_id} -> {user_id} to {new_permission.value}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update permission level: {str(e)}")
            raise
    
    async def add_care_points(self, guardian_id: str, user_id: str, points: int, 
                            reason: str = "task_completion") -> Dict[str, Any]:
        """Add care points to guardian"""
        try:
            if points <= 0:
                raise ValidationError("Care points must be positive")
            
            document_id = f"{guardian_id}_{user_id}"
            
            # Get current care points
            link = await self.get_guardian_link(guardian_id, user_id)
            if not link:
                raise NotFoundError("Guardian link not found")
            
            if not link.approved_by_user:
                raise ValidationError("Guardian link not approved by user")
            
            new_total = link.care_points + points
            
            updates = {
                "care_points": new_total,
                "last_care_points_earned": datetime.utcnow()
            }
            
            await self.update(document_id, updates)
            
            # Log care points transaction
            await self._log_care_points_transaction(guardian_id, user_id, points, reason)
            
            result = {
                "points_added": points,
                "new_total": new_total,
                "reason": reason,
                "timestamp": datetime.utcnow()
            }
            
            self.logger.info(f"Added {points} care points to {guardian_id} for user {user_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to add care points: {str(e)}")
            raise
    
    async def _log_care_points_transaction(self, guardian_id: str, user_id: str, 
                                         points: int, reason: str) -> None:
        """Log care points transaction"""
        try:
            transaction_log = {
                "guardian_id": guardian_id,
                "user_id": user_id,
                "points": points,
                "reason": reason,
                "timestamp": datetime.utcnow(),
                "transaction_type": "earned"
            }
            
            # Store in care_points_transactions collection
            transactions_collection = self.db.collection("care_points_transactions")
            transactions_collection.add(transaction_log)
            
        except Exception as e:
            self.logger.error(f"Failed to log care points transaction: {str(e)}")
            # Don't raise - this is supplementary logging
    
    async def check_permission(self, guardian_id: str, user_id: str, 
                             required_permission: GuardianPermission) -> bool:
        """Check if guardian has required permission for user"""
        try:
            link = await self.get_guardian_link(guardian_id, user_id)
            
            if not link or not link.approved_by_user:
                return False
            
            # Permission hierarchy: view_only < task_edit < chat_send
            permission_levels = {
                GuardianPermission.VIEW_ONLY: 1,
                GuardianPermission.TASK_EDIT: 2,
                GuardianPermission.CHAT_SEND: 3
            }
            
            current_level = permission_levels.get(link.permission_level, 0)
            required_level = permission_levels.get(required_permission, 999)
            
            return current_level >= required_level
            
        except Exception as e:
            self.logger.error(f"Failed to check permission: {str(e)}")
            return False
    
    async def get_pending_approvals(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending guardian link approvals for user"""
        try:
            query = (self.collection_ref
                    .where("user_id", "==", user_id)
                    .where("approved_by_user", "==", False))
            
            docs = query.get()
            
            pending = []
            for doc in docs:
                data = doc.to_dict()
                pending_info = {
                    "guardian_id": data["guardian_id"],
                    "permission_level": data["permission_level"],
                    "relationship_type": data.get("relationship_type", "guardian"),
                    "created_at": data["created_at"],
                    "link_id": doc.id
                }
                pending.append(pending_info)
            
            return pending
            
        except Exception as e:
            self.logger.error(f"Failed to get pending approvals for user {user_id}: {str(e)}")
            raise
    
    async def get_care_points_summary(self, guardian_id: str, days: int = 30) -> Dict[str, Any]:
        """Get care points summary for guardian"""
        try:
            # Get all users under guardian's care
            users = await self.get_guardian_users(guardian_id, approved_only=True)
            
            total_care_points = sum(user["care_points"] for user in users)
            
            # Get recent transactions
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            transactions_collection = self.db.collection("care_points_transactions")
            query = (transactions_collection
                    .where("guardian_id", "==", guardian_id)
                    .where("timestamp", ">=", start_date)
                    .where("timestamp", "<=", end_date)
                    .order_by("timestamp", direction=firestore.Query.DESCENDING))
            
            transaction_docs = query.get()
            
            recent_transactions = []
            points_earned_period = 0
            
            for doc in transaction_docs:
                data = doc.to_dict()
                recent_transactions.append({
                    "user_id": data["user_id"],
                    "points": data["points"],
                    "reason": data["reason"],
                    "timestamp": data["timestamp"]
                })
                points_earned_period += data["points"]
            
            return {
                "total_care_points": total_care_points,
                "points_earned_last_30_days": points_earned_period,
                "users_under_care": len(users),
                "recent_transactions": recent_transactions[:10],  # Last 10 transactions
                "users": users
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get care points summary for guardian {guardian_id}: {str(e)}")
            raise
    
    async def remove_guardian_link(self, guardian_id: str, user_id: str, 
                                 removed_by: str) -> bool:
        """Remove guardian link (can be done by either party)"""
        try:
            document_id = f"{guardian_id}_{user_id}"
            
            # Log the removal
            removal_log = {
                "guardian_id": guardian_id,
                "user_id": user_id,
                "removed_by": removed_by,
                "removed_at": datetime.utcnow()
            }
            
            removals_collection = self.db.collection("guardian_link_removals")
            removals_collection.add(removal_log)
            
            # Delete the link
            result = await self.delete(document_id)
            
            if result:
                self.logger.info(f"Removed guardian link: {guardian_id} -> {user_id} by {removed_by}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to remove guardian link: {str(e)}")
            raise
    
    async def get_guardian_dashboard_data(self, guardian_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for guardian"""
        try:
            # Get users under care
            users = await self.get_guardian_users(guardian_id, approved_only=True)
            
            # Get care points summary
            care_points_summary = await self.get_care_points_summary(guardian_id)
            
            # Get pending approvals (if any users haven't approved yet)
            all_links = await self.get_guardian_users(guardian_id, approved_only=False)
            pending_approvals = [user for user in all_links if not user["approved_by_user"]]
            
            dashboard_data = {
                "guardian_id": guardian_id,
                "users_under_care": len(users),
                "total_care_points": care_points_summary["total_care_points"],
                "points_earned_last_30_days": care_points_summary["points_earned_last_30_days"],
                "pending_approvals": len(pending_approvals),
                "users": users,
                "recent_transactions": care_points_summary["recent_transactions"],
                "pending_approval_details": pending_approvals
            }
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Failed to get guardian dashboard data for {guardian_id}: {str(e)}")
            raise