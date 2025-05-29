```python
import pytest
from shared.agents.agent_base import AgentBase
from shared.agents.cortexa_agent import CortexaAgent
from shared.agents.daphne_agent import DaphneAgent

def test_agent_base():
    """Test AgentBase class functionality"""
    agent = AgentBase("TestAgent")
    agent.set_context("test_key", "test_value")
    assert agent.get_context("test_key") == "test_value"
    
    with pytest.raises(NotImplementedError):
        agent.ask("test prompt")
    
    with pytest.raises(NotImplementedError):
        agent.respond("test input")

@pytest.mark.asyncio
async def test_cortexa_agent():
    """Test CortexaAgent specific functionality"""
    agent = CortexaAgent()
    
    # Test plugin detection
    plugin_match = agent._detect_plugin_trigger("run plugin calculator on 2+2")
    assert plugin_match == ("calculator", "2+2")
    
    # Test response generation
    response = agent.respond("predict market trends")
    assert "Cortexa predicts" in response
    assert "confidence" in response

@pytest.mark.asyncio
async def test_daphne_agent():
    """Test DaphneAgent specific functionality"""
    agent = DaphneAgent()
    
    # Test mood-based responses
    response = agent.respond("hello")
    assert "👋" in response
    assert "Daphne" in response
    
    response = agent.respond("status")
    assert "🧠" in response
    assert "System" in response

@pytest.mark.asyncio
async def test_agent_chain():
    """Test agent chain execution"""
    from shared.workflows.agent_chain_executor import execute_agent_chain
    
    chain = ["cortexa", "daphne"]
    prompt = "Test prompt"
    
    results = execute_agent_chain(chain, prompt)
    assert len(results) == 2
    assert all("agent" in step and "output" in step for step in results)
```