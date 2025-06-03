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

litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"]

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

# Latest model versions
MODELS = {
    "gpt-4.1": "gpt-4.1-2025-04-14",
    "sonnet-4": "claude-sonnet-4-20250514",
    "gemini-2.5": "gemini-2.5-pro-preview-05-06"
}

def estimate_tokens(text: str) -> int:
    """Simple token estimation (roughly 4 chars per token)"""
    return len(text) // 4

def load_test_scenarios():
    """Load test scenarios from JSON file and convert to Scenario objects"""
    with open('scenarios.json', 'r') as f:
        data = json.load(f)
    return [Scenario.from_dict(item) for item in data]

def format_standard(scenario: Scenario):
    """Standard message format (baseline) - API-neutral conversation as simple text"""
    user_request = scenario.get_user_request()
    
    # Convert OpenAI-style messages to API-neutral text format
    conversation_parts = []
    
    for msg in scenario.standard_messages[1:-1]:  # Skip system and final user message
        role = msg["role"]
        content = msg["content"]
        
        if role == "user":
            conversation_parts.append(f"User: {content}")
        elif role == "assistant":
            if "tool_calls" in msg and msg["tool_calls"]:
                # Convert tool calls to natural language
                text_content = content or ""
                for tool_call in msg["tool_calls"]:
                    func_name = tool_call["function"]["name"]
                    func_args = tool_call["function"]["arguments"]
                    text_content += f" [Called {func_name} with {func_args}]"
                conversation_parts.append(f"Assistant: {text_content}")
            else:
                conversation_parts.append(f"Assistant: {content}")
        elif role == "tool":
            # Tool results as system information
            conversation_parts.append(f"System returned: {content}")
    
    # Create simple conversation text
    conversation_text = "\n\n".join(conversation_parts)
    simple_content = f"""Previous conversation:
{conversation_text}

Current request: {user_request}"""
    
    return [
        scenario.standard_messages[0],  # Keep original system message
        {"role": "user", "content": simple_content}
    ]

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

def format_json_conversation(scenario: Scenario):
    """JSON conversation history - structured conversation with context metadata"""
    user_request = scenario.get_user_request()
    tool_results = scenario.get_tool_results()
    
    # Format user history entries
    history_entries = [item.to_natural_language() for item in scenario.user_profile.history]
    
    # Format conversation history
    conversation_entries = []
    for msg in scenario.standard_messages[1:-1]:
        if msg['role'] != 'tool':  # Skip tool messages, we'll include results separately
            conversation_entries.append(f"{msg['role']}: {msg['content']}")
    
    # Format recent changes
    changes_entries = []
    for change in scenario.project_context.recent_changes:
        changes_entries.append(f"{change.get('version', 'unknown')}: {change.get('changes', 'no description')}")
    
    # Format tool results
    tool_entries = []
    for result in tool_results:
        tool_entries.append(f"{result['function']}: {result['result']}")
    
    json_content = f"""Context and request in structured format:

USER PROFILE:
  Name: {scenario.user_profile.name}
  Role: {scenario.user_profile.role} ({scenario.user_profile.team} team)
  Working style: {scenario.user_profile.preferences}
  Expertise: {scenario.user_profile.specialization}
  
  Work history:
{chr(10).join([f"    - {entry}" for entry in history_entries]) if history_entries else "    - No history available"}

PROJECT CONTEXT:
  Repository: {scenario.project_context.repo} (version {scenario.project_context.current_version})
  Technology: {', '.join(scenario.project_context.tech_stack)}
  
  Infrastructure: {scenario.project_context.infrastructure.get("production", {}).get("instances", "unknown")} instances, {scenario.project_context.infrastructure.get("deployment_pattern", "unknown")} deployment
  
  Current status: {scenario.project_context.current_state.get("health_status", "unknown")} system with {scenario.project_context.current_state.get("active_alerts", "unknown")} alerts
  
  Requirements: {scenario.project_context.requirements.get("uptime_sla", "unknown")} uptime, {scenario.project_context.requirements.get("performance_sla", "unknown")} performance
  
  Recent changes:
{chr(10).join([f"    - {entry}" for entry in changes_entries]) if changes_entries else "    - No recent changes"}

CONVERSATION HISTORY:
{chr(10).join([f"  {entry}" for entry in conversation_entries]) if conversation_entries else "  - No prior conversation"}

TOOL RESULTS:
{chr(10).join([f"  {entry}" for entry in tool_entries]) if tool_entries else "  - No tool results"}

CURRENT REQUEST:
  {user_request}"""
    
    return [
        scenario.standard_messages[0],  # Keep original system message
        {"role": "user", "content": json_content}
    ]

def test_openai(messages, model="gpt-4"):
    """Test with OpenAI API"""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    start_time = time.time()
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=16384,
        temperature=0.1
    )
    
    end_time = time.time()
    
    return {
        "response": response.choices[0].message.content,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        "time": end_time - start_time,
        # GPT-4.1: $2.00 input / $8.00 output per 1M tokens
        # Source: https://openai.com/api/pricing/
        "cost": (response.usage.prompt_tokens * 2.00 + response.usage.completion_tokens * 8.00) / 1000000
    }

def test_anthropic(messages, model="claude-3-5-sonnet-20241022"):
    """Test with Anthropic API"""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    start_time = time.time()
    
    # Convert to Anthropic format - filter out tool messages
    system_msg = ""
    user_messages = []
    
    for msg in messages:
        if msg["role"] == "system":
            system_msg = msg["content"]
        elif msg["role"] in ["user", "assistant"]:  # Only allow user/assistant for Anthropic
            user_messages.append(msg)
        # Skip tool messages as Anthropic doesn't support them in this format
    
    response = client.messages.create(
        model=model,
        system=system_msg,
        messages=user_messages,
        max_tokens=16384,
        temperature=0.1
    )
    
    end_time = time.time()
    
    return {
        "response": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        "time": end_time - start_time,
        # Claude Sonnet 4: $3.00 input / $15.00 output per 1M tokens
        # Source: https://docs.anthropic.com/en/docs/about-claude/models
        "cost": (response.usage.input_tokens * 3.00 + response.usage.output_tokens * 15.00) / 1000000
    }

def test_gemini(messages, model="gemini-1.5-pro"):
    """Test with Gemini API"""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model_instance = genai.GenerativeModel(model)
    start_time = time.time()
    
    # Convert to Gemini format
    prompt_parts = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            prompt_parts.append(f"System: {content}")
        elif role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")
    
    prompt = "\n\n".join(prompt_parts)
    
    response = model_instance.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=16384,
            temperature=0.1
        )
    )
    
    end_time = time.time()

    input_tokens = response.usage_metadata.prompt_token_count
    output_tokens = response.usage_metadata.candidates_token_count
    
    return {
        "response": response.text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "time": end_time - start_time,
        # Gemini 2.5 Pro: $1.25 input / $10.00 output per 1M tokens
        # Source: https://ai.google.dev/pricing
        "cost": (input_tokens * 1.25 + output_tokens * 10.00) / 1000000
    }

def run_test(format_name, format_func, scenario):
    """Run test for a specific format across all models"""
    print(f"\n{'='*60}")
    print(f"Testing: {format_name}")
    print(f"{'='*60}")
    
    messages = format_func(scenario)
    results = {}
    
    # Test GPT-4.1
    print(f"\n🤖 Testing GPT-4.1...")
    result = test_openai(messages, MODELS["gpt-4.1"])
    print(f"📊 Evaluating with GPT-4.1, Sonnet 4, Gemini 2.5...")
    quality = evaluate_response_quality(result['response'], scenario)
    result['quality'] = quality
    results["gpt-4.1"] = result
    print(f"✅ Success: {result['total_tokens']} tokens, ${result['cost']:.6f}, {result['time']:.2f}s")
    print(f"   Quality Score: {quality['overall']:.2f} (Spec: {quality.get('specificity', 0):.2f}, Pers: {quality.get('personalization', 0):.2f}, Action: {quality.get('actionability', 0):.2f}, Context: {quality.get('context_utilization', 0):.2f})")
    
    # Test Sonnet 4
    print(f"\n🤖 Testing Sonnet 4...")
    result = test_anthropic(messages, MODELS["sonnet-4"])
    print(f"📊 Evaluating with GPT-4.1, Sonnet 4, Gemini 2.5...")
    quality = evaluate_response_quality(result['response'], scenario)
    result['quality'] = quality
    results["sonnet-4"] = result
    print(f"✅ Success: {result['total_tokens']} tokens, ${result['cost']:.6f}, {result['time']:.2f}s")
    print(f"   Quality Score: {quality['overall']:.2f} (Spec: {quality['specificity']:.2f}, Pers: {quality['personalization']:.2f}, Action: {quality['actionability']:.2f}, Context: {quality['context_utilization']:.2f})")
    
    # Test Gemini 2.5
    print(f"\n🤖 Testing Gemini 2.5...")
    result = test_gemini(messages, MODELS["gemini-2.5"])
    print(f"📊 Evaluating with GPT-4.1, Sonnet 4, Gemini 2.5...")
    quality = evaluate_response_quality(result['response'], scenario)
    result['quality'] = quality
    results["gemini-2.5"] = result
    print(f"✅ Success: {result['total_tokens']} tokens, ${result['cost']:.6f}, {result['time']:.2f}s")
    print(f"   Quality Score: {quality['overall']:.2f} (Spec: {quality['specificity']:.2f}, Pers: {quality['personalization']:.2f}, Action: {quality['actionability']:.2f}, Context: {quality['context_utilization']:.2f})")
    
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

    # Use same models as testing for evaluation
    all_scores = []
    
    # GPT-4.1 evaluation
    gpt_result = test_openai([{"role": "user", "content": evaluation_prompt}], MODELS["gpt-4.1"])
    gpt_scores = _parse_evaluation_scores(gpt_result['response'])
    all_scores.append(gpt_scores)
    
    # Sonnet 4 evaluation  
    sonnet_result = test_anthropic([{"role": "user", "content": evaluation_prompt}], MODELS["sonnet-4"])
    sonnet_scores = _parse_evaluation_scores(sonnet_result['response'])
    all_scores.append(sonnet_scores)
    
    # Gemini 2.5 evaluation
    gemini_result = test_gemini([{"role": "user", "content": evaluation_prompt}], MODELS["gemini-2.5"])
    gemini_scores = _parse_evaluation_scores(gemini_result['response'])
    all_scores.append(gemini_scores)
    
    # Average scores across all three models
    averaged_scores = {}
    score_keys = ['specificity', 'personalization', 'actionability', 'context_utilization', 'overall']
    
    for key in score_keys:
        scores_for_key = [scores.get(key, 0.0) for scores in all_scores]
        averaged_scores[key] = sum(scores_for_key) / len(scores_for_key)
    
    return averaged_scores

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
        ("JSON Conversation (Factor 3)", format_json_conversation)
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
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"factor3_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n💾 Results saved to: {filename}")
    print("\n🎬 Perfect for video demonstration!")

if __name__ == "__main__":
    main()
