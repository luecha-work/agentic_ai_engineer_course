from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from langchain_community.chat_models.ollama import ChatOllama
from typing import List

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class Debate:
    """Debate crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def debater(self) -> Agent:
        return Agent(
            config=self.agents_config["debater"], llm=ChatOllama(model="ollama/llama3.1"), verbose=True  # type: ignore[index]
        )

    @agent
    def judge(self) -> Agent:
        return Agent(
            config=self.agents_config["judge"], llm=ChatOllama(model="ollama/llama3.1"), verbose=True  # type: ignore[index]
        )

    @task
    def propose(self) -> Task:
        return Task(
            config=self.tasks_config["propose"],  # type: ignore[index]
        )

    @task
    def oppose(self) -> Task:
        return Task(
            config=self.tasks_config["oppose"],  # type: ignore[index]
        )

    @task
    def decide(self) -> Task:
        return Task(
            config=self.tasks_config["decide"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Debate crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
