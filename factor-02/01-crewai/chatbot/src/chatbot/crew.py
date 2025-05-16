from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from functools import cached_property
from typing import List

@CrewBase
class Chatbot():
    """DevOps and Engineering Knowledge Assistant chatbot"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @cached_property
    def knowledge_sources(self) -> List[BaseKnowledgeSource]:
        # Create text file knowledge source with relative paths from knowledge directory
        return [
            TextFileKnowledgeSource(
                file_paths=[
                    "code-review-guidelines.md",
                    "blue-green-deployment.md",
                    "error-rate-runbook.md",
                    "kubernetes-cluster-setup.md",
                    "database-outage.md"
                ],
            ),
        ]

    @agent
    def knowledge_researcher(self) -> Agent:
        """Create the knowledge researcher agent"""
        return Agent(
            config=self.agents_config['knowledge_researcher'],  # type: ignore[index]
            verbose=True,
            knowledge_sources=self.knowledge_sources,
        )

    @agent
    def devops_assistant(self) -> Agent:
        """Create the DevOps assistant agent"""
        return Agent(
            config=self.agents_config['devops_assistant'],  # type: ignore[index]
            verbose=True,
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
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            knowledge_sources=self.knowledge_sources,
        )
