"""Schema Template Definition 📁
────────────────────────────────────────────
This module defines the recommended file structure
and coding patterns for the AI agent system.

File naming and organization guidelines:
1. Use snake_case for filenames
2. Group related functionality in directories
3. Follow consistent header formats
4. Use type hints consistently
5. Document all public interfaces
"""

"""
Recommended Project Structure
============================

backend/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_llm_agent.py
│   │   ├── mycocore_agent.py
│   │   ├── neuroweave_agent.py
│   │   ├── rootbloom_agent.py
│   │   └── sporelink_agent.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── endpoints/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logger.py
│   └── services/
│       ├── __init__.py
│       └── auth_service.py
├── shared/
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── gpt_client.py
│   │   └── mood_engine.py
│   ├── memory/
│   │   ├── __init__.py
│   │   └── memory_router.py
│   └── state/
│       ├── __init__.py
│       ├── session_manager.py
│       └── mood_state_tracker.py
└── tests/
    ├── unit/
    │   └── test_agents.py
    └── integration/
        └── test_api.py

"""

# Standard header format for all files
STANDARD_HEADER = '''"""[ModuleName] [Emoji]
────────────────────────────────────────────
[Brief description of module purpose]

This module [provides/handles/manages] [key functionality]:
- [Bullet point for key responsibility 1]
- [Bullet point for key responsibility 2]
- [Bullet point for key responsibility 3]
- [Bullet point for key responsibility 4]
- [Bullet point for key responsibility 5]

[Additional context or important notes about usage]
"""'''

# Example standard class documentation format
STANDARD_CLASS_DOC = '''"""[Brief class description]
    
    This class [provides/handles/manages] [key functionality],
    [additional context or important implementation details].
    
    Attributes:
        [attr1] ([type]): [Description]
        [attr2] ([type]): [Description]
    """'''

# Example standard method documentation format
STANDARD_METHOD_DOC = '''"""[Brief method description]
        
        [Additional explanation if needed]
        
        Args:
            [arg1] ([type]): [Description]
            [arg2] ([type], optional): [Description]. Defaults to [default].
            
        Returns:
            [return_type]: [Description of return value]
            
        Raises:
            [exception_type]: [When this exception is raised]
        """'''