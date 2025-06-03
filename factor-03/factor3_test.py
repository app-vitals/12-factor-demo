#!/usr/bin/env python3
"""
Factor 3 Quality Comparison - Refactored
Tests whether structured context actually improves response quality
Measures specificity, accuracy, and actionability of responses
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

import litellm
from langfuse.decorators import observe

# Import our modular components
from models import load_test_scenarios
from formatters import FORMATS, get_available_formats
from evaluation import test_model_and_evaluate, EVALUATION_MODELS
from analysis import generate_comprehensive_summary, analyze_results_by_models

# Configure LiteLLM for multi-provider compatibility
litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"]
litellm.modify_params = True  # Critical for Anthropic tool call compatibility

load_dotenv()


def validate_api_keys():
    """Ensure all required API keys are configured"""
    required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    print(f"✅ All APIs configured: OpenAI, Anthropic, Gemini")


def run_format_test(format_name: str, format_func, scenario):
    """
    Test a specific format across all models
    
    Args:
        format_name: Display name for the format
        format_func: Function to apply the format
        scenario: Test scenario to format and test
        
    Returns:
        Dict mapping model names to test results
    """
    print(f"\n{'='*60}")
    print(f"Testing: {format_name}")
    print(f"{'='*60}")
    
    messages = format_func(scenario)
    results = {}
    
    # Test all models using unified interface
    model_configs = [
        ("gpt-4.1", "GPT-4.1", EVALUATION_MODELS["gpt-4.1"]),
        ("sonnet-4", "Sonnet 4", EVALUATION_MODELS["sonnet-4"]),
        ("gemini-2.5", "Gemini 2.5", EVALUATION_MODELS["gemini-2.5"])
    ]
    
    for model_key, model_name, model_id in model_configs:
        result = test_model_and_evaluate(
            messages, model_key, model_name, model_id, scenario, format_name
        )
        results[model_key] = result
    
    return results


def main():
    """Run the Factor 3 quality comparison test"""
    print("🧪 FACTOR 3 QUALITY COMPARISON")
    print("Testing whether structured context actually improves response quality")
    print("Models: GPT-4.1, Sonnet 4, Gemini 2.5")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Validate environment
    validate_api_keys()
    
    # Load test scenarios
    scenarios = load_test_scenarios()
    
    # Get available formats
    available_formats = get_available_formats()
    
    # Calculate test counts
    num_models = len(EVALUATION_MODELS)
    total_tests = len(scenarios) * len(available_formats) * num_models
    test_count = 0
    
    print(f"\n🎯 Running {total_tests} total tests across {len(scenarios)} scenarios...")
    print(f"📋 Formats: {', '.join(available_formats)}")
    
    # Run all tests
    all_results = {}
    
    for scenario in scenarios:
        print(f"\n{'='*80}")
        print(f"SCENARIO: {scenario.name}")
        print(f"{'='*80}")
        
        scenario_results = {}
        
        for format_name in available_formats:
            format_func = FORMATS[format_name]
            results = run_format_test(format_name, format_func, scenario)
            scenario_results[format_name] = results
            test_count += len(results)
        
        all_results[scenario.name] = scenario_results
    
    # Save results with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"factor3_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Generate comprehensive analysis
    generate_comprehensive_summary(all_results)
    
    print(f"\n💾 Results saved to: {filename}")
    
    # Run model comparison analysis
    analyze_results_by_models(all_results)


if __name__ == "__main__":
    main()
