#!/usr/bin/env python3
"""
Factor 3 Quality Comparison
Tests whether structured context actually improves response quality
Measures specificity, accuracy, and actionability of responses
Follows the factor-01 demo pattern: simple, focused, production-ready
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

import litellm
from langfuse.decorators import observe, langfuse_context

litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"]
litellm.modify_params = True  # Allow LiteLLM to modify params for compatibility

load_dotenv()

@dataclass
class WorkHistoryItem:
    type: str
    result: str
    date: str
    duration: Optional[str] = None
    notes: Optional[str] = None
    target: Optional[str] = None    # For migrations
    issue: Optional[str] = None     # For incidents
    version: Optional[str] = None   # For deployments
    
    def to_natural_language(self) -> str:
        duration_text = f" ({self.duration})" if self.duration else ""
        
        # Handle different types of work items with specific details
        if self.target:
            detail = f"target: {self.target}"
        elif self.issue:
            detail = f"issue: {self.issue}"
        elif self.version:
            detail = f"version: {self.version}"
        else:
            detail = self.notes or 'no details'
            
        return f"{self.type}: {self.result} on {self.date}{duration_text} - {detail}"

@dataclass
class UserProfile:
    name: str
    role: str
    team: str
    preferences: str
    specialization: str
    history: List[WorkHistoryItem]
    
    def to_xml_format(self) -> str:
        history_formatted = "\n".join([f"    - {item.to_natural_language()}" for item in self.history])
        
        return f"""<user_profile>
  <name>{self.name}</name>
  <role>{self.role}</role>
  <team>{self.team}</team>
  <preferences>{self.preferences}</preferences>
  <specialization>{self.specialization}</specialization>
  <work_history>
{history_formatted if history_formatted else '    - No work history available'}
  </work_history>
</user_profile>"""
    
    def to_natural_language(self) -> str:
        history_text = "\n".join([f"  - {item.to_natural_language()}" for item in self.history])
        return f"""{self.name} is a {self.role} on the {self.team} team.
  
  Working style: {self.preferences}
  Expertise: {self.specialization}
  
  Recent work history:
{history_text if history_text else '  - No work history available'}"""

@dataclass
class ProjectContext:
    repo: str
    tech_stack: List[str]
    current_version: str
    infrastructure: Dict[str, Any]
    current_state: Dict[str, Any]
    requirements: Dict[str, Any]
    recent_changes: List[Dict[str, str]]
    
    def to_xml_format(self) -> str:
        tech_stack_formatted = "\n    ".join([f"- {tech}" for tech in self.tech_stack])
        recent_changes_formatted = "\n".join([
            f"    - {change.get('version', 'unknown')}: {change.get('changes', 'no description')}"
            for change in self.recent_changes
        ])
        
        # Extract infrastructure details safely
        prod_info = self.infrastructure.get('production', {})
        instances = prod_info.get('instances', 'unknown')
        regions = ', '.join(prod_info.get('regions', []))
        instance_type = prod_info.get('type', 'unknown')
        deployment_pattern = self.infrastructure.get('deployment_pattern', 'unknown')
        monitoring = ', '.join(self.infrastructure.get('monitoring', []))
        
        # Extract current state safely
        health = self.current_state.get('health_status', 'unknown')
        alerts = self.current_state.get('active_alerts', 'unknown')
        perf_metrics = self.current_state.get('performance_metrics', {})
        p95 = perf_metrics.get('p95_response_time', 'unknown')
        error_rate = self.current_state.get('error_rate', perf_metrics.get('error_rate', 'unknown'))
        cpu = self.current_state.get('cpu_usage', 'unknown')
        memory = self.current_state.get('memory_usage', 'unknown')
        
        # Extract requirements safely
        uptime_sla = self.requirements.get('uptime_sla', 'unknown')
        perf_sla = self.requirements.get('performance_sla', 'unknown')
        deploy_window = self.requirements.get('deployment_window', self.requirements.get('deployment_windows', 'unknown'))
        rollback_time = self.requirements.get('rollback_time', 'unknown')
        
        return f"""<project_context>
  <repository>{self.repo}</repository>
  <current_version>{self.current_version}</current_version>
  
  <technology_stack>
    {tech_stack_formatted}
  </technology_stack>
  
  <infrastructure>
    Production: {instances} instances in {regions} regions
    Instance type: {instance_type}
    Deployment pattern: {deployment_pattern}
    Monitoring: {monitoring}
  </infrastructure>
  
  <current_state>
    Health: {health}
    Active alerts: {alerts}
    Performance: P95 {p95}, Error rate {error_rate}
    Load: CPU {cpu}, Memory {memory}
  </current_state>
  
  <requirements>
    Uptime SLA: {uptime_sla}
    Performance SLA: {perf_sla}
    Deployment windows: {deploy_window}
    Rollback time: {rollback_time}
  </requirements>
  
  <recent_changes>
{recent_changes_formatted if recent_changes_formatted else '    - No recent changes'}
  </recent_changes>
</project_context>"""
    
    def to_natural_language(self) -> str:
        tech_stack_natural = ', '.join(self.tech_stack)
        changes_natural = "\n".join([
            f"  - {change.get('version', 'unknown')}: {change.get('changes', 'no description')}"
            for change in self.recent_changes
        ])
        
        # Extract key infrastructure and state info
        prod_info = self.infrastructure.get('production', {})
        instances = prod_info.get('instances', 'unknown')
        regions = ', '.join(prod_info.get('regions', []))
        deployment_pattern = self.infrastructure.get('deployment_pattern', 'unknown')
        health = self.current_state.get('health_status', 'unknown')
        alerts = self.current_state.get('active_alerts', 'unknown')
        uptime_sla = self.requirements.get('uptime_sla', 'unknown')
        perf_sla = self.requirements.get('performance_sla', 'unknown')
        deploy_window = self.requirements.get('deployment_window', self.requirements.get('deployment_windows', 'unknown'))
        
        return f"""Project: {self.repo} (currently running {self.current_version})
  Technology stack: {tech_stack_natural}
  
  Infrastructure: {instances} production instances across {regions} regions
  Deployment approach: {deployment_pattern}
  
  Current system status: {health} with {alerts} active alerts
  
  SLA requirements: {uptime_sla} uptime, {perf_sla} performance target
  Deployment constraints: {deploy_window}
  
  Recent changes:
{changes_natural if changes_natural else '  - No recent changes'}"""

@dataclass
class Scenario:
    name: str
    standard_messages: List[Dict[str, Any]]
    evaluation_criteria: Dict[str, List[str]]
    user_profile: UserProfile
    project_context: ProjectContext
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Scenario':
        # Parse user profile
        user_data = data['context']['user_profile']
        history_items = []
        for item in user_data.get('history', []):
            if isinstance(item, dict):
                history_items.append(WorkHistoryItem(
                    type=item.get('type', 'event'),
                    result=item.get('result', 'completed'),
                    date=item.get('date', 'unknown'),
                    duration=item.get('duration'),
                    notes=item.get('notes'),
                    target=item.get('target'),        # For migrations
                    issue=item.get('issue'),          # For incidents  
                    version=item.get('version')       # For deployments
                ))
        
        user_profile = UserProfile(
            name=user_data['name'],
            role=user_data['role'],
            team=user_data.get('team', 'N/A'),
            preferences=user_data['preferences'],
            specialization=user_data.get('specialization', 'N/A'),
            history=history_items
        )
        
        # Parse project context
        project_data = data['context']['project_context']
        project_context = ProjectContext(
            repo=project_data['repo'],
            tech_stack=project_data['tech_stack'],
            current_version=project_data['current_version'],
            infrastructure=project_data.get('infrastructure', {}),
            current_state=project_data.get('current_state', {}),
            requirements=project_data.get('requirements', {}),
            recent_changes=project_data.get('recent_changes', [])
        )
        
        return cls(
            name=data['name'],
            standard_messages=data['standard_messages'],
            evaluation_criteria=data['evaluation_criteria'],
            user_profile=user_profile,
            project_context=project_context
        )
    
    def get_user_request(self) -> str:
        return self.standard_messages[-1]["content"]
    
    def get_conversation_flow(self) -> List[str]:
        conversation_flow = []
        for msg in self.standard_messages[1:-1]:  # Skip system and final user message
            if msg["role"] == "user":
                conversation_flow.append(f"User: {msg['content']}")
            elif msg["role"] == "assistant" and "tool_calls" not in msg:
                conversation_flow.append(f"Assistant: {msg['content']}")
        return conversation_flow
    
    def get_tool_results(self) -> List[Dict[str, str]]:
        tool_results = []
        for msg in self.standard_messages[1:-1]:
            if msg["role"] == "assistant" and "tool_calls" in msg:
                for tool_call in msg["tool_calls"]:
                    tool_results.append({
                        "function": tool_call["function"]["name"],
                        "args": tool_call["function"]["arguments"],
                        "call_id": tool_call["id"]
                    })
            elif msg["role"] == "tool":
                # Find matching tool call and combine
                for tool_result in tool_results:
                    if tool_result["call_id"] == msg["tool_call_id"]:
                        tool_result["result"] = msg["content"]
                        break
        return tool_results

# Latest model versions - LiteLLM format
MODELS = {
    "gpt-4.1": "gpt-4.1-2025-04-14",
    "sonnet-4": "claude-sonnet-4-20250514", 
    "gemini-2.5": "gemini/gemini-2.5-pro-preview-05-06"  # Use gemini/ prefix for Google AI Studio
}

def load_test_scenarios():
    """Load test scenarios from JSON file and convert to Scenario objects"""
    with open('scenarios.json', 'r') as f:
        data = json.load(f)
    return [Scenario.from_dict(item) for item in data]

def format_standard(scenario: Scenario):
    """Standard message format (baseline) - Original OpenAI conversation format"""
    # LiteLLM should handle tool call format translation automatically
    return scenario.standard_messages

def format_xml_structured(scenario: Scenario):
    """XML structured format - Factor 3 single message with comprehensive context"""
    user_request = scenario.get_user_request()
    conversation_flow = scenario.get_conversation_flow()
    tool_results = scenario.get_tool_results()
    
    xml_content = f"""{scenario.user_profile.to_xml_format()}

{scenario.project_context.to_xml_format()}

<conversation_flow>
{chr(10).join(conversation_flow)}
</conversation_flow>

<tool_results>
{chr(10).join([f"  {result['function']}: {result['result']}" for result in tool_results])}
</tool_results>

<current_request>{user_request}</current_request>"""

    return [
        scenario.standard_messages[0],  # Keep original system message
        {"role": "user", "content": xml_content}
    ]

def format_compressed(scenario: Scenario):
    """Compressed format - minimal tokens but includes key context from all areas"""
    user_request = scenario.get_user_request()
    
    # Extract tool results efficiently for compressed format
    tool_summary = []
    for msg in scenario.standard_messages[1:-1]:
        if msg["role"] == "tool":
            # Extract just key-value pairs from tool results
            try:
                result_data = json.loads(msg["content"])
                key_info = []
                for key, value in result_data.items():
                    if key in ["status", "current_version", "error_rate", "p95_response_time", "health_status"]:
                        key_info.append(f"{key}:{value}")
                if key_info:
                    tool_summary.append("|".join(key_info[:2]))  # Max 2 key metrics per tool
            except:
                pass
    
    # Create compressed representation but include all key context areas
    role_abbrev = scenario.user_profile.role.split()[0]  # "Senior DevOps Engineer" -> "Senior"
    tech_abbrev = "+".join([tech.split()[0] for tech in scenario.project_context.tech_stack[:3]])  # First 3 tech stack items
    history_abbrev = f"{len(scenario.user_profile.history)}prev" if scenario.user_profile.history else "0prev"
    version_abbrev = scenario.project_context.current_version
    state_abbrev = scenario.project_context.current_state.get('health_status', 'unknown')[:10]
    tools_abbrev = ";".join(tool_summary[:2]) if tool_summary else "no-tools"  # Max 2 tool results
    
    compressed = f"USER:{role_abbrev}|PREF:{scenario.user_profile.preferences[:40]}|PROJ:{tech_abbrev}|VER:{version_abbrev}|STATE:{state_abbrev}|HIST:{history_abbrev}|TOOLS:{tools_abbrev}|REQ:{user_request}"
    
    return [
        {"role": "system", "content": f"{scenario.standard_messages[0]['content']} Format: USER=role|PREF=preferences|PROJ=tech|VER=version|STATE=health|HIST=history|TOOLS=tool_results|REQ=request"},
        {"role": "user", "content": compressed}
    ]

def format_document_centric(scenario: Scenario):
    """Document-centric format - True Factor 3 following official Anthropic docs"""
    from datetime import datetime
    
    user_request = scenario.get_user_request()
    conversation_summary = scenario.get_conversation_flow()
    tool_results = scenario.get_tool_results()

    # Build document-centric structure following official Factor 3 docs with natural language
    document_content = f"""<document>
<document_content>
<user_profile>
{scenario.user_profile.to_natural_language()}
</user_profile>

<project_context>
{scenario.project_context.to_natural_language()}
</project_context>

<conversation_context>
{chr(10).join(conversation_summary)}
</conversation_context>

<tool_results>
{chr(10).join([f"  {result['function']}: {result['result']}" for result in tool_results])}
</tool_results>
</document_content>

<source>Live engineering context - {datetime.now().isoformat()}</source>
</document>

<current_request>
{user_request}
</current_request>"""

    return [
        scenario.standard_messages[0],  # Keep original system message  
        {"role": "user", "content": document_content}
    ]

def format_markdown(scenario: Scenario):
    """Markdown format - clean, readable structure using markdown syntax"""
    user_request = scenario.get_user_request()
    tool_results = scenario.get_tool_results()
    
    # Format user history entries
    history_entries = [item.to_natural_language() for item in scenario.user_profile.history]
    
    # Format conversation history
    conversation_entries = []
    for msg in scenario.standard_messages[1:-1]:
        if msg['role'] != 'tool':  # Skip tool messages, we'll include results separately
            conversation_entries.append(f"**{msg['role'].title()}**: {msg['content']}")
    
    # Format recent changes
    changes_entries = []
    for change in scenario.project_context.recent_changes:
        changes_entries.append(f"- **{change.get('version', 'unknown')}**: {change.get('changes', 'no description')}")
    
    # Format tool results
    tool_entries = []
    for result in tool_results:
        tool_entries.append(f"- **{result['function']}**: {result['result']}")
    
    markdown_content = f"""# Context and Current Request

## User Profile
- **Name**: {scenario.user_profile.name}
- **Role**: {scenario.user_profile.role} ({scenario.user_profile.team} team)
- **Working Style**: {scenario.user_profile.preferences}
- **Expertise**: {scenario.user_profile.specialization}

### Work History
{chr(10).join([f"- {entry}" for entry in history_entries]) if history_entries else "- No history available"}

## Project Context
- **Repository**: {scenario.project_context.repo} (version {scenario.project_context.current_version})
- **Technology Stack**: {', '.join(scenario.project_context.tech_stack)}
- **Infrastructure**: {scenario.project_context.infrastructure.get("production", {}).get("instances", "unknown")} instances, {scenario.project_context.infrastructure.get("deployment_pattern", "unknown")} deployment
- **Current Status**: {scenario.project_context.current_state.get("health_status", "unknown")} system with {scenario.project_context.current_state.get("active_alerts", "unknown")} alerts
- **Requirements**: {scenario.project_context.requirements.get("uptime_sla", "unknown")} uptime, {scenario.project_context.requirements.get("performance_sla", "unknown")} performance

### Recent Changes
{chr(10).join(changes_entries) if changes_entries else "- No recent changes"}

## Conversation History
{chr(10).join(conversation_entries) if conversation_entries else "- No prior conversation"}

## Tool Results
{chr(10).join(tool_entries) if tool_entries else "- No tool results"}

## Current Request
{user_request}"""
    
    return [
        scenario.standard_messages[0],  # Keep original system message
        {"role": "user", "content": markdown_content}
    ]

def test_model(messages, model):
    """Test with any model via LiteLLM unified interface"""
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

@observe(name="factor3_model_test")
def test_model_and_evaluate(messages, model_key, model_name, model_id, scenario, format_name):
    """Test a model and evaluate response quality - captured as single Langfuse trace"""
    print(f"\n🤖 Testing {model_name}...")
    
    # Test the model
    result = test_model(messages, model_id)
    
    # Evaluate response quality
    print(f"📊 Evaluating with GPT-4.1, Sonnet 4, Gemini 2.5...")
    quality = evaluate_response_quality(result['response'], scenario)
    result['quality'] = quality
    
    # Print results
    print(f"✅ Success: {result['total_tokens']} tokens, ${result['cost']:.6f}, {result['time']:.2f}s")
    print(f"   Quality Score: {quality['overall']:.2f} (Spec: {quality.get('specificity', 0):.2f}, Pers: {quality.get('personalization', 0):.2f}, Action: {quality.get('actionability', 0):.2f}, Context: {quality.get('context_utilization', 0):.2f})")
    
    # Log additional metadata to current trace
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

def run_test(format_name, format_func, scenario):
    """Run test for a specific format across all models"""
    print(f"\n{'='*60}")
    print(f"Testing: {format_name}")
    print(f"{'='*60}")
    
    messages = format_func(scenario)
    results = {}
    
    # Test all models using unified interface
    model_configs = [
        ("gpt-4.1", "GPT-4.1", MODELS["gpt-4.1"]),
        ("sonnet-4", "Sonnet 4", MODELS["sonnet-4"]),
        ("gemini-2.5", "Gemini 2.5", MODELS["gemini-2.5"])
    ]
    
    for model_key, model_name, model_id in model_configs:
        result = test_model_and_evaluate(messages, model_key, model_name, model_id, scenario, format_name)
        results[model_key] = result
    
    return results

def _parse_evaluation_scores(scores_text):
    """Parse evaluation scores from text response"""
    scores = {}
    for line in scores_text.split():
        if ':' in line:
            key, value = line.split(':')
            try:
                scores[key] = float(value)
            except:
                pass
    return scores

def evaluate_response_quality(response, scenario: Scenario):
    """
    Use same models as testing (GPT-4.1, Sonnet 4, Gemini 2.5) to evaluate response quality
    Returns averaged scores across models to eliminate single-model bias
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

    # Use all three models for evaluation
    evaluation_models = [
        MODELS["gpt-4.1"],
        MODELS["sonnet-4"],
        MODELS["gemini-2.5"]
    ]
    
    all_scores = []
    for eval_model in evaluation_models:
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

def analyze_results_by_models(results_data, model_filter=None):
    """Analyze results with optional model filtering"""
    if model_filter is None:
        model_filter = ["gpt-4.1", "sonnet-4", "gemini-2.5"]
    
    print(f"\n🔍 ANALYSIS WITH MODELS: {', '.join(model_filter)}")
    print("-" * 60)
    
    # Aggregate results by format across all scenarios with model filtering
    format_aggregates = {}
    
    for scenario_name, scenario_results in results_data.items():
        for format_name, format_results in scenario_results.items():
            if format_name not in format_aggregates:
                format_aggregates[format_name] = {'quality_scores': [], 'token_counts': [], 'costs': []}
                
            for model_name, result in format_results.items():
                if model_name in model_filter:
                    quality_score = result.get('quality', {}).get('overall', 0)
                    format_aggregates[format_name]['quality_scores'].append(quality_score)
                    format_aggregates[format_name]['token_counts'].append(result['total_tokens'])
                    format_aggregates[format_name]['costs'].append(result['cost'])
    
    # Calculate statistical summary
    quality_by_format = {}
    for format_name, data in format_aggregates.items():
        if data['quality_scores']:
            quality_by_format[format_name] = {
                'avg_quality': sum(data['quality_scores']) / len(data['quality_scores']),
                'avg_tokens': sum(data['token_counts']) / len(data['token_counts']),
                'avg_cost': sum(data['costs']) / len(data['costs']),
                'sample_size': len(data['quality_scores'])
            }
    
    # Sort by quality
    sorted_formats = sorted(quality_by_format.items(), key=lambda x: x[1]['avg_quality'], reverse=True)
    
    for format_name, stats in sorted_formats:
        print(f"{format_name:<25} Quality: {stats['avg_quality']:.3f} | Tokens: {stats['avg_tokens']:.0f} | Cost: ${stats['avg_cost']:.5f} | n={stats['sample_size']}")
    
    # Calculate improvement statistics
    if len(quality_by_format) >= 2:
        quality_values = [stats['avg_quality'] for stats in quality_by_format.values()]
        best_quality = max(quality_values)
        worst_quality = min(quality_values)
        improvement = ((best_quality - worst_quality) / worst_quality) * 100 if worst_quality > 0 else 0
        
        # Cost-benefit analysis
        best_format = sorted_formats[0][0] 
        worst_format = sorted_formats[-1][0]
        best_cost = quality_by_format[best_format]['avg_cost']
        worst_cost = quality_by_format[worst_format]['avg_cost']
        cost_multiplier = best_cost / worst_cost if worst_cost > 0 else 1
        
        print(f"\n📊 RESULTS WITH {', '.join(model_filter).upper()}:")
        print(f"   Quality improvement: {improvement:.1f}%")
        print(f"   Cost increase: {(cost_multiplier - 1) * 100:.1f}%")
        print(f"   Quality/Cost ratio: {improvement / ((cost_multiplier - 1) * 100) if cost_multiplier > 1 else float('inf'):.2f}")
        
        return {
            'quality_improvement': improvement,
            'cost_increase': (cost_multiplier - 1) * 100,
            'quality_cost_ratio': improvement / ((cost_multiplier - 1) * 100) if cost_multiplier > 1 else float('inf'),
            'best_quality': best_quality,
            'worst_quality': worst_quality,
            'sample_size': sum(stats['sample_size'] for stats in quality_by_format.values())
        }
    
    return None

def load_and_analyze_results(filename):
    """Load existing results and analyze with different model combinations"""
    with open(filename, 'r') as f:
        results_data = json.load(f)
    
    print("🔬 COMPARATIVE MODEL ANALYSIS")
    print("=" * 80)
    
    # All models
    all_models_stats = analyze_results_by_models(results_data, ["gpt-4.1", "sonnet-4", "gemini-2.5"])
    
    # Without Gemini (no reasoning tokens)
    no_gemini_stats = analyze_results_by_models(results_data, ["gpt-4.1", "sonnet-4"])
    
    # Only Gemini
    only_gemini_stats = analyze_results_by_models(results_data, ["gemini-2.5"])
    
    # Only GPT-4.1
    only_gpt_stats = analyze_results_by_models(results_data, ["gpt-4.1"])
    
    # Only Sonnet 4
    only_sonnet_stats = analyze_results_by_models(results_data, ["sonnet-4"])
    
    print(f"\n🏆 SUMMARY COMPARISON:")
    print(f"{'Model Combination':<20} {'Quality Gain':<12} {'Cost Increase':<14} {'Value Ratio':<12}")
    print("-" * 60)
    
    if all_models_stats:
        print(f"{'All Models':<20} {all_models_stats['quality_improvement']:<12.1f}% {all_models_stats['cost_increase']:<14.1f}% {all_models_stats['quality_cost_ratio']:<12.2f}")
    
    if no_gemini_stats:
        print(f"{'GPT-4.1 + Sonnet':<20} {no_gemini_stats['quality_improvement']:<12.1f}% {no_gemini_stats['cost_increase']:<14.1f}% {no_gemini_stats['quality_cost_ratio']:<12.2f}")
    
    if only_gemini_stats:
        print(f"{'Gemini Only':<20} {only_gemini_stats['quality_improvement']:<12.1f}% {only_gemini_stats['cost_increase']:<14.1f}% {only_gemini_stats['quality_cost_ratio']:<12.2f}")
    
    if only_gpt_stats:
        print(f"{'GPT-4.1 Only':<20} {only_gpt_stats['quality_improvement']:<12.1f}% {only_gpt_stats['cost_increase']:<14.1f}% {only_gpt_stats['quality_cost_ratio']:<12.2f}")
    
    if only_sonnet_stats:
        print(f"{'Sonnet 4 Only':<20} {only_sonnet_stats['quality_improvement']:<12.1f}% {only_sonnet_stats['cost_increase']:<14.1f}% {only_sonnet_stats['quality_cost_ratio']:<12.2f}")
    
    print(f"\n💡 INSIGHT: Gemini's reasoning tokens impact cost analysis")
    if no_gemini_stats and all_models_stats:
        cost_diff = all_models_stats['cost_increase'] - no_gemini_stats['cost_increase']
        print(f"   Cost difference with/without Gemini: {cost_diff:.1f} percentage points")
        print(f"   Cleaner cost analysis excludes reasoning token overhead")

def main():
    """Run the Factor 3 quality comparison test"""
    print("🧪 FACTOR 3 QUALITY COMPARISON")
    print("Testing whether structured context actually improves response quality")
    print("Models: GPT-4.1, Sonnet 4, Gemini 2.5")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Validate all required API keys
    required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        raise ValueError(f"All API keys are required: {', '.join(missing_keys)}")
    
    print(f"\n✅ All APIs configured: OpenAI, Anthropic, Gemini")
    
    # Get test scenarios
    scenarios = load_test_scenarios()
    
    # Test formats - progression from standard to Factor 3 optimized
    # All formats now use standardized context coverage for fair comparison
    formats = [
        ("Standard Messages (Baseline)", format_standard),
        ("XML Structured (Factor 3)", format_xml_structured),
        ("Document-Centric (Factor 3)", format_document_centric),
        ("Compressed (Factor 3)", format_compressed),
        ("Markdown (Factor 3)", format_markdown)
    ]
    
    all_results = {}
    num_models = 3  # GPT-4.1, Sonnet 4, Gemini 2.5
    total_tests = len(scenarios) * len(formats) * num_models
    test_count = 0
    
    print(f"\n🎯 Running {total_tests} total tests across {len(scenarios)} scenarios...")
    
    for scenario in scenarios:
        print(f"\n{'='*80}")
        print(f"SCENARIO: {scenario.name}")
        print(f"{'='*80}")
        
        scenario_results = {}
        
        for format_name, format_func in formats:
            results = run_test(format_name, format_func, scenario)
            scenario_results[format_name] = results
            test_count += len(results)
        
        all_results[scenario.name] = scenario_results
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"factor3_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Summary across all scenarios
    print(f"\n{'='*80}")
    print("COMPREHENSIVE RESULTS ACROSS ALL SCENARIOS")
    print(f"{'='*80}")
    print(f"Total tests completed: {test_count}")
    
    # Aggregate results by format across all scenarios
    format_aggregates = {}
    
    for scenario_name, scenario_results in all_results.items():
        print(f"\n--- {scenario_name} ---")
        print(f"{'Format':<25} {'Model':<12} {'Tokens':<8} {'Cost':<10} {'Quality':<8} {'Time':<6}")
        print("-" * 80)
        
        for format_name, format_results in scenario_results.items():
            if format_name not in format_aggregates:
                format_aggregates[format_name] = {'quality_scores': [], 'token_counts': [], 'costs': []}
                
            for model_name, result in format_results.items():
                quality_score = result.get('quality', {}).get('overall', 0)
                format_aggregates[format_name]['quality_scores'].append(quality_score)
                format_aggregates[format_name]['token_counts'].append(result['total_tokens'])
                format_aggregates[format_name]['costs'].append(result['cost'])
                
                print(f"{format_name:<25} {model_name:<12} {result['total_tokens']:<8} ${result['cost']:<9.6f} {quality_score:<8.2f} {result['time']:<6.2f}s")
    
    # Calculate statistical summary
    quality_by_format = {}
    for format_name, data in format_aggregates.items():
        if data['quality_scores']:
            quality_by_format[format_name] = {
                'avg_quality': sum(data['quality_scores']) / len(data['quality_scores']),
                'avg_tokens': sum(data['token_counts']) / len(data['token_counts']),
                'avg_cost': sum(data['costs']) / len(data['costs']),
                'sample_size': len(data['quality_scores'])
            }
    
    # Factor 3 Effectiveness Analysis
    print(f"\n🎯 FACTOR 3 STATISTICAL ANALYSIS")
    print("-" * 60)
    
    # Sort by quality
    sorted_formats = sorted(quality_by_format.items(), key=lambda x: x[1]['avg_quality'], reverse=True)
    
    for format_name, stats in sorted_formats:
        print(f"{format_name:<25} Quality: {stats['avg_quality']:.3f} | Tokens: {stats['avg_tokens']:.0f} | Cost: ${stats['avg_cost']:.5f} | n={stats['sample_size']}")
    
    # Determine if Factor 3 actually works
    if len(quality_by_format) >= 2:
        quality_values = [stats['avg_quality'] for stats in quality_by_format.values()]
        best_quality = max(quality_values)
        worst_quality = min(quality_values)
        improvement = ((best_quality - worst_quality) / worst_quality) * 100 if worst_quality > 0 else 0
        
        print(f"\n📊 FACTOR 3 STATISTICAL SIGNIFICANCE:")
        print(f"   Quality improvement: {improvement:.1f}%")
        print(f"   Best format quality:  {best_quality:.3f}")
        print(f"   Worst format quality: {worst_quality:.3f}")
        print(f"   Total sample size: {sum(stats['sample_size'] for stats in quality_by_format.values())}")
        
        # More rigorous assessment
        sample_size = sum(stats['sample_size'] for stats in quality_by_format.values())
        if sample_size < 15:
            print(f"⚠️  Small sample size (n={sample_size}) - results may not be statistically significant")
        
        if improvement > 25:
            print("✅ Factor 3 STRONGLY PROVEN: Large quality improvement!")
        elif improvement > 15:
            print("✅ Factor 3 PROVEN: Significant quality improvement!")
        elif improvement > 8:
            print("⚠️ Factor 3 MODEST: Some quality improvement, but may not justify cost")
        else:
            print("❌ Factor 3 UNCLEAR: Minimal quality difference - cost may not be justified")
        
        # Cost-benefit analysis
        best_format = sorted_formats[0][0] 
        worst_format = sorted_formats[-1][0]
        best_cost = quality_by_format[best_format]['avg_cost']
        worst_cost = quality_by_format[worst_format]['avg_cost']
        cost_multiplier = best_cost / worst_cost if worst_cost > 0 else 1
        
        print(f"\n💰 COST-BENEFIT ANALYSIS:")
        print(f"   Quality improvement: {improvement:.1f}%")
        print(f"   Cost increase: {(cost_multiplier - 1) * 100:.1f}%")
        print(f"   Quality/Cost ratio: {improvement / ((cost_multiplier - 1) * 100) if cost_multiplier > 1 else float('inf'):.2f}")
        
        if improvement / (cost_multiplier * 100) > 0.5:
            print("✅ Good value: Quality improvement justifies cost increase")
        else:
            print("❌ Poor value: Cost increase may not justify quality improvement")
    
    print(f"\n💾 Results saved to: {filename}")
    print("\n🎬 Perfect for video demonstration!")
    
    # Run model comparison analysis on saved results
    analyze_results_by_models(all_results)

if __name__ == "__main__":
    main()
