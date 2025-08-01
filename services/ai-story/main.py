# AI Story Generation Engine Service
# DeepSeek R1 integration for therapeutic story generation with Story DAG integration

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
from enum import Enum
import asyncio
import json
import uuid
import sys
import os
import time
import hashlib
import re

# Optional httpx import for external API calls
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("Warning: httpx not available, external API calls will be mocked")

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from interfaces.core_types import (
    ChapterType, StoryNode, StoryEdge, NodeType, 
    UnlockCondition, UnlockConditionType, UserStoryState
)

app = FastAPI(title="AI Story Generation Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI Story Generation Models
class StoryGenerationRequest(BaseModel):
    uid: str
    chapter_type: ChapterType
    user_context: Dict[str, Any]  # mood, tasks, progress, companion relationships
    story_state: Dict[str, Any]   # current node, choice history, flags
    generation_type: str = "continuation"  # "opening", "continuation", "choice", "ending"
    therapeutic_focus: List[str] = []  # specific therapeutic goals
    companion_context: Dict[str, Any] = {}  # companion relationships and interactions
    max_length: int = 500
    temperature: float = 0.7

class StoryGenerationResponse(BaseModel):
    story_id: str
    generated_content: str
    story_nodes: List[Dict[str, Any]] = []
    story_edges: List[Dict[str, Any]] = []
    therapeutic_tags: List[str] = []
    companion_interactions: List[Dict[str, Any]] = []
    safety_score: float
    generation_time_ms: int
    fallback_used: bool = False
    next_choices: List[Dict[str, str]] = []

class ContentSafetyResult(BaseModel):
    is_safe: bool
    safety_score: float  # 0.0 to 1.0
    flagged_categories: List[str] = []
    therapeutic_appropriateness: float  # 0.0 to 1.0
    recommendations: List[str] = []

class TherapeuticPromptTemplate(BaseModel):
    template_id: str
    chapter_type: ChapterType
    therapeutic_focus: List[str]
    prompt_template: str
    system_message: str
    safety_guidelines: List[str]
    companion_integration: Dict[str, str] = {}

# DeepSeek R1 Integration
class DeepSeekR1Client:
    def __init__(self, api_key: str = None, base_url: str = "https://api.deepseek.com/v1"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "mock_key_for_testing")
        self.base_url = base_url
        self.model = "deepseek-r1"
        self.timeout = 30.0
        
    async def generate_story(
        self, 
        prompt: str, 
        system_message: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Generate story content using DeepSeek R1"""
        
        start_time = time.time()
        
        # For development/testing, use mock response
        if self.api_key == "mock_key_for_testing":
            await asyncio.sleep(0.5)  # Simulate API delay
            return await self._mock_deepseek_response(prompt, system_message)
        
        # Real DeepSeek R1 API call
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                generation_time = int((time.time() - start_time) * 1000)
                
                return {
                    "content": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {}),
                    "generation_time_ms": generation_time,
                    "model": self.model
                }
                
        except Exception as e:
            print(f"DeepSeek R1 API error: {e}")
            # Fallback to mock response
            return await self._mock_deepseek_response(prompt, system_message)
    
    async def _mock_deepseek_response(self, prompt: str, system_message: str = None) -> Dict[str, Any]:
        """Mock DeepSeek R1 response for development/testing - ?"""
        
        # Generate contextual mock content based on prompt - ?
        if "opening" in prompt.lower() or "?" in prompt.lower():
            content = """60?

?
?

?
こ
?

?"""
        
        elif "challenge" in prompt.lower() or "?" in prompt.lower():
            content = """?

?
?60?

し
?

レベル"""
        
        elif "companion" in prompt.lower() or "?" in prompt.lower():
            content = """?

?
ユーザー

?
こ

?"""
        
        elif "level" in prompt.lower() or "成" in prompt.lower():
            content = """?

?
?

?
?
こ

60?"""
        
        else:
            content = """?

?
?

?
?
?

?"""
        
        return {
            "content": content,
            "usage": {"prompt_tokens": 100, "completion_tokens": 150, "total_tokens": 250},
            "generation_time_ms": 500,
            "model": "deepseek-r1-mock"
        }

# Initialize DeepSeek R1 client
deepseek_client = DeepSeekR1Client()

# Therapeutic Prompt Templates
class TherapeuticPromptManager:
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, TherapeuticPromptTemplate]:
        """Initialize therapeutic prompt templates for different chapters"""
        
        templates = {}
        
        # Self-Discipline Chapter - ?
        templates["self_discipline"] = TherapeuticPromptTemplate(
            template_id="self_discipline",
            chapter_type=ChapterType.SELF_DISCIPLINE,
            therapeutic_focus=["second_chance", "hero_growth", "daily_training"],
            system_message="""あ
60?
- ?
- ?
- ?
- ?
- ?
- レベル""",
            prompt_template="""?:
- 気分: {mood_level}
- ?: {task_completion_rate}
- ?: {companion_relationships}
- ?: {current_story_state}

?
?
?2-3?""",
            safety_guidelines=[
                "自動",
                "?",
                "?",
                "?"
            ],
            companion_integration={
                "yu": "?",
                "mentor": "?"
            }
        )
        
        # Empathy Chapter
        templates["empathy"] = TherapeuticPromptTemplate(
            template_id="empathy",
            chapter_type=ChapterType.EMPATHY,
            therapeutic_focus=["emotional_intelligence", "perspective_taking", "compassion"],
            system_message="""共有
- ?
- ?
- 自動
- ?""",
            prompt_template="""ユーザー:
- ?: {mood_level}
- ?: {companion_relationships}
- ?: {social_context}

共有""",
            safety_guidelines=[
                "?",
                "?",
                "?"
            ]
        )
        
        return templates
    
    def get_template(self, chapter_type: ChapterType) -> TherapeuticPromptTemplate:
        """Get therapeutic prompt template for chapter"""
        template_key = chapter_type.value
        return self.templates.get(template_key, self.templates["self_discipline"])
    
    def format_prompt(
        self, 
        template: TherapeuticPromptTemplate, 
        context: Dict[str, Any]
    ) -> str:
        """Format prompt template with user context"""
        try:
            return template.prompt_template.format(**context)
        except KeyError as e:
            # Handle missing context keys gracefully
            print(f"Missing context key: {e}")
            return template.prompt_template

prompt_manager = TherapeuticPromptManager()

# Content Safety System
class ContentSafetyFilter:
    def __init__(self):
        self.harmful_patterns = [
            "自動", "自動", "死", "消", "価",
            "?", "も", "終", "無"
        ]
        self.therapeutic_keywords = [
            "成", "希", "?", "?", "支援", "?",
            "学", "発", "?", "挑", "勇"
        ]
    
    async def evaluate_content(self, content: str) -> ContentSafetyResult:
        """Evaluate content safety and therapeutic appropriateness"""
        
        # Check for harmful patterns
        flagged_categories = []
        harmful_score = 0
        
        content_lower = content.lower()
        for pattern in self.harmful_patterns:
            if pattern in content_lower:
                flagged_categories.append("potentially_harmful")
                harmful_score += 1
        
        # Calculate therapeutic appropriateness
        therapeutic_score = 0
        for keyword in self.therapeutic_keywords:
            if keyword in content_lower:
                therapeutic_score += 1
        
        # Normalize scores
        safety_score = max(0.0, 1.0 - (harmful_score / len(self.harmful_patterns)))
        therapeutic_appropriateness = min(1.0, therapeutic_score / 5.0)
        
        # Determine overall safety
        is_safe = safety_score >= 0.8 and len(flagged_categories) == 0
        
        recommendations = []
        if not is_safe:
            recommendations.append("コア")
        if therapeutic_appropriateness < 0.5:
            recommendations.append("?")
        
        return ContentSafetyResult(
            is_safe=is_safe,
            safety_score=safety_score,
            flagged_categories=flagged_categories,
            therapeutic_appropriateness=therapeutic_appropriateness,
            recommendations=recommendations
        )

safety_filter = ContentSafetyFilter()

# Fallback Template System
class FallbackTemplateSystem:
    def __init__(self):
        self.templates = self._initialize_fallback_templates()
    
    def _initialize_fallback_templates(self) -> Dict[str, List[str]]:
        """Initialize fallback story templates - ?"""
        return {
            "opening": [
                "?",
                "?",
                "?60?"
            ],
            "challenge": [
                "?",
                "?",
                "?"
            ],
            "companion": [
                "?",
                "?",
                "共有"
            ],
            "reflection": [
                "?",
                "?",
                "?"
            ],
            "level_up": [
                "?",
                "?60?",
                "?"
            ]
        }
    
    def get_fallback_content(self, generation_type: str, context: Dict[str, Any] = None) -> str:
        """Get fallback story content"""
        templates = self.templates.get(generation_type, self.templates["opening"])
        
        # Simple selection based on context or random
        if context and "mood_level" in context:
            mood = context["mood_level"]
            if mood >= 4:
                return templates[0] if len(templates) > 0 else "物語"
            elif mood <= 2:
                return templates[-1] if len(templates) > 0 else "?"
        
        return templates[0] if templates else "あ"

fallback_system = FallbackTemplateSystem()

# Mock database for development
class StoryGenerationDatabase:
    def __init__(self):
        self.generation_history: Dict[str, List[StoryGenerationResponse]] = {}
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        self.performance_metrics: List[Dict[str, Any]] = []

story_db = StoryGenerationDatabase()

# Authentication
async def verify_jwt_token() -> dict:
    """Mock JWT verification for testing purposes"""
    return {"uid": "test_user_123", "email": "test@example.com"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-story"}

# Story Generation Endpoints
@app.post("/ai/story/v2/generate", response_model=StoryGenerationResponse)
async def generate_story(
    request: StoryGenerationRequest,
    current_user: dict = Depends(verify_jwt_token),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Generate therapeutic story content using DeepSeek R1"""
    
    start_time = time.time()
    story_id = str(uuid.uuid4())
    
    try:
        # Get therapeutic prompt template
        template = prompt_manager.get_template(request.chapter_type)
        
        # Format context for prompt
        context = {
            "mood_level": request.user_context.get("mood_score", 3),
            "task_completion_rate": request.user_context.get("completion_rate", 0.5),
            "companion_relationships": request.companion_context,
            "current_story_state": request.story_state,
            "social_context": request.user_context.get("social_interactions", {})
        }
        
        # Generate prompt
        formatted_prompt = prompt_manager.format_prompt(template, context)
        
        # Call DeepSeek R1
        ai_response = await deepseek_client.generate_story(
            prompt=formatted_prompt,
            system_message=template.system_message,
            temperature=request.temperature,
            max_tokens=request.max_length
        )
        
        generated_content = ai_response["content"]
        
        # Content safety check
        safety_result = await safety_filter.evaluate_content(generated_content)
        
        # Use fallback if content is not safe
        fallback_used = False
        if not safety_result.is_safe:
            generated_content = fallback_system.get_fallback_content(
                request.generation_type, 
                request.user_context
            )
            fallback_used = True
            safety_result = await safety_filter.evaluate_content(generated_content)
        
        # Extract story elements (simplified for now)
        story_nodes, story_edges = await extract_story_elements(generated_content, request)
        
        # Generate next choices
        next_choices = await generate_next_choices(generated_content, request)
        
        generation_time = int((time.time() - start_time) * 1000)
        
        # Create response
        response = StoryGenerationResponse(
            story_id=story_id,
            generated_content=generated_content,
            story_nodes=story_nodes,
            story_edges=story_edges,
            therapeutic_tags=template.therapeutic_focus,
            companion_interactions=await extract_companion_interactions(generated_content),
            safety_score=safety_result.safety_score,
            generation_time_ms=generation_time,
            fallback_used=fallback_used,
            next_choices=next_choices
        )
        
        # Store generation history
        if request.uid not in story_db.generation_history:
            story_db.generation_history[request.uid] = []
        story_db.generation_history[request.uid].append(response)
        
        # Log performance metrics
        background_tasks.add_task(log_performance_metrics, {
            "generation_time_ms": generation_time,
            "content_length": len(generated_content),
            "safety_score": safety_result.safety_score,
            "fallback_used": fallback_used,
            "chapter_type": request.chapter_type.value
        })
        
        return response
        
    except Exception as e:
        print(f"Story generation error: {e}")
        
        # Emergency fallback
        fallback_content = fallback_system.get_fallback_content(
            request.generation_type,
            request.user_context
        )
        
        safety_result = await safety_filter.evaluate_content(fallback_content)
        generation_time = int((time.time() - start_time) * 1000)
        
        return StoryGenerationResponse(
            story_id=story_id,
            generated_content=fallback_content,
            therapeutic_tags=["resilience", "hope"],
            safety_score=safety_result.safety_score,
            generation_time_ms=generation_time,
            fallback_used=True,
            next_choices=[
                {"choice_id": "continue", "choice_text": "物語"},
                {"choice_id": "reflect", "choice_text": "?"}
            ]
        )

# Story DAG Integration
class StoryDAGIntegration:
    def __init__(self):
        self.story_dag_base_url = os.getenv("STORY_DAG_URL", "http://localhost:8005")
    
    async def create_story_nodes_and_edges(
        self, 
        generated_content: str, 
        request: StoryGenerationRequest,
        next_choices: List[Dict[str, str]]
    ) -> tuple[List[Dict], List[Dict]]:
        """Create story nodes and edges in Story DAG system"""
        
        story_nodes = []
        story_edges = []
        
        try:
            # Extract chapter ID from story state
            chapter_id = request.story_state.get("current_chapter_id", f"{request.chapter_type.value}_ch1")
            
            # Create main story node
            main_node = await self._create_story_node(
                chapter_id=chapter_id,
                node_type=self._map_generation_type_to_node_type(request.generation_type),
                title=self._extract_title_from_content(generated_content),
                content=generated_content,
                therapeutic_tags=request.therapeutic_focus,
                companion_effects=self._extract_companion_effects(generated_content),
                mood_effects=self._extract_mood_effects(generated_content, request),
                unlock_conditions=self._generate_unlock_conditions(request)
            )
            
            if main_node:
                story_nodes.append(main_node)
                
                # Create choice nodes and edges for next choices
                current_node_id = main_node["node_id"]
                
                for choice in next_choices:
                    choice_node = await self._create_choice_node(
                        chapter_id=chapter_id,
                        choice_data=choice,
                        request=request
                    )
                    
                    if choice_node:
                        story_nodes.append(choice_node)
                        
                        # Create edge connecting main node to choice node
                        edge = await self._create_story_edge(
                            from_node_id=current_node_id,
                            to_node_id=choice_node["node_id"],
                            choice_text=choice["choice_text"],
                            real_task_id=choice.get("real_task_id"),
                            habit_tag=choice.get("habit_tag"),
                            therapeutic_weight=self._calculate_therapeutic_weight(choice, request)
                        )
                        
                        if edge:
                            story_edges.append(edge)
            
        except Exception as e:
            print(f"Story DAG integration error: {e}")
            # Return simplified structure on error
            story_nodes = [{
                "node_id": str(uuid.uuid4()),
                "chapter_type": request.chapter_type.value,
                "node_type": request.generation_type,
                "title": "Generated Story Segment",
                "content": generated_content[:200] + "..." if len(generated_content) > 200 else generated_content,
                "therapeutic_tags": request.therapeutic_focus
            }]
        
        return story_nodes, story_edges
    
    async def _create_story_node(
        self,
        chapter_id: str,
        node_type: NodeType,
        title: str,
        content: str,
        therapeutic_tags: List[str],
        companion_effects: Dict[str, int],
        mood_effects: Dict[str, float],
        unlock_conditions: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Create a story node via Story DAG API"""
        
        node_data = {
            "chapter_id": chapter_id,
            "node_type": node_type.value,
            "title": title,
            "content": content,
            "estimated_read_time": max(1, len(content) // 100),  # Rough estimate
            "therapeutic_tags": therapeutic_tags,
            "unlock_conditions": unlock_conditions,
            "companion_effects": companion_effects,
            "mood_effects": mood_effects,
            "ending_flags": {}
        }
        
        if not HTTPX_AVAILABLE:
            # Mock response when httpx is not available
            return {
                "node_id": str(uuid.uuid4()),
                "chapter_id": chapter_id,
                "node_type": node_type.value,
                "title": title,
                "content": content,
                "therapeutic_tags": therapeutic_tags
            }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.story_dag_base_url}/nodes",
                    json=node_data,
                    headers={"Authorization": "Bearer mock_token"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "node_id": result["node_id"],
                        "chapter_id": chapter_id,
                        "node_type": node_type.value,
                        "title": title,
                        "content": content,
                        "therapeutic_tags": therapeutic_tags
                    }
        except Exception as e:
            print(f"Failed to create story node: {e}")
        
        return None
    
    async def _create_choice_node(
        self,
        chapter_id: str,
        choice_data: Dict[str, str],
        request: StoryGenerationRequest
    ) -> Optional[Dict[str, Any]]:
        """Create a choice node for user selection"""
        
        choice_content = f"?: {choice_data['choice_text']}\n\nこ"
        
        return await self._create_story_node(
            chapter_id=chapter_id,
            node_type=NodeType.CHOICE,
            title=f"?: {choice_data['choice_text']}",
            content=choice_content,
            therapeutic_tags=request.therapeutic_focus,
            companion_effects={},
            mood_effects={},
            unlock_conditions=[]
        )
    
    async def _create_story_edge(
        self,
        from_node_id: str,
        to_node_id: str,
        choice_text: str,
        real_task_id: Optional[str] = None,
        habit_tag: Optional[str] = None,
        therapeutic_weight: float = 1.0
    ) -> Optional[Dict[str, Any]]:
        """Create a story edge via Story DAG API"""
        
        edge_data = {
            "from_node_id": from_node_id,
            "to_node_id": to_node_id,
            "choice_text": choice_text,
            "real_task_id": real_task_id,
            "habit_tag": habit_tag,
            "probability": 1.0,
            "therapeutic_weight": therapeutic_weight,
            "companion_requirements": {},
            "achievement_rewards": [],
            "ending_influence": {}
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.story_dag_base_url}/edges",
                    json=edge_data,
                    headers={"Authorization": "Bearer mock_token"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "edge_id": result["edge_id"],
                        "from_node_id": from_node_id,
                        "to_node_id": to_node_id,
                        "choice_text": choice_text,
                        "real_task_id": real_task_id,
                        "habit_tag": habit_tag,
                        "therapeutic_weight": therapeutic_weight
                    }
        except Exception as e:
            print(f"Failed to create story edge: {e}")
        
        return None
    
    def _map_generation_type_to_node_type(self, generation_type: str) -> NodeType:
        """Map generation type to Story DAG node type"""
        mapping = {
            "opening": NodeType.OPENING,
            "challenge": NodeType.CHALLENGE,
            "choice": NodeType.CHOICE,
            "resolution": NodeType.RESOLUTION,
            "reflection": NodeType.REFLECTION,
            "companion": NodeType.COMPANION_INTRO,
            "ending": NodeType.ENDING
        }
        return mapping.get(generation_type, NodeType.CHOICE)
    
    def _extract_title_from_content(self, content: str) -> str:
        """Extract a suitable title from generated content"""
        lines = content.split('\n')
        first_line = lines[0].strip()
        
        # If first line is short and descriptive, use it as title
        if len(first_line) <= 50 and first_line:
            return first_line
        
        # Otherwise, create a generic title
        return "物語"
    
    def _extract_companion_effects(self, content: str) -> Dict[str, int]:
        """Extract companion relationship effects from content"""
        effects = {}
        
        # Simple pattern matching for companion mentions
        if "ユーザー" in content:
            # Positive mentions increase relationship
            if any(word in content for word in ["?", "?", "支援", "一般", "?"]):
                effects["yu"] = 10
            else:
                effects["yu"] = 5
        
        if "?" in content or "?" in content:
            effects["mentor"] = 8
        
        return effects
    
    def _extract_mood_effects(self, content: str, request: StoryGenerationRequest) -> Dict[str, float]:
        """Extract mood effects from content"""
        effects = {}
        
        # Positive mood indicators
        positive_words = ["希", "成", "?", "?", "?", "?", "?"]
        negative_words = ["?", "挑", "?", "?"]
        
        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        
        if positive_count > negative_count:
            effects["hope"] = 0.1
            effects["confidence"] = 0.05
        elif negative_count > 0:
            effects["determination"] = 0.1  # Challenges can build determination
        
        return effects
    
    def _generate_unlock_conditions(self, request: StoryGenerationRequest) -> List[Dict[str, Any]]:
        """Generate unlock conditions based on request context"""
        conditions = []
        
        # Add task completion conditions if user has pending tasks
        if request.user_context.get("pending_tasks", 0) > 0:
            conditions.append({
                "condition_type": UnlockConditionType.TASK_COMPLETION.value,
                "parameters": {"min_tasks": 1},
                "required": False
            })
        
        # Add mood threshold for certain content types
        if request.generation_type in ["challenge", "resolution"]:
            conditions.append({
                "condition_type": UnlockConditionType.MOOD_THRESHOLD.value,
                "parameters": {"mood_score": 2},
                "required": False
            })
        
        return conditions
    
    def _calculate_therapeutic_weight(self, choice: Dict[str, str], request: StoryGenerationRequest) -> float:
        """Calculate therapeutic weight for story edge"""
        base_weight = 1.0
        
        # Increase weight for choices that align with therapeutic focus
        choice_text = choice["choice_text"].lower()
        
        for focus in request.therapeutic_focus:
            if focus in ["habit_formation", "self_control"] and any(word in choice_text for word in ["挑", "?", "?"]):
                base_weight += 0.3
            elif focus in ["emotional_intelligence", "empathy"] and any(word in choice_text for word in ["理", "共有", "つ"]):
                base_weight += 0.3
        
        return min(2.0, base_weight)  # Cap at 2.0

# Initialize Story DAG integration
story_dag_integration = StoryDAGIntegration()

# Initialize Story DAG integration
story_dag_integration = StoryDAGIntegration()

async def extract_story_elements(content: str, request: StoryGenerationRequest) -> tuple[List[Dict], List[Dict]]:
    """Extract story nodes and edges from generated content with DAG integration"""
    
    # Generate next choices first
    next_choices = await generate_next_choices(content, request)
    
    # Use Story DAG integration to create nodes and edges
    return await story_dag_integration.create_story_nodes_and_edges(
        generated_content=content,
        request=request,
        next_choices=next_choices
    )

async def generate_next_choices(content: str, request: StoryGenerationRequest) -> List[Dict[str, str]]:
    """Generate contextual next choices based on content"""
    
    # Simplified choice generation
    # In a full implementation, this would analyze the content to generate relevant choices
    
    base_choices = [
        {"choice_id": "continue", "choice_text": "物語"},
        {"choice_id": "reflect", "choice_text": "?"}
    ]
    
    # Add chapter-specific choices
    if request.chapter_type == ChapterType.SELF_DISCIPLINE:
        base_choices.append({"choice_id": "challenge", "choice_text": "?"})
    elif request.chapter_type == ChapterType.EMPATHY:
        base_choices.append({"choice_id": "connect", "choice_text": "?"})
    
    return base_choices

async def extract_companion_interactions(content: str) -> List[Dict[str, Any]]:
    """Extract companion interactions from generated content"""
    
    interactions = []
    
    # Simple pattern matching for companion mentions
    if "ユーザー" in content:
        interactions.append({
            "companion_id": "yu",
            "interaction_type": "dialogue",
            "content": "ユーザー",
            "relationship_impact": 5
        })
    
    return interactions

async def log_performance_metrics(metrics: Dict[str, Any]):
    """Log performance metrics for monitoring"""
    metrics["timestamp"] = datetime.utcnow().isoformat()
    story_db.performance_metrics.append(metrics)
    
    # Keep only recent metrics (last 1000)
    if len(story_db.performance_metrics) > 1000:
        story_db.performance_metrics = story_db.performance_metrics[-1000:]

# Content Safety Endpoints
@app.post("/ai/story/safety/evaluate", response_model=ContentSafetyResult)
async def evaluate_content_safety(
    content: Dict[str, str],
    current_user: dict = Depends(verify_jwt_token)
):
    """Evaluate content safety and therapeutic appropriateness"""
    
    text_content = content.get("content", "")
    return await safety_filter.evaluate_content(text_content)

# Template Management
@app.get("/ai/story/templates")
async def list_prompt_templates(
    current_user: dict = Depends(verify_jwt_token)
):
    """List available therapeutic prompt templates"""
    
    return {
        "templates": [
            {
                "template_id": template.template_id,
                "chapter_type": template.chapter_type,
                "therapeutic_focus": template.therapeutic_focus,
                "safety_guidelines": template.safety_guidelines
            }
            for template in prompt_manager.templates.values()
        ]
    }

# Performance Monitoring
@app.get("/ai/story/metrics")
async def get_performance_metrics(
    current_user: dict = Depends(verify_jwt_token)
):
    """Get AI story generation performance metrics"""
    
    if not story_db.performance_metrics:
        return {"message": "No metrics available"}
    
    recent_metrics = story_db.performance_metrics[-100:]  # Last 100 generations
    
    avg_generation_time = sum(m["generation_time_ms"] for m in recent_metrics) / len(recent_metrics)
    avg_safety_score = sum(m["safety_score"] for m in recent_metrics) / len(recent_metrics)
    fallback_rate = sum(1 for m in recent_metrics if m["fallback_used"]) / len(recent_metrics)
    
    return {
        "total_generations": len(story_db.performance_metrics),
        "recent_generations": len(recent_metrics),
        "average_generation_time_ms": avg_generation_time,
        "average_safety_score": avg_safety_score,
        "fallback_usage_rate": fallback_rate,
        "p95_latency_requirement": 3500,  # 3.5 seconds
        "p95_latency_actual": max(m["generation_time_ms"] for m in recent_metrics[-20:]) if recent_metrics else 0
    }

# Real-time Story Generation for Daily Events
@app.post("/ai/story/v2/daily-generation")
async def generate_daily_story(
    daily_context: Dict[str, Any],
    current_user: dict = Depends(verify_jwt_token),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Generate daily story content based on user's task completion and mood (21:30 trigger)"""
    
    uid = daily_context.get("uid")
    if not uid:
        raise HTTPException(status_code=400, detail="User ID required")
    
    # Extract daily context
    completed_tasks = daily_context.get("completed_tasks", [])
    mood_score = daily_context.get("mood_score", 3)
    task_completion_rate = daily_context.get("completion_rate", 0.0)
    current_chapter = daily_context.get("current_chapter", ChapterType.SELF_DISCIPLINE)
    companion_relationships = daily_context.get("companion_relationships", {})
    
    # Determine story generation type based on performance
    if task_completion_rate >= 0.8:
        generation_type = "achievement"
    elif task_completion_rate >= 0.5:
        generation_type = "progress"
    elif task_completion_rate >= 0.2:
        generation_type = "encouragement"
    else:
        generation_type = "support"
    
    # Create story generation request
    request = StoryGenerationRequest(
        uid=uid,
        chapter_type=current_chapter,
        user_context={
            "mood_score": mood_score,
            "completion_rate": task_completion_rate,
            "completed_tasks": len(completed_tasks),
            "daily_performance": generation_type
        },
        story_state=daily_context.get("story_state", {}),
        generation_type=generation_type,
        therapeutic_focus=["daily_reflection", "progress_recognition", "motivation"],
        companion_context=companion_relationships,
        temperature=0.8  # Slightly higher for more creative daily stories
    )
    
    # Generate story
    story_response = await generate_story(request, current_user, background_tasks)
    
    # Add daily-specific metadata
    story_response.story_id = f"daily_{datetime.utcnow().strftime('%Y%m%d')}_{story_response.story_id}"
    
    return {
        "daily_story": story_response,
        "generation_trigger": "daily_21_30",
        "performance_category": generation_type,
        "next_day_suggestions": await generate_next_day_suggestions(completed_tasks, mood_score)
    }

async def generate_next_day_suggestions(completed_tasks: List[Dict], mood_score: int) -> List[Dict[str, str]]:
    """Generate suggestions for tomorrow's tasks based on today's performance"""
    
    suggestions = []
    
    # Analyze task patterns
    task_types = [task.get("type", "routine") for task in completed_tasks]
    
    if "social" not in task_types:
        suggestions.append({
            "type": "social",
            "suggestion": "?",
            "real_task_hint": "?"
        })
    
    if mood_score <= 2:
        suggestions.append({
            "type": "self_care",
            "suggestion": "?",
            "real_task_hint": "?"
        })
    
    if len(completed_tasks) == 0:
        suggestions.append({
            "type": "small_step",
            "suggestion": "?",
            "real_task_hint": "5?"
        })
    
    return suggestions

# Task-Story Integration
@app.post("/ai/story/v2/task-completion-story")
async def generate_task_completion_story(
    task_completion_data: Dict[str, Any],
    current_user: dict = Depends(verify_jwt_token)
):
    """Generate story content when user completes a task"""
    
    uid = task_completion_data.get("uid")
    task_data = task_completion_data.get("task", {})
    completion_context = task_completion_data.get("context", {})
    
    # Determine story focus based on task type
    task_type = task_data.get("type", "routine")
    difficulty = task_data.get("difficulty", 1)
    
    therapeutic_focus = []
    if task_type == "routine":
        therapeutic_focus = ["habit_formation", "consistency"]
    elif task_type == "social":
        therapeutic_focus = ["social_connection", "empathy"]
    elif task_type == "skill_up":
        therapeutic_focus = ["growth_mindset", "learning"]
    else:
        therapeutic_focus = ["achievement", "self_efficacy"]
    
    # Create contextual story request
    request = StoryGenerationRequest(
        uid=uid,
        chapter_type=completion_context.get("current_chapter", ChapterType.SELF_DISCIPLINE),
        user_context={
            "task_completed": task_data,
            "difficulty_level": difficulty,
            "completion_mood": completion_context.get("mood_after", 3)
        },
        story_state=completion_context.get("story_state", {}),
        generation_type="task_completion",
        therapeutic_focus=therapeutic_focus,
        companion_context=completion_context.get("companion_relationships", {}),
        max_length=300,  # Shorter for task completion stories
        temperature=0.6
    )
    
    return await generate_story(request, current_user, BackgroundTasks())

# Story Choice Integration with Real Tasks
@app.post("/ai/story/v2/choice-to-task")
async def convert_story_choice_to_task(
    choice_data: Dict[str, Any],
    current_user: dict = Depends(verify_jwt_token)
):
    """Convert a story choice into a real-world task suggestion"""
    
    choice_text = choice_data.get("choice_text", "")
    story_context = choice_data.get("story_context", {})
    user_context = choice_data.get("user_context", {})
    
    # Analyze choice to suggest real task
    task_suggestion = await analyze_choice_for_task_creation(
        choice_text, 
        story_context, 
        user_context
    )
    
    return {
        "story_choice": choice_text,
        "suggested_task": task_suggestion,
        "integration_type": "choice_to_action",
        "therapeutic_rationale": task_suggestion.get("rationale", "")
    }

async def analyze_choice_for_task_creation(
    choice_text: str, 
    story_context: Dict[str, Any], 
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze story choice to create meaningful real-world task"""
    
    choice_lower = choice_text.lower()
    
    # Pattern matching for task creation
    if any(word in choice_lower for word in ["挑", "?", "?"]):
        return {
            "type": "skill_up",
            "title": "?",
            "description": f"ストーリー{choice_text}?",
            "difficulty": 3,
            "estimated_time": 30,
            "rationale": "物語"
        }
    
    elif any(word in choice_lower for word in ["つ", "?", "コア"]):
        return {
            "type": "social",
            "title": "誰",
            "description": f"物語",
            "difficulty": 2,
            "estimated_time": 15,
            "rationale": "ストーリー"
        }
    
    elif any(word in choice_lower for word in ["?", "?", "?"]):
        return {
            "type": "routine",
            "title": "?",
            "description": f"物語",
            "difficulty": 1,
            "estimated_time": 10,
            "rationale": "ストーリー"
        }
    
    else:
        return {
            "type": "one_shot",
            "title": "物語",
            "description": f"?{choice_text}?",
            "difficulty": 2,
            "estimated_time": 20,
            "rationale": "物語"
        }

# User Story History
@app.get("/ai/story/history/{uid}")
async def get_user_story_history(
    uid: str,
    limit: int = 10,
    current_user: dict = Depends(verify_jwt_token)
):
    """Get user's story generation history"""
    
    if current_user["uid"] != uid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    history = story_db.generation_history.get(uid, [])
    
    return {
        "uid": uid,
        "total_generations": len(history),
        "recent_stories": [
            {
                "story_id": story.story_id,
                "generated_content": story.generated_content[:100] + "..." if len(story.generated_content) > 100 else story.generated_content,
                "therapeutic_tags": story.therapeutic_tags,
                "safety_score": story.safety_score,
                "generation_time_ms": story.generation_time_ms,
                "fallback_used": story.fallback_used
            }
            for story in history[-limit:]
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)