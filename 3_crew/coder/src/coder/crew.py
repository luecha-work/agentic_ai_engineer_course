from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class Coder():
    """Coder crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    @agent
    def coder(self) -> Agent:
        """ Creates the coder agent """
        return Agent(
            config=self.agents_config['coder'], # type: ignore[index]
            verbose=True,
            allow_code_execution=True,
            code_execution_mode='safe',
            max_execution_time=60,
            max_retry_limit=5,
        )
        
    @task
    def coding_task(self) -> Task:
        return Task(
            config=self.tasks_config['coding_task'], # type: ignore[index]
        )
        
    @crew
    def crew(self) -> Crew:
        """ Creates the coder crew """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
    