from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import Any, List
from pydantic import BaseModel, Field
from crewai_tools import SerperDevTool

# from stock_picker.tools.push_tool import PushNotificationTool
from stock_picker.tools.send_mail import SendMailTool


class TrendingCompany(BaseModel):
    """A company that is in the news and attracting attention"""

    name: str = Field(description="The name of the company")
    ticker: str = Field(description="The ticker of the company")
    reason: str = Field(description="The reason why the company is trending")


class TrendingCompanyList(BaseModel):
    """A list of multiple trending companies that are in the news"""

    companies: List[TrendingCompany] = Field(
        description="The list of companies trending in the news"
    )


class TrendingCompanyResearch(BaseModel):
    """A company that has been researched and analyzed"""

    name: str = Field(description="Company name")
    market_position: str = Field(
        description="Current market position and competitive analysis"
    )
    future_outlook: str = Field(description="Future outlook and growth potential")
    investment_potential: str = Field(
        description="Investment potential and suitability for investment"
    )


class TrendingCompanyResearchList(BaseModel):
    """A list of multiple companies that have been researched and analyzed"""

    companies: List[TrendingCompanyResearch] = Field(
        description="The list of companies researched and analyzed"
    )


@CrewBase
class StockPicker:
    """StockPicker crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # @agent
    # def researcher(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['researcher'], # type: ignore[index]
    #         verbose=True
    #     )

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config["trending_company_finder"],  # type: ignore[index]
            tools=[SerperDevTool()],
        )

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["financial_researcher"],  # type: ignore[index]
        )

    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config["stock_picker"],  # type: ignore[index]
            tools=[SendMailTool()],
        )

    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config["find_trending_companies"],  # type: ignore[index]
            output_pydantic=TrendingCompanyList,
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config["research_trending_companies"],  # type: ignore[index]
            output_pydantic=TrendingCompanyResearchList,
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config["pick_best_company"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""

        manager: Agent = Agent(
            config=self.agents_config["manager"],  # type: ignore[index]
            allow_delegation=True,
        )

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager,
        )
