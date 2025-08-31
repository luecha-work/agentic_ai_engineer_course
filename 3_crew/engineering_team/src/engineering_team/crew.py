from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class EngineeringTeam:
    """EngineeringTeam crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def engineering_lead(self) -> Agent:
        return Agent(
            config=self.agents_config["engineering_lead"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def backend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["backend_engineer"],  # type: ignore[index]
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=240,
            max_retry_limit=5,
        )

    @agent
    def frontend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["frontend_engineer"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def test_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["test_engineer"],  # type: ignore[index]
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=240,
            max_retry_limit=5,
        )

    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config["design_task"],  # type: ignore[index]
        )

    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config["code_task"],  # type: ignore[index]
        )

    @task
    def frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config["frontend_task"],  # type: ignore[index]
        )

    @task
    def test_task(self) -> Task:
        return Task(
            config=self.tasks_config["test_task"],  # type: ignore[index]
        )

    # @agent
    # def manager(self):
    #     return Agent(
    #         role="Project Manager",
    #         goal="Distribute tasks to agents efficiently",
    #         backstory="An experienced team lead in multi-agent coordination.",
    #         llm=ChatOpenAI(model="gpt-4"),
    #     )

    # @crew
    # def engineering_team(self):
    #     return Crew(
    #         agents=self.agents,
    #         tasks=self.tasks,
    #         process=Process.react,
    #         manager_agent=self.manager(),
    #     )

    @crew
    def engineering_team(self) -> Crew:
        """Creates the EngineeringTeam crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
