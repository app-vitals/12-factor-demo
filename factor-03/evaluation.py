"""
Quality evaluation functions for Factor 3 testing
Uses multi-model evaluation to eliminate single-model bias
"""

import time
import litellm
from typing import Dict, List
from langfuse.decorators import observe, langfuse_context
from models import Scenario

# Latest model versions - LiteLLM format
EVALUATION_MODELS = {
    "gpt-4.1": "gpt-4.1-2025-04-14",
    "sonnet-4": "claude-sonnet-4-20250514", 
    "gemini-2.5": "gemini/gemini-2.5-pro-preview-05-06"
}


def test_model(messages: List[Dict], model: str) -> Dict:
    """
    Test a single model with given messages
    
    Args:
        messages: Conversation messages to send to model
        model: Model identifier for LiteLLM
    
    Returns:
        Dict with response, token counts, cost, and timing
    """
    start_time = time.time()
    
    response = litellm.completion(
        model=model,
        messages=messages,
        max_tokens=16384,
        temperature=0.1,
        metadata={
            # Nest LiteLLM calls under current Langfuse trace
            "existing_trace_id": langfuse_context.get_current_trace_id(),
            "parent_observation_id": langfuse_context.get_current_observation_id(),
        },
    )
    
    end_time = time.time()
    
    return {
        "response": response.choices[0].message.content,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        "time": end_time - start_time,
        # LiteLLM automatically calculates accurate costs
        "cost": litellm.completion_cost(completion_response=response)
    }


def _parse_evaluation_scores(scores_text: str) -> Dict[str, float]:
    """
    Parse evaluation scores from model response text
    
    Expected format: "specificity:0.X personalization:0.X actionability:0.X context_utilization:0.X overall:0.X"
    
    Args:
        scores_text: Raw text response from evaluation model
        
    Returns:
        Dict mapping score names to float values
    """
    scores = {}
    for line in scores_text.split():
        if ':' in line:
            key, value = line.split(':')
            try:
                scores[key] = float(value)
            except:
                pass
    return scores


def evaluate_response_quality(response: str, scenario: Scenario) -> Dict[str, float]:
    """
    Evaluate response quality using multi-model scoring
    
    Uses GPT-4.1, Sonnet 4, and Gemini 2.5 to evaluate response quality
    across multiple dimensions, then averages scores to eliminate bias.
    
    Evaluation Dimensions:
    - Specificity: Does response mention specific technical details?
    - Personalization: Does it address user's context and preferences?
    - Actionability: Does it provide concrete, executable steps?
    - Context Utilization: Does it effectively use available context?
    - Overall: Holistic quality assessment
    
    Args:
        response: AI response to evaluate
        scenario: Test scenario with context and criteria
        
    Returns:
        Dict with averaged scores across all evaluation models
    """
    # Extract data from scenario object
    user_request = scenario.get_user_request()
    user_profile = scenario.user_profile
    project_context = scenario.project_context
    evaluation_criteria = scenario.evaluation_criteria
    
    # Build detailed evaluation criteria from scenario
    specificity_criteria = '\n'.join([f"  - {item}" for item in evaluation_criteria.get('specificity', [])])
    personalization_criteria = '\n'.join([f"  - {item}" for item in evaluation_criteria.get('personalization', [])])
    actionability_criteria = '\n'.join([f"  - {item}" for item in evaluation_criteria.get('actionability', [])])
    context_utilization_criteria = '\n'.join([f"  - {item}" for item in evaluation_criteria.get('context_utilization', [])])
    
    evaluation_prompt = f"""Evaluate this technical advice response for quality on a scale of 0-1:

CONTEXT:
- User: {user_profile.name} ({user_profile.role})
- Preferences: {user_profile.preferences}
- Project: {project_context.repo} using {', '.join(project_context.tech_stack)}
- Request: {user_request}

RESPONSE TO EVALUATE:
{response}

EVALUATION CRITERIA - Rate 0-1 for each based on these specific requirements:

1. SPECIFICITY (0-1): Does the response mention specific details?
{specificity_criteria}

2. PERSONALIZATION (0-1): Does it address the user's context and preferences?
{personalization_criteria}

3. ACTIONABILITY (0-1): Does it provide concrete, executable steps?
{actionability_criteria}

4. CONTEXT_UTILIZATION (0-1): Does it effectively use available context and tool results?
{context_utilization_criteria}

Format: specificity:0.X personalization:0.X actionability:0.X context_utilization:0.X overall:0.X

Only output the scores, nothing else."""
    
    # Use all three models for evaluation to eliminate bias
    all_scores = []
    for eval_model in EVALUATION_MODELS.values():
        result = test_model([{"role": "user", "content": evaluation_prompt}], eval_model)
        scores = _parse_evaluation_scores(result['response'])
        all_scores.append(scores)
    
    # Average scores across all three models
    averaged_scores = {}
    score_keys = ['specificity', 'personalization', 'actionability', 'context_utilization', 'overall']
    
    for key in score_keys:
        scores_for_key = [scores.get(key, 0.0) for scores in all_scores]
        averaged_scores[key] = sum(scores_for_key) / len(scores_for_key)
    
    return averaged_scores


@observe(name="factor3_model_test")
def test_model_and_evaluate(messages: List[Dict], model_key: str, model_name: str, 
                           model_id: str, scenario: Scenario, format_name: str) -> Dict:
    """
    Test a model with given messages and evaluate response quality
    
    This function is decorated with Langfuse observability to track
    individual test runs as traces.
    
    Args:
        messages: Formatted messages to send to model
        model_key: Short model identifier (e.g., "gpt-4.1")
        model_name: Display name for model (e.g., "GPT-4.1")
        model_id: Full LiteLLM model identifier
        scenario: Test scenario being evaluated
        format_name: Name of context format being tested
        
    Returns:
        Dict with test results including quality scores
    """
    print(f"\n🤖 Testing {model_name}...")
    
    # Test the model
    result = test_model(messages, model_id)
    
    # Evaluate response quality using multi-model scoring
    print(f"📊 Evaluating with GPT-4.1, Sonnet 4, Gemini 2.5...")
    quality = evaluate_response_quality(result['response'], scenario)
    result['quality'] = quality
    
    # Print results
    print(f"✅ Success: {result['total_tokens']} tokens, ${result['cost']:.6f}, {result['time']:.2f}s")
    print(f"   Quality Score: {quality['overall']:.2f} (Spec: {quality.get('specificity', 0):.2f}, Pers: {quality.get('personalization', 0):.2f}, Action: {quality.get('actionability', 0):.2f}, Context: {quality.get('context_utilization', 0):.2f})")
    
    # Log additional metadata to current Langfuse trace
    langfuse_context.update_current_trace(
        metadata={
            "scenario": scenario.name,
            "format": format_name,
            "model": model_name,
            "model_id": model_id,
            "total_tokens": result['total_tokens'],
            "cost": result['cost'],
            "quality_overall": quality['overall'],
            "quality_scores": quality
        }
    )
    
    return result