"""
Context formatting functions for Factor 3 testing
Each formatter converts a Scenario into a different context format for testing
"""

import json
from datetime import datetime
from typing import List, Dict, Any
from models import Scenario


def format_standard(scenario: Scenario) -> List[Dict[str, Any]]:
    """
    Standard message format (baseline)
    
    Returns the original OpenAI conversation format with tool calls.
    This represents the typical way developers structure AI conversations.
    LiteLLM handles tool call format translation automatically.
    
    Args:
        scenario: Test scenario with conversation history
    
    Returns:
        Original conversation messages (system + user + assistant + tool messages)
    """
    return scenario.standard_messages


def format_xml_structured(scenario: Scenario) -> List[Dict[str, Any]]:
    """
    XML Structured format - Factor 3's poster child
    
    Converts the entire conversation context into a single XML-structured message.
    This is the official Factor 3 recommendation for structured context.
    
    Structure:
    - <user_profile> with role, preferences, work history
    - <project_context> with tech stack, infrastructure, current state
    - <conversation_flow> with previous exchanges
    - <tool_results> with function call results
    - <current_request> with the user's actual request
    
    Args:
        scenario: Test scenario to format
    
    Returns:
        [system_message, single_structured_user_message]
    """
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


def format_document_centric(scenario: Scenario) -> List[Dict[str, Any]]:
    """
    Document-Centric format - True Factor 3 following official Anthropic docs
    
    Treats context as a retrieved document with natural language descriptions.
    This follows the official Factor 3 documentation pattern where context
    is presented as if retrieved from external sources.
    
    Structure:
    - <document> wrapper with natural language content
    - <user_profile> in conversational tone
    - <project_context> in readable format
    - <conversation_context> with dialogue history
    - <tool_results> with function outputs
    - <source> metadata about the document
    - <current_request> separate from the document
    
    Args:
        scenario: Test scenario to format
    
    Returns:
        [system_message, document_plus_request_message]
    """
    user_request = scenario.get_user_request()
    conversation_summary = scenario.get_conversation_flow()
    tool_results = scenario.get_tool_results()

    # Build document-centric structure with natural language
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


def format_compressed(scenario: Scenario) -> List[Dict[str, Any]]:
    """
    Compressed format - Minimal tokens but includes key context
    
    Attempts to preserve all essential context areas while minimizing token usage.
    Uses abbreviations and compact notation to fit maximum information
    in minimum space.
    
    Format: USER:role|PREF:preferences|PROJ:tech|VER:version|STATE:health|HIST:history|TOOLS:tool_results|REQ:request
    
    Args:
        scenario: Test scenario to format
    
    Returns:
        [modified_system_message, compressed_user_message]
    """
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
    
    # Create compressed representation with all key context areas
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


def format_markdown(scenario: Scenario) -> List[Dict[str, Any]]:
    """
    Markdown format - Clean, readable structure
    
    Uses markdown syntax for clear hierarchy and readability.
    Maintains comprehensive context coverage while being developer-friendly
    and easy to scan visually.
    
    Structure:
    - # Context and Current Request (main heading)
    - ## User Profile (role, style, expertise, history)
    - ## Project Context (repo, tech, infrastructure, status, requirements)
    - ### Recent Changes (version history)
    - ## Conversation History (previous exchanges)
    - ## Tool Results (function call outputs)
    - ## Current Request (actual user request)
    
    Args:
        scenario: Test scenario to format
    
    Returns:
        [system_message, markdown_formatted_message]
    """
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


# Format registry for easy access
FORMATS = {
    "Standard Messages (Baseline)": format_standard,
    "XML Structured (Factor 3)": format_xml_structured,
    "Document-Centric (Factor 3)": format_document_centric,
    "Compressed (Factor 3)": format_compressed,
    "Markdown (Factor 3)": format_markdown
}


def get_available_formats():
    """Return list of available format names"""
    return list(FORMATS.keys())


def apply_format(format_name: str, scenario: Scenario) -> List[Dict[str, Any]]:
    """Apply a specific format to a scenario"""
    if format_name not in FORMATS:
        raise ValueError(f"Unknown format: {format_name}. Available: {list(FORMATS.keys())}")
    
    return FORMATS[format_name](scenario)