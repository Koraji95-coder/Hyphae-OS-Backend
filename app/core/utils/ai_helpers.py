"""AI Utilities 🤖
────────────────────────────────────────────
Helper functions for AI-related operations.

This module provides utilities for:
- Text preprocessing and normalization
- LLM prompt optimization and formatting
- Response parsing and extraction
- Token counting and optimization
- Model performance monitoring
"""

import re
from typing import Dict, Any, List, Optional, Union
import time

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Estimate token count for a given text and model.
    
    Args:
        text (str): Text to analyze
        model (str): Model name to estimate tokens for
        
    Returns:
        int: Estimated token count
    """
    # Simple estimation: ~4 chars per token for English text
    # In production, would use tiktoken or similar
    return len(text) // 4

def format_system_prompt(template: str, variables: Dict[str, str]) -> str:
    """Format a system prompt template with variables.
    
    Args:
        template (str): Prompt template with {variable} placeholders
        variables (Dict[str, str]): Values to insert into template
        
    Returns:
        str: Formatted prompt
    """
    return template.format(**variables)

def extract_json_from_response(response: str) -> Dict[str, Any]:
    """Extract JSON object from an LLM response text.
    
    Args:
        response (str): LLM response text
        
    Returns:
        Dict[str, Any]: Extracted JSON object or empty dict if not found
        
    Raises:
        ValueError: If invalid JSON is found
    """
    # Find content between JSON markers or code blocks
    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    matches = re.findall(json_pattern, response)
    
    if matches:
        import json
        try:
            return json.loads(matches[0])
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {e}")
    
    return {}

def truncate_text(text: str, max_tokens: int, model: str = "gpt-4") -> str:
    """Truncate text to fit within token limit.
    
    Args:
        text (str): Text to truncate
        max_tokens (int): Maximum tokens allowed
        model (str): Model name for token estimation
        
    Returns:
        str: Truncated text
    """
    current_tokens = count_tokens(text, model)
    
    if current_tokens <= max_tokens:
        return text
        
    # Simple truncation by ratio
    ratio = max_tokens / current_tokens
    char_limit = int(len(text) * ratio)
    
    # Try to truncate at sentence boundary
    truncated = text[:char_limit]
    last_period = truncated.rfind('.')
    
    if last_period > 0:
        return truncated[:last_period + 1] + " [truncated]"
    else:
        return truncated + " [truncated]"

def measure_response_time(func):
    """Decorator to measure LLM response time.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with timing
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        
        # Log timing information
        import logging
        logger = logging.getLogger("ai_timing")
        logger.info(f"LLM response time: {elapsed_time:.2f}s")
        
        return result
    return wrapper