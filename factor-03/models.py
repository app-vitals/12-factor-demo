"""
Data models for Factor 3 testing framework
Contains UserProfile, ProjectContext, WorkHistoryItem, and Scenario classes
"""

import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class WorkHistoryItem:
    """Represents a single work history entry for a user"""
    type: str
    result: str
    date: str
    duration: Optional[str] = None
    notes: Optional[str] = None
    target: Optional[str] = None    # For migrations
    issue: Optional[str] = None     # For incidents
    version: Optional[str] = None   # For deployments
    
    def to_natural_language(self) -> str:
        """Convert to human-readable format"""
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
    """User context including role, preferences, and work history"""
    name: str
    role: str
    team: str
    preferences: str
    specialization: str
    history: List[WorkHistoryItem]
    
    def to_xml_format(self) -> str:
        """Format user profile as XML for structured context"""
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
        """Format user profile as natural language for document-centric format"""
        history_text = "\n".join([f"  - {item.to_natural_language()}" for item in self.history])
        return f"""{self.name} is a {self.role} on the {self.team} team.
  
  Working style: {self.preferences}
  Expertise: {self.specialization}
  
  Recent work history:
{history_text if history_text else '  - No work history available'}"""


@dataclass
class ProjectContext:
    """Project infrastructure and state information"""
    repo: str
    tech_stack: List[str]
    current_version: str
    infrastructure: Dict[str, Any]
    current_state: Dict[str, Any]
    requirements: Dict[str, Any]
    recent_changes: List[Dict[str, str]]
    
    def to_xml_format(self) -> str:
        """Format project context as XML for structured context"""
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
        """Format project context as natural language for document-centric format"""
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
    """Test scenario with messages, context, and evaluation criteria"""
    name: str
    standard_messages: List[Dict[str, Any]]
    evaluation_criteria: Dict[str, List[str]]
    user_profile: UserProfile
    project_context: ProjectContext
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Scenario':
        """Create Scenario from JSON data"""
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
        """Extract the final user request from the conversation"""
        return self.standard_messages[-1]["content"]
    
    def get_conversation_flow(self) -> List[str]:
        """Extract conversation history (excluding system and final user message)"""
        conversation_flow = []
        for msg in self.standard_messages[1:-1]:  # Skip system and final user message
            if msg["role"] == "user":
                conversation_flow.append(f"User: {msg['content']}")
            elif msg["role"] == "assistant" and "tool_calls" not in msg:
                conversation_flow.append(f"Assistant: {msg['content']}")
        return conversation_flow
    
    def get_tool_results(self) -> List[Dict[str, str]]:
        """Extract tool call results from the conversation"""
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


def load_test_scenarios() -> List[Scenario]:
    """Load test scenarios from JSON file and convert to Scenario objects"""
    with open('scenarios.json', 'r') as f:
        data = json.load(f)
    return [Scenario.from_dict(item) for item in data]
