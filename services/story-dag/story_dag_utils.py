#!/usr/bin/env python3
"""
Utility functions for Story DAG Management System
"""

import json
import uuid
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime

class StoryDAGUtils:
    """Utility functions for Story DAG operations"""
    
    @staticmethod
    def generate_sample_story() -> Dict:
        """Generate a sample story DAG structure"""
        story_id = str(uuid.uuid4())
        
        # Create nodes
        nodes = [
            {
                "node_id": "intro",
                "title": "Introduction",
                "content": "You wake up in a strange room. You don't remember how you got here.",
                "node_type": "narrative",
                "story_id": story_id,
                "tags": ["beginning", "mystery"]
            },
            {
                "node_id": "door",
                "title": "The Door",
                "content": "You approach a heavy wooden door. It appears to be locked.",
                "node_type": "choice",
                "story_id": story_id,
                "tags": ["obstacle"]
            },
            {
                "node_id": "window",
                "title": "The Window",
                "content": "You look out the window and see you're on the second floor of a building.",
                "node_type": "choice",
                "story_id": story_id,
                "tags": ["observation"]
            },
            {
                "node_id": "key",
                "title": "Found a Key",
                "content": "After searching the room, you find a rusty key under the bed.",
                "node_type": "narrative",
                "story_id": story_id,
                "tags": ["discovery", "item"]
            },
            {
                "node_id": "unlock",
                "title": "Unlock the Door",
                "content": "You use the key to unlock the door. It opens with a creak.",
                "node_type": "narrative",
                "story_id": story_id,
                "tags": ["progress"]
            },
            {
                "node_id": "hallway",
                "title": "The Hallway",
                "content": "You step into a long, dimly lit hallway.",
                "node_type": "ending",
                "story_id": story_id,
                "tags": ["transition"]
            },
            {
                "node_id": "jump",
                "title": "Jump Out",
                "content": "You decide to risk jumping out the window.",
                "node_type": "ending",
                "story_id": story_id,
                "tags": ["danger", "escape"]
            }
        ]
        
        # Create choices
        choices = [
            {
                "choice_id": "c1",
                "source_node_id": "intro",
                "target_node_id": "door",
                "text": "Examine the door",
                "story_id": story_id
            },
            {
                "choice_id": "c2",
                "source_node_id": "intro",
                "target_node_id": "window",
                "text": "Look out the window",
                "story_id": story_id
            },
            {
                "choice_id": "c3",
                "source_node_id": "door",
                "target_node_id": "key",
                "text": "Search the room",
                "story_id": story_id
            },
            {
                "choice_id": "c4",
                "source_node_id": "key",
                "target_node_id": "unlock",
                "text": "Use the key on the door",
                "story_id": story_id
            },
            {
                "choice_id": "c5",
                "source_node_id": "unlock",
                "target_node_id": "hallway",
                "text": "Step into the hallway",
                "story_id": story_id
            },
            {
                "choice_id": "c6",
                "source_node_id": "window",
                "target_node_id": "jump",
                "text": "Jump out the window",
                "story_id": story_id
            },
            {
                "choice_id": "c7",
                "source_node_id": "window",
                "target_node_id": "door",
                "text": "Go back and check the door",
                "story_id": story_id
            }
        ]
        
        return {
            "story_id": story_id,
            "title": "The Mysterious Room",
            "description": "A sample story about escaping a mysterious room.",
            "nodes": nodes,
            "choices": choices,
            "start_node_id": "intro"
        }
    
    @staticmethod
    def export_story_to_json(story_data: Dict, filepath: str) -> None:
        """Export story data to a JSON file"""
        # Convert datetime objects to strings
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        with open(filepath, 'w') as f:
            json.dump(story_data, f, default=json_serial, indent=2)
    
    @staticmethod
    def import_story_from_json(filepath: str) -> Dict:
        """Import story data from a JSON file"""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def visualize_story_dag(story_data: Dict) -> str:
        """Generate a text-based visualization of the story DAG"""
        nodes = {node["node_id"]: node for node in story_data["nodes"]}
        choices = story_data["choices"]
        
        # Build adjacency list
        adjacency = {}
        for node_id in nodes:
            adjacency[node_id] = []
        
        for choice in choices:
            source = choice["source_node_id"]
            target = choice["target_node_id"]
            text = choice["text"]
            if source in adjacency:
                adjacency[source].append((target, text))
        
        # Generate visualization
        result = [f"Story: {story_data.get('title', 'Untitled')}"]
        result.append("=" * 50)
        
        def print_node(node_id, depth=0, visited=None):
            if visited is None:
                visited = set()
            
            if node_id in visited:
                return ["  " * depth + f"[{node_id}] (already visited)"]
            
            visited.add(node_id)
            node = nodes.get(node_id, {"title": "Unknown", "node_type": "unknown"})
            node_type = node.get("node_type", "unknown")
            
            lines = ["  " * depth + f"[{node_id}] {node['title']} ({node_type})"]
            
            for target, text in adjacency.get(node_id, []):
                lines.append("  " * (depth + 1) + f"? {text}")
                lines.extend(print_node(target, depth + 2, visited.copy()))
            
            return lines
        
        start_node = story_data.get("start_node_id")
        if start_node:
            result.extend(print_node(start_node))
        else:
            # If no start node specified, print all nodes
            for node_id in nodes:
                if not any(choice["target_node_id"] == node_id for choice in choices):
                    # This is a potential root node
                    result.extend(print_node(node_id))
        
        return "\n".join(result)
    
    @staticmethod
    def analyze_story_complexity(story_data: Dict) -> Dict:
        """Analyze the complexity of a story DAG"""
        nodes = story_data["nodes"]
        choices = story_data["choices"]
        
        # Count node types
        node_types = {}
        for node in nodes:
            node_type = node.get("node_type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        # Calculate branching factor
        node_outgoing = {}
        for choice in choices:
            source = choice["source_node_id"]
            node_outgoing[source] = node_outgoing.get(source, 0) + 1
        
        avg_branching = sum(node_outgoing.values()) / len(node_outgoing) if node_outgoing else 0
        max_branching = max(node_outgoing.values()) if node_outgoing else 0
        
        # Calculate depth (longest path)
        def calculate_max_depth(start_node_id, visited=None):
            if visited is None:
                visited = set()
            
            if start_node_id in visited:
                return 0  # Cycle detected
            
            visited.add(start_node_id)
            max_depth = 0
            
            for choice in choices:
                if choice["source_node_id"] == start_node_id:
                    target = choice["target_node_id"]
                    depth = 1 + calculate_max_depth(target, visited.copy())
                    max_depth = max(max_depth, depth)
            
            return max_depth
        
        start_node = story_data.get("start_node_id")
        max_depth = calculate_max_depth(start_node) if start_node else 0
        
        return {
            "total_nodes": len(nodes),
            "total_choices": len(choices),
            "node_types": node_types,
            "average_branching_factor": round(avg_branching, 2),
            "max_branching_factor": max_branching,
            "max_depth": max_depth,
            "complexity_score": round((len(nodes) * avg_branching * max_depth) / 100, 2)
        }
    
    @staticmethod
    def validate_story_structure(story_data: Dict) -> Dict:
        """Validate the structure of a story DAG"""
        nodes = {node["node_id"]: node for node in story_data["nodes"]}
        choices = story_data["choices"]
        errors = []
        warnings = []
        
        # Check for required fields
        if "start_node_id" not in story_data:
            errors.append("Missing start_node_id")
        elif story_data["start_node_id"] not in nodes:
            errors.append(f"Start node '{story_data['start_node_id']}' not found in nodes")
        
        # Check node structure
        for node in story_data["nodes"]:
            required_fields = ["node_id", "title", "content", "node_type"]
            for field in required_fields:
                if field not in node:
                    errors.append(f"Node '{node.get('node_id', 'unknown')}' missing required field: {field}")
        
        # Check choice structure
        for choice in choices:
            required_fields = ["choice_id", "source_node_id", "target_node_id", "text"]
            for field in required_fields:
                if field not in choice:
                    errors.append(f"Choice '{choice.get('choice_id', 'unknown')}' missing required field: {field}")
            
            # Check if referenced nodes exist
            if choice.get("source_node_id") not in nodes:
                errors.append(f"Choice '{choice.get('choice_id')}' references non-existent source node: {choice.get('source_node_id')}")
            
            if choice.get("target_node_id") not in nodes:
                errors.append(f"Choice '{choice.get('choice_id')}' references non-existent target node: {choice.get('target_node_id')}")
        
        # Check for unreachable nodes
        reachable = set()
        start_node = story_data.get("start_node_id")
        
        def mark_reachable(node_id):
            if node_id in reachable:
                return
            reachable.add(node_id)
            for choice in choices:
                if choice["source_node_id"] == node_id:
                    mark_reachable(choice["target_node_id"])
        
        if start_node:
            mark_reachable(start_node)
        
        unreachable = set(nodes.keys()) - reachable
        if unreachable:
            warnings.append(f"Unreachable nodes: {list(unreachable)}")
        
        # Check for dead ends (nodes with no outgoing choices)
        nodes_with_choices = set(choice["source_node_id"] for choice in choices)
        dead_ends = set(nodes.keys()) - nodes_with_choices
        
        # Filter out ending nodes (which are expected to be dead ends)
        actual_dead_ends = [node_id for node_id in dead_ends 
                           if nodes[node_id].get("node_type") != "ending"]
        
        if actual_dead_ends:
            warnings.append(f"Non-ending nodes with no choices: {actual_dead_ends}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "reachable_nodes": len(reachable),
            "total_nodes": len(nodes)
        }

def main():
    """Demo function to show utility usage"""
    utils = StoryDAGUtils()
    
    # Generate sample story
    print("Generating sample story...")
    story = utils.generate_sample_story()
    
    # Visualize the story
    print("\nStory Visualization:")
    print(utils.visualize_story_dag(story))
    
    # Analyze complexity
    print("\nComplexity Analysis:")
    complexity = utils.analyze_story_complexity(story)
    for key, value in complexity.items():
        print(f"  {key}: {value}")
    
    # Validate structure
    print("\nStructure Validation:")
    validation = utils.validate_story_structure(story)
    print(f"  Valid: {validation['is_valid']}")
    if validation['errors']:
        print(f"  Errors: {validation['errors']}")
    if validation['warnings']:
        print(f"  Warnings: {validation['warnings']}")

if __name__ == "__main__":
    main()