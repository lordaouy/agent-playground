from pydantic_models import BaseModel, Field
from typing import List, Optional


class SubTask(BaseModel):
    Sub_Task: str
    Agent: str
    Agent_Function: str
    Sub_Task_Output: Optional[str] = None
    Sub_Task_Output_Observation: Optional[str] = None
    Subtask_Status: Optional[str] = None

class Task(BaseModel):
    Task: str
    Task_Output: Optional[str] = None
    Task_Output_Observation: Optional[str] = None
    Task_Status: Optional[str] = None
    Sub_Tasks: Optional[List[SubTask]] = Field(default_factory=list)

class CurrentTask(BaseModel):
    Task: str
    Subtask: str

class AgentInput(BaseModel):
    agent_input: str
    Agent: str
    Agent_Function: str

class AgentOutput(BaseModel):
    agent_output: str
    Agent: str
    Agent_Function: str

class NextTask(BaseModel):
    Task: str
    Subtask: str

class NextAgentInput(BaseModel):
    agent_input: str
    Agent: str
    Agent_Function: str

class Plan(BaseModel):
    Tasks: List[Task]
    Overall_execution_of_the_plan: Optional[str] = None

class ShortTermMemory(BaseModel):
    Thought: Optional[str] = None
    Action: Optional[str] = None
    Observation: Optional[str] = None

class LongTermMemory(BaseModel):
    Thought: Optional[str] = None
    Action: Optional[str] = None
    Observation: Optional[str] = None

class OverallResponse(BaseModel):
    Plan: Plan
    Short_Term_Memory: ShortTermMemory = Field(alias="st_memory")
    Long_Term_Memory: LongTermMemory = Field(alias="lt_memory")

class OverallResponse1(BaseModel):
    Current_Task: CurrentTask
    Agent_Input: AgentInput
    Plan: Plan
    Short_Term_Memory: ShortTermMemory = Field(alias="st_memory")
    Long_Term_Memory: LongTermMemory = Field(alias="lt_memory")

class OverallResponse2(BaseModel):
    Agent_Output: AgentOutput
    Plan: Plan
    Short_Term_Memory: ShortTermMemory = Field(alias="st_memory")
    Long_Term_Memory: LongTermMemory = Field(alias="lt_memory")
    Next_Task: NextTask
    Next_Agent_Input: NextAgentInput