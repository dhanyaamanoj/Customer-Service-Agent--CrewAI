from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool
from crewai import Agent, Crew, Process, Task,LLM
from customer_agent.tools.custom_tool import UpdateMasterDataTool

tool = UpdateMasterDataTool(request_filepath=r'C:\Users\DHANYA MANOJ\OneDrive\Desktop\Final_Crew\customer_agent\knowledge\policy_service_requests.csv',
                            master_data_filepath=r'C:\Users\DHANYA MANOJ\OneDrive\Desktop\Final_Crew\customer_agent\knowledge\InsurancePolicy_Masterdata.csv')

result=tool.run()

 
#from customer_agent import PolicyDataUpdateTool

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

File_read_tool = FileReadTool(file_path=r"C:\Users\DHANYA MANOJ\OneDrive\Desktop\Final_Crew\customer_agent\knowledge\policy_service_requests.csv")
# policy_service_request=(r"C:\Users\DHANYA MANOJ\OneDrive\Desktop\Final_Crew\customer_agent\knowledge\policy_service_requests.csv")
# insurance_masterdata=(r"C:\Users\DHANYA MANOJ\OneDrive\Desktop\Techvantage\CREW_AI\customer_service_agent\knowledge\Insurance_Masterdata.csv")
# Update_tool= PolicyDataUpdateTool(request_file_path=policy_service_request, master_data_file_path=insurance_masterdata)
groq_llm=LLM(model="groq/llama-3.1-70b-versatile",
        api_key="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",temperature=0.4)

update=FileReadTool(file_path=r"C:\Users\DHANYA MANOJ\OneDrive\Desktop\Final_Crew\customer_agent\update_result.json")

@CrewBase
class CustomerAgent:
    """Customer  Agent Crew"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def reasoner(self) -> Agent:
        return Agent(
            config=self.agents_config['reasoner'],
            verbose=True,
            tools=[File_read_tool] 
        )

    @agent
    def executor(self) -> Agent:
        return Agent(
            config=self.agents_config['executor'],
            verbose=True,
            tools=[update]
              # Pass the tool object here, not the _run method
        )

    @agent
    def feedback_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['feedback_manager'],
            verbose=True,
            llm=groq_llm,
            output_file="output.md"
        )

    @task
    def reasoning_task(self) -> Task:
        return Task(
            config=self.tasks_config['reasoning_task'],
        )

    @task
    def execution_task(self) -> Task:
        return Task(
            config=self.tasks_config['execution_task'],
            output_file='result.json',
        )

    @task
    def feedback_task(self) -> Task:
        return Task(
            config=self.tasks_config['feedback_task'],
            output_file='feedback.csv'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Customer Policy Service Agent Crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,  # Sequential execution for proper task dependencies
            verbose=True,
        )
