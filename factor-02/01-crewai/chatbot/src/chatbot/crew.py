from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from typing import List, Optional
import os
import sys
import logging
from pathlib import Path

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

# No custom directory handling needed - crewAI looks for files in the ./knowledge directory

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
                "database-outage.md"
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
                "database-outage.md"
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

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            llm=openai_llm
        )
        
    def ask(self, question: str) -> str:
        """
        Ask a question to the DevOps Knowledge Assistant
        
        Args:
            question: The user's question about DevOps or engineering topics
            
        Returns:
            str: The assistant's response
        """
        # Log information about the question for debugging
        logger.info(f"Processing question: {question}")
        
        # Check if knowledge files exist in standard location
        knowledge_dir = Path("knowledge")
        if knowledge_dir.exists():
            logger.info(f"Knowledge directory found at ./knowledge")
            # Check if required knowledge files exist
            for filename in [
                "code-review-guidelines.md",
                "blue-green-deployment.md",
                "error-rate-runbook.md",
                "kubernetes-cluster-setup.md",
                "database-outage.md"
            ]:
                file_path = knowledge_dir / filename
                if file_path.exists():
                    logger.info(f"Knowledge file exists: {filename}")
                else:
                    logger.warning(f"Knowledge file MISSING: {filename}")
        else:
            logger.warning("Knowledge directory not found in ./knowledge")
                
        # Run the crew with the user's question
        inputs = {
            "user_question": question
        }
        
        # Execute the crew and get the result
        try:
            result = self.crew().kickoff(inputs=inputs)
            return result
        except Exception as e:
            logger.error(f"Error running crew: {str(e)}")
            return f"I encountered an error while processing your question. Error details: {str(e)}"
