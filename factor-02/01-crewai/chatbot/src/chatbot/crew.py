from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from typing import List, Optional
import os

# Fix import for both package mode and direct execution
try:
    from chatbot.config.api_config import get_anthropic_llm  # When installed as a package
except ImportError:
    from src.chatbot.config.api_config import get_anthropic_llm  # When running directly

@CrewBase
class Chatbot():
    """DevOps and Engineering Knowledge Assistant chatbot"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    @agent
    def knowledge_researcher(self) -> Agent:
        """Create the knowledge researcher agent"""
        # Create text file knowledge sources
        knowledge_files = TextFileKnowledgeSource(
            file_paths=[
                "code-review-guidelines.md",
                "blue-green-deployment.md",
                "error-rate-runbook.md",
                "kubernetes-cluster-setup.md",
                "database-outage.md"
            ]
        )
        
        # Get Anthropic LLM
        anthropic_llm = get_anthropic_llm()
        
        return Agent(
            config=self.agents_config['knowledge_researcher'], # type: ignore[index]
            verbose=True,
            knowledge_sources=[knowledge_files],
            llm=anthropic_llm
        )

    @agent
    def devops_assistant(self) -> Agent:
        """Create the DevOps assistant agent"""
        # Create text file knowledge sources
        knowledge_files = TextFileKnowledgeSource(
            file_paths=[
                "code-review-guidelines.md",
                "blue-green-deployment.md",
                "error-rate-runbook.md",
                "kubernetes-cluster-setup.md"
            ]
        )
        
        # Get Anthropic LLM
        anthropic_llm = get_anthropic_llm()
        
        return Agent(
            config=self.agents_config['devops_assistant'], # type: ignore[index]
            verbose=True,
            knowledge_sources=[knowledge_files],
            llm=anthropic_llm
        )

    @task
    def research_query(self) -> Task:
        """Create the research query task"""
        return Task(
            config=self.tasks_config['research_query'], # type: ignore[index]
        )

    @task
    def formulate_answer(self) -> Task:
        """Create the formulate answer task"""
        return Task(
            config=self.tasks_config['formulate_answer'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the DevOps Knowledge Assistant crew"""
        # Set dummy OpenAI key to prevent errors
        os.environ["OPENAI_API_KEY"] = "dummy_key"
        
        # Get Anthropic LLM for the crew
        anthropic_llm = get_anthropic_llm()

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            llm=anthropic_llm
        )
        
    def ask(self, question: str) -> str:
        """
        Ask a question to the DevOps Knowledge Assistant
        
        Args:
            question: The user's question about DevOps or engineering topics
            
        Returns:
            str: The assistant's response
        """
        # Set dummy OpenAI key to prevent errors
        os.environ["OPENAI_API_KEY"] = "dummy_key"
        
        # Run the crew with the user's question
        inputs = {
            "user_question": question
        }
        
        # Execute the crew and get the result
        result = self.crew().kickoff(inputs=inputs)
        
        # Return the answer from the final task
        return result
