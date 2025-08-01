"""
Base repository pattern implementation for Firestore
Provides common CRUD operations and query optimization
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, TypeVar, Generic, Union
from datetime import datetime, timedelta
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter, Or, And
from google.cloud.firestore_v1.types import WriteResult
import logging

from ..config.firestore_collections import validate_document_data, get_collection_schema
from ..utils.exceptions import ValidationError, NotFoundError, DatabaseError
from .query_optimizer import QueryOptimizer, QueryProfiler

T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    """Base repository class with common CRUD operations"""
    
    def __init__(self, db_client: firestore.Client, collection_name: str, enable_optimization: bool = True):
        self.db = db_client
        self.collection_name = collection_name
        self.collection_ref = db_client.collection(collection_name)
        self.logger = logging.getLogger(f"{__name__}.{collection_name}")
        
        # Query optimization
        if enable_optimization:
            self.query_optimizer = QueryOptimizer(db_client)
            self.query_profiler = QueryProfiler(self.query_optimizer)
        else:
            self.query_optimizer = None
            self.query_profiler = None
        
    @abstractmethod
    def _to_entity(self, doc_data: Dict[str, Any], doc_id: str = None) -> T:
        """Convert Firestore document to entity object"""
        pass
    
    @abstractmethod
    def _to_document(self, entity: T) -> Dict[str, Any]:
        """Convert entity object to Firestore document"""
        pass
    
    def _validate_document(self, doc_data: Dict[str, Any]) -> None:
        """Validate document data against schema"""
        errors = validate_document_data(self.collection_name, doc_data)
        if errors:
            raise ValidationError(f"Validation failed: {', '.join(errors)}")
    
    async def create(self, entity: T, document_id: str = None) -> str:
        """Create a new document"""
        try:
            doc_data = self._to_document(entity)
            doc_data['created_at'] = datetime.utcnow()
            doc_data['updated_at'] = datetime.utcnow()
            
            self._validate_document(doc_data)
            
            if document_id:
                doc_ref = self.collection_ref.document(document_id)
                doc_ref.set(doc_data)
                created_id = document_id
            else:
                doc_ref = self.collection_ref.add(doc_data)[1]
                created_id = doc_ref.id
            
            self.logger.info(f"Created document {created_id} in {self.collection_name}")
            return created_id
            
        except Exception as e:
            self.logger.error(f"Failed to create document in {self.collection_name}: {str(e)}")
            raise DatabaseError(f"Create operation failed: {str(e)}")
    
    async def get_by_id(self, document_id: str) -> Optional[T]:
        """Get document by ID"""
        try:
            doc_ref = self.collection_ref.document(document_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            return self._to_entity(doc.to_dict(), doc.id)
            
        except Exception as e:
            self.logger.error(f"Failed to get document {document_id} from {self.collection_name}: {str(e)}")
            raise DatabaseError(f"Get operation failed: {str(e)}")
    
    async def update(self, document_id: str, updates: Dict[str, Any]) -> bool:
        """Update document with partial data"""
        try:
            updates['updated_at'] = datetime.utcnow()
            
            # Validate updates if full document validation is needed
            if len(updates) > 2:  # More than just updated_at
                existing_doc = await self.get_by_id(document_id)
                if not existing_doc:
                    raise NotFoundError(f"Document {document_id} not found")
                
                # Merge updates with existing data for validation
                existing_data = self._to_document(existing_doc)
                existing_data.update(updates)
                self._validate_document(existing_data)
            
            doc_ref = self.collection_ref.document(document_id)
            doc_ref.update(updates)
            
            self.logger.info(f"Updated document {document_id} in {self.collection_name}")
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to update document {document_id} in {self.collection_name}: {str(e)}")
            raise DatabaseError(f"Update operation failed: {str(e)}")
    
    async def delete(self, document_id: str) -> bool:
        """Delete document by ID"""
        try:
            doc_ref = self.collection_ref.document(document_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
            
            doc_ref.delete()
            self.logger.info(f"Deleted document {document_id} from {self.collection_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id} from {self.collection_name}: {str(e)}")
            raise DatabaseError(f"Delete operation failed: {str(e)}")
    
    async def find_by_field(self, field: str, value: Any, limit: int = None) -> List[T]:
        """Find documents by field value"""
        try:
            query = self.collection_ref.where(filter=FieldFilter(field, "==", value))
            
            if limit:
                query = query.limit(limit)
            
            docs = query.get()
            return [self._to_entity(doc.to_dict(), doc.id) for doc in docs]
            
        except Exception as e:
            self.logger.error(f"Failed to find documents by {field} in {self.collection_name}: {str(e)}")
            raise DatabaseError(f"Find operation failed: {str(e)}")
    
    async def find_by_multiple_fields(self, filters: Dict[str, Any], limit: int = None) -> List[T]:
        """Find documents by multiple field values with query optimization"""
        try:
            # Optimize query if optimizer is available
            if self.query_optimizer:
                query_plan = self.query_optimizer.analyze_query(self.collection_name, filters, limit=limit)
                
                # Log optimization hints
                if query_plan.optimization_hints:
                    self.logger.info(f"Query optimization hints for {self.collection_name}: {query_plan.optimization_hints}")
                
                # Optimize filters
                filters = self.query_optimizer.optimize_query_filters(filters)
            
            query = self.collection_ref
            
            for field, value in filters.items():
                if isinstance(value, dict) and 'operator' in value:
                    # Support for complex operators
                    operator = value['operator']
                    val = value['value']
                    query = query.where(filter=FieldFilter(field, operator, val))
                elif isinstance(value, list):
                    query = query.where(filter=FieldFilter(field, "in", value))
                else:
                    query = query.where(filter=FieldFilter(field, "==", value))
            
            if limit:
                query = query.limit(limit)
            
            # Profile query execution if profiler is available
            if self.query_profiler:
                docs = await self.query_profiler.profile_async_query(
                    self.collection_name, 
                    lambda: query.get()
                )
            else:
                docs = query.get()
            
            return [self._to_entity(doc.to_dict(), doc.id) for doc in docs]
            
        except Exception as e:
            self.logger.error(f"Failed to find documents by multiple fields in {self.collection_name}: {str(e)}")
            raise DatabaseError(f"Multi-field find operation failed: {str(e)}")
    
    async def find_with_pagination(self, 
                                 filters: Dict[str, Any] = None,
                                 order_by: str = None,
                                 order_direction: str = "asc",
                                 page_size: int = 20,
                                 start_after: Any = None) -> Dict[str, Any]:
        """Find documents with pagination support and query optimization"""
        try:
            # Optimize query if optimizer is available
            if self.query_optimizer and filters:
                query_plan = self.query_optimizer.analyze_query(
                    self.collection_name, filters, order_by, page_size
                )
                
                # Log performance warnings
                if query_plan.execution_time_estimate > 1.0:
                    self.logger.warning(
                        f"Slow query detected for {self.collection_name}: "
                        f"estimated {query_plan.execution_time_estimate:.2f}s"
                    )
                
                # Optimize filters
                if filters:
                    filters = self.query_optimizer.optimize_query_filters(filters)
            
            query = self.collection_ref
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    if isinstance(value, dict) and 'operator' in value:
                        # Support for complex operators
                        operator = value['operator']
                        val = value['value']
                        query = query.where(filter=FieldFilter(field, operator, val))
                    else:
                        query = query.where(filter=FieldFilter(field, "==", value))
            
            # Apply ordering
            if order_by:
                direction = firestore.Query.DESCENDING if order_direction.lower() == "desc" else firestore.Query.ASCENDING
                query = query.order_by(order_by, direction=direction)
            
            # Apply pagination
            if start_after:
                query = query.start_after(start_after)
            
            query = query.limit(page_size)
            
            # Profile query execution if profiler is available
            if self.query_profiler:
                docs = await self.query_profiler.profile_async_query(
                    self.collection_name, 
                    lambda: query.get()
                )
            else:
                docs = query.get()
            
            entities = [self._to_entity(doc.to_dict(), doc.id) for doc in docs]
            
            # Get last document for next page cursor
            last_doc = docs[-1] if docs else None
            next_cursor = last_doc.get(order_by) if last_doc and order_by else None
            
            return {
                "data": entities,
                "next_cursor": next_cursor,
                "has_more": len(entities) == page_size
            }
            
        except Exception as e:
            self.logger.error(f"Failed paginated query in {self.collection_name}: {str(e)}")
            raise DatabaseError(f"Paginated query failed: {str(e)}")
    
    async def count(self, filters: Dict[str, Any] = None) -> int:
        """Count documents matching filters"""
        try:
            query = self.collection_ref
            
            if filters:
                for field, value in filters.items():
                    query = query.where(filter=FieldFilter(field, "==", value))
            
            # Use aggregation query for better performance
            aggregation_query = query.count()
            result = aggregation_query.get()
            
            return result[0].value
            
        except Exception as e:
            self.logger.error(f"Failed to count documents in {self.collection_name}: {str(e)}")
            raise DatabaseError(f"Count operation failed: {str(e)}")
    
    async def batch_create(self, entities: List[T], document_ids: List[str] = None) -> List[str]:
        """Create multiple documents in a batch"""
        try:
            if document_ids and len(document_ids) != len(entities):
                raise ValueError("Number of document IDs must match number of entities")
            
            batch = self.db.batch()
            created_ids = []
            
            for i, entity in enumerate(entities):
                doc_data = self._to_document(entity)
                doc_data['created_at'] = datetime.utcnow()
                doc_data['updated_at'] = datetime.utcnow()
                
                self._validate_document(doc_data)
                
                if document_ids:
                    doc_ref = self.collection_ref.document(document_ids[i])
                    created_ids.append(document_ids[i])
                else:
                    doc_ref = self.collection_ref.document()
                    created_ids.append(doc_ref.id)
                
                batch.set(doc_ref, doc_data)
            
            batch.commit()
            self.logger.info(f"Batch created {len(entities)} documents in {self.collection_name}")
            return created_ids
            
        except Exception as e:
            self.logger.error(f"Failed batch create in {self.collection_name}: {str(e)}")
            raise DatabaseError(f"Batch create operation failed: {str(e)}")
    
    async def batch_update(self, updates: Dict[str, Dict[str, Any]]) -> bool:
        """Update multiple documents in a batch"""
        try:
            batch = self.db.batch()
            
            for document_id, update_data in updates.items():
                update_data['updated_at'] = datetime.utcnow()
                doc_ref = self.collection_ref.document(document_id)
                batch.update(doc_ref, update_data)
            
            batch.commit()
            self.logger.info(f"Batch updated {len(updates)} documents in {self.collection_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed batch update in {self.collection_name}: {str(e)}")
            raise DatabaseError(f"Batch update operation failed: {str(e)}")
    
    async def find_by_date_range(self, 
                                date_field: str,
                                start_date: datetime,
                                end_date: datetime,
                                additional_filters: Dict[str, Any] = None,
                                limit: int = None) -> List[T]:
        """Find documents within a date range"""
        try:
            query = self.collection_ref.where(
                filter=FieldFilter(date_field, ">=", start_date)
            ).where(
                filter=FieldFilter(date_field, "<=", end_date)
            )
            
            if additional_filters:
                for field, value in additional_filters.items():
                    query = query.where(filter=FieldFilter(field, "==", value))
            
            if limit:
                query = query.limit(limit)
            
            docs = query.get()
            return [self._to_entity(doc.to_dict(), doc.id) for doc in docs]
            
        except Exception as e:
            self.logger.error(f"Failed date range query in {self.collection_name}: {str(e)}")
            raise DatabaseError(f"Date range query failed: {str(e)}")
    
    async def aggregate_by_field(self, 
                               group_by_field: str,
                               aggregate_field: str = None,
                               aggregate_function: str = "count",
                               filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate documents by field (client-side aggregation)"""
        try:
            query = self.collection_ref
            
            if filters:
                for field, value in filters.items():
                    query = query.where(filter=FieldFilter(field, "==", value))
            
            docs = query.get()
            
            # Client-side aggregation
            aggregation_result = {}
            
            for doc in docs:
                doc_data = doc.to_dict()
                group_value = doc_data.get(group_by_field)
                
                if group_value not in aggregation_result:
                    aggregation_result[group_value] = {"count": 0, "sum": 0, "values": []}
                
                aggregation_result[group_value]["count"] += 1
                
                if aggregate_field and aggregate_field in doc_data:
                    value = doc_data[aggregate_field]
                    if isinstance(value, (int, float)):
                        aggregation_result[group_value]["sum"] += value
                        aggregation_result[group_value]["values"].append(value)
            
            # Calculate additional statistics
            for group_value, stats in aggregation_result.items():
                if stats["values"]:
                    stats["average"] = stats["sum"] / len(stats["values"])
                    stats["min"] = min(stats["values"])
                    stats["max"] = max(stats["values"])
                else:
                    stats["average"] = 0
                    stats["min"] = 0
                    stats["max"] = 0
                
                # Remove raw values to reduce response size
                del stats["values"]
            
            return aggregation_result
            
        except Exception as e:
            self.logger.error(f"Failed aggregation query in {self.collection_name}: {str(e)}")
            raise DatabaseError(f"Aggregation query failed: {str(e)}")
    
    async def exists(self, document_id: str) -> bool:
        """Check if document exists"""
        try:
            doc_ref = self.collection_ref.document(document_id)
            doc = doc_ref.get()
            return doc.exists
            
        except Exception as e:
            self.logger.error(f"Failed to check existence of document {document_id} in {self.collection_name}: {str(e)}")
            raise DatabaseError(f"Existence check failed: {str(e)}")
    
    async def get_schema_info(self) -> Dict[str, Any]:
        """Get collection schema information"""
        return get_collection_schema(self.collection_name)

class CachedRepository(BaseRepository[T]):
    """Repository with caching support"""
    
    def __init__(self, db_client: firestore.Client, collection_name: str, cache_ttl_seconds: int = 300):
        super().__init__(db_client, collection_name)
        self.cache = {}
        self.cache_ttl = cache_ttl_seconds
        self.cache_timestamps = {}
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid"""
        if key not in self.cache_timestamps:
            return False
        
        age = datetime.utcnow().timestamp() - self.cache_timestamps[key]
        return age < self.cache_ttl
    
    def _cache_set(self, key: str, value: Any) -> None:
        """Set cache entry"""
        self.cache[key] = value
        self.cache_timestamps[key] = datetime.utcnow().timestamp()
    
    def _cache_get(self, key: str) -> Any:
        """Get cache entry if valid"""
        if self._is_cache_valid(key):
            return self.cache[key]
        
        # Clean up expired entry
        if key in self.cache:
            del self.cache[key]
            del self.cache_timestamps[key]
        
        return None
    
    async def get_by_id(self, document_id: str) -> Optional[T]:
        """Get document by ID with caching"""
        cache_key = f"get_by_id:{document_id}"
        cached_result = self._cache_get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        result = await super().get_by_id(document_id)
        self._cache_set(cache_key, result)
        return result
    
    async def update(self, document_id: str, updates: Dict[str, Any]) -> bool:
        """Update document and invalidate cache"""
        result = await super().update(document_id, updates)
        
        # Invalidate related cache entries
        cache_key = f"get_by_id:{document_id}"
        if cache_key in self.cache:
            del self.cache[cache_key]
            del self.cache_timestamps[cache_key]
        
        return result
    
    def clear_cache(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.cache_timestamps.clear()
        self.logger.info(f"Cleared cache for {self.collection_name}")