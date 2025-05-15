from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from typing import List
import os
import logging

# Configure logging
log_level = logging.DEBUG if os.environ.get("DEVOPS_DEBUG", "").lower() in ["1", "true", "yes"] else logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('devops_assistant')

# Log debug status
if log_level == logging.DEBUG:
    logger.debug("Debug logging enabled")

# Fix import for both package mode and direct execution
try:
    from chatbot.config.api_config import get_openai_llm  # When installed as a package
except ImportError:
    from src.chatbot.config.api_config import get_openai_llm  # When running directly

@CrewBase
class Chatbot():
    """DevOps and Engineering Knowledge Assistant chatbot"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    @agent
    def knowledge_researcher(self) -> Agent:
        """Create the knowledge researcher agent"""
        # Create text file knowledge source with relative paths from knowledge directory
        knowledge_files = TextFileKnowledgeSource(
            file_paths=[
                "code-review-guidelines.md",
                "blue-green-deployment.md",
                "error-rate-runbook.md",
                "kubernetes-cluster-setup.md",
                "database-outage.md",
                "argocd.md"
            ]
        )
        
        # Log for debugging
        logger.info("Created knowledge source for knowledge_researcher")
                
        # Get OpenAI LLM
        openai_llm = get_openai_llm()
        
        return Agent(
            config=self.agents_config['knowledge_researcher'], # type: ignore[index]
            verbose=True,
            knowledge_sources=[knowledge_files],  # Pass the TextFileKnowledgeSource object
            llm=openai_llm
        )

    @agent
    def devops_assistant(self) -> Agent:
        """Create the DevOps assistant agent"""
        # Create text file knowledge source with relative paths from knowledge directory
        knowledge_files = TextFileKnowledgeSource(
            file_paths=[
                "code-review-guidelines.md",
                "blue-green-deployment.md",
                "error-rate-runbook.md",
                "kubernetes-cluster-setup.md",
                "database-outage.md",
                "argocd.md"
            ]
        )
        
        # Log for debugging
        logger.info("Created knowledge source for devops_assistant")
    
        # Get OpenAI LLM
        openai_llm = get_openai_llm()
        
        return Agent(
            config=self.agents_config['devops_assistant'], # type: ignore[index]
            verbose=True,
            knowledge_sources=[knowledge_files],  # Pass the TextFileKnowledgeSource object
            llm=openai_llm
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
        # Get OpenAI LLM for the crew
        openai_llm = get_openai_llm()

        knowledge_files = TextFileKnowledgeSource(
            file_paths=[
                "code-review-guidelines.md",
                "blue-green-deployment.md",
                "error-rate-runbook.md",
                "kubernetes-cluster-setup.md",
                "database-outage.md",
                "argocd.md"
            ]
        )

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
             knowledge_sources=[knowledge_files],
            verbose=True,
            llm=openai_llm
        )
