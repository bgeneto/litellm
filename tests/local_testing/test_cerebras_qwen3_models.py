"""
Test for Cerebras Qwen-3 model support.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath("../.."))
import litellm


def test_cerebras_qwen3_model_support():
    """Test that the new Cerebras Qwen-3 models are properly configured."""
    
    new_models = [
        "cerebras/qwen-3-235b-a22b-instruct-2507",
        "cerebras/qwen-3-235b-a22b-thinking-2507",
        "cerebras/qwen-3-coder-480b"
    ]
    
    for model in new_models:
        # Test provider resolution
        from litellm.litellm_core_utils.get_llm_provider_logic import get_llm_provider
        model_name, provider, api_key, api_base = get_llm_provider(model=model)
        
        assert provider == "cerebras", f"Expected cerebras provider for {model}, got {provider}"
        assert api_base == "https://api.cerebras.ai/v1", f"Expected correct API base for {model}"
        
        # Test mock completion
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": "Hello"}],
            mock_response="Test response",
            max_tokens=10
        )
        
        assert response is not None
        assert response.choices[0].message.content == "Test response"
        assert model_name in response.model


def test_cerebras_qwen3_specific_capabilities():
    """Test model-specific capabilities of the new Qwen-3 models."""
    
    # Load model configuration
    import json
    with open(os.path.join(os.path.dirname(__file__), '../../model_prices_and_context_window.json'), 'r') as f:
        model_config = json.load(f)
    
    # Test thinking model has reasoning support
    thinking_model = "cerebras/qwen-3-235b-a22b-thinking-2507"
    assert thinking_model in model_config
    assert model_config[thinking_model].get('supports_reasoning') is True
    
    # Test all models have expected capabilities
    all_models = [
        "cerebras/qwen-3-235b-a22b-instruct-2507",
        "cerebras/qwen-3-235b-a22b-thinking-2507",
        "cerebras/qwen-3-coder-480b"
    ]
    
    for model in all_models:
        config = model_config[model]
        assert config['litellm_provider'] == 'cerebras'
        assert config['mode'] == 'chat'
        assert config['supports_function_calling'] is True
        assert config['supports_tool_choice'] is True
        assert config['max_tokens'] == 128000
        assert config['max_input_tokens'] == 128000
        assert config['max_output_tokens'] == 128000
        
    # Test pricing is reasonable for larger models
    instruct_config = model_config["cerebras/qwen-3-235b-a22b-instruct-2507"]
    coder_config = model_config["cerebras/qwen-3-coder-480b"]
    
    # The 480B coder model should be more expensive than the 235B instruct model
    assert coder_config['input_cost_per_token'] >= instruct_config['input_cost_per_token']
    assert coder_config['output_cost_per_token'] >= instruct_config['output_cost_per_token']