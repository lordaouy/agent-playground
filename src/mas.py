from openai import BadRequestError
import streamlit as st

class MAS_orchestrator:
    def __init__(self, client, model, pydantic_models, st, sidebar_placeholder, ):
        self.client = client
        self.model = model
        self.pydantic_models = pydantic_models
        self.st = st
        self.sidebar_placeholder = sidebar_placeholder

    def get_initial_plan(self, industry, use_case, user_query):
        user_message = f"""You are a Task Decomposition Planner Agent. Your role is to analyze user requests and break them down into executable tasks using available AI agents and their functions.

        ### Instructions:
        1. **Analyze Request**: Parse the user's request to identify necessary high-level agents and their functions. Avoid unnecessary complexity.
        2. **Decompose Tasks**: Break down the request into clear task descriptions for each agent/function. Do not detail specific steps within each function.
        3. **Plan Creation**: Develop a sophisticated plan with the agents you have available, you decided howm many steps the plan should have to solve the problem using the agents you have at your disposal. A plan should have about 5-6 steps.  
        4. **Memory Utilization**:
        - **Short-Term Memory**: Use for planning and executing the current plan.
        - **Long-Term Memory**: Use for overall plan execution and incorporating learnings from past plans.
        5. Always output the plan, short-term memory and long-term memory.
        6. Create meaningful agent names insted of using numbered agents. so instead of Agent 1 it should be a meaningful name for the agent executing the task. 

        ### JSON Formatting:
        - Use triple backticks with `json` for all JSON content.
        - Start each section with `##` followed by the section name.
        - Ensure all JSON objects and arrays are properly closed with matching braces and commas.
        - Use double quotes for all keys and string values.
        - Do not include extra text outside the JSON sections.
        - After each JSON section, state 'JSON section complete.'

        ### Accessibility:
        - Provide perfectly formatted JSON to ensure compatibility with JSON readers.

        Use the following information to create the required agents and plan for the industry and use case here:

        Industry:
        {industry}

        Use case:
        {use_case}

        # INPUTS:

        - The only required input is the request and the agents_definition. If a plan is not included, you must create one and generate the short-term and long-term memory.

        ## Request (the overall task to solve) {{
        ```json
        {{ 
            "request": {{  
                "inbound_request": "{user_query}"
            }}  
        }}
        ```

        #Agent Definitions
        ```json
        {{    
            "Name of Agent 1": {{   
                "Definition": "The description of the agent",    
                "function_1": {{   
                    "name": "function_name",    
                    "task": "The task for the agent to execute"    
                }}   
            }},    
            "Name of Agent 2": {{   
                "Definition": "The description of the agent",    
                "function_1": {{   
                    "name": "function_name",    
                    "task": "The task for the agent to execute"    
                }}   
            }},
            // Add more agents as needed
        }}   
        ```

        OUTPUT:

        ##Plan (the plan to be executed)
        ```json
        {{
            "Tasks": [
                {{
                    "Task": "Description of Task 1",
                    "Task_Output": "Output of Task 1",
                    "Task_Output_Observation": "Observation of Task 1",
                    "Task_Status": "Status of Task 1, default should be blank",
                    "Sub_Tasks": [
                        {{
                            "Sub_Task": "Description of Subtask 1",
                            "Agent": "Agent Name",
                            "Agent_Function": "Function Name",
                            "Sub_Task_Output": "Output of Subtask 1",
                            "Sub_Task_Output_Observation": "Observation of Subtask 1",
                            "Subtask_Status": "Status of Subtask 1, default should be blank""
                        }},
                        {{
                            "Sub_Task": "Description of Subtask 2",
                            "Agent": "Agent Name",
                            "Agent_Function": "Function Name",
                            "Sub_Task_Output": "Output of Subtask 2",
                            "Sub_Task_Output_Observation": "Observation of Subtask 2",
                            "Subtask_Status": "Status of Subtask 2, default should be blank""
                        }}
                        // Add more Subtasks as needed
                    ]
                }},
                {{
                    "Task": "Description of Task 2",
                    "Task_Output": "Output of Task 2",
                    "Task_Output_Observation": "Observation of Task 2",
                    "Task_Status": "Status of Task 2, default should be blank"",
                    "Sub_Tasks": [
                        // Subtasks for Task 2
                    ]
                }}
                // Add more Tasks as needed
            ],
            "Overall_execution_of_the_plan": "In-Progress or Completed. Default should be blank"
        }}
        ```

        ##Short-Term Memory (used to generate thought, action, observation and can be used to make the current plan more efficient and optimized)
        ```json
        {{
        "st_memory": {{
            "Thought": "The initial idea",
            "Action": "The action taken",
            "Observation": "The observed output"
        }}
        }}
        ```

        ##Long-Term Memory (used to generate thought, action, observation and can be used to make the future plans more efficient and optimized. The information generated here is related to the overall plan and can be used to help optimize future plans with observation it has learned with the current plan.)
        ```json
        {{
        "lt_memory": {{
            "Thought": "The initial idea",
            "Action": "The action taken",
            "Observation": "The observed output"
        }}
        }}
        ```
        """

        try:
            loading_placeholder = self.st.empty()
            with self.st.spinner("Processing your query and generating initial agent composition and plan..."):
                completion = self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": user_message}
                    ],
                    response_format=self.pydantic_models.OverallResponse,
                )
            loading_placeholder.empty()
            event = completion.choices[0].message.parsed

            plan = event.Plan
            st_memory = event.Short_Term_Memory
            lt_memory = event.Long_Term_Memory

            plan_json = plan.model_dump_json(indent=2)
            st_memory_json = st_memory.model_dump_json(indent=2)
            lt_memory_json = lt_memory.model_dump_json(indent=2)

            return plan_json, st_memory_json, lt_memory_json

        except BadRequestError as e:
            print(f"API Request Failed: {e}")
            return None, None, None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None, None, None

    def get_initial_plan_message(self, plan_json, st_memory_json, lt_memory_json, st_tools):
        user_message = f"""Summarize the plan and provide it as a meaningful response back to the user on what the overall plan is and how it will be executed. Provide the response like it was the agent speaking back to the user on what it's going to do. Always start with the Agent name. Also state that you will use short-term memory and long-term memory to help with the planning and future plans.

        The plan: {plan_json}
        
        ### HTML Formatting:
        - Provide a header using a `<span>` with specific styles.
        - Ensure all HTML tags are properly closed.
        - Do not include HTML within JSON sections.

        Generate a chatbot message using markdown that includes an agent's message with a formatted example plan similar to the one below:

        **Important:** Do not include any code blocks or triple backticks in your response. Provide the content as plain markdown. 
        
        <span style="color:#4B9CD3; font-size:28px; font-weight:bold;">Planner Agent</span>

        <span style="color:#DAA520;">Hello! I'm here to help you outline a comprehensive plan for Marketing and Research. Here's an example to get you started:</span>

        ##### 📅 Project Plan

        - 🔍 Research market trends
            - **Agent:** Web Search Agent
            - **Function:** perform_search
        - 🏨 Select and recommend suitable venues
            - **Agent:** Venue Selection Agent
            - **Function:** select_venue
        - 🗓️ Create a detailed trip schedule
            - **Agent:** Scheduling Agent
            - **Function:** create_schedule
        - 💰 Calculate the overall trip budget
            - **Agent:** Budgeting Agent
            - **Function:** manage_budget
        - 🍽️ Arrange catering services if needed during the trip
            - **Agent:** Catering Agent
            - **Function:** arrange_catering
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": user_message}
                ],
            )

            event = completion.choices[0].message
            self.st.markdown(event.content, unsafe_allow_html=True)
            self.st.session_state.plan = plan_json if 'plan_json' in locals() else {}
            self.st.session_state.st_memory = st_memory_json if 'st_memory_json' in locals() else {}  
            self.st.session_state.lt_memory = lt_memory_json if 'lt_memory_json' in locals() else {} 

            if 'plan_json' in locals() and plan_json: 
                self.st.session_state.plan = plan_json   
                st_tools.update_sidebar(plan_json, self.st, self.sidebar_placeholder)

            self.st.markdown(  
                """  
                <hr style="border: none; height: 2px; background-color: white; width: 50%; margin-left: auto; margin-right: auto;">  
                """,  
                unsafe_allow_html=True  
            )  

            return event.content

        except BadRequestError as e:
            print(f"API Request Failed: {e}")
            return None, None, None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None, None, None

    def orchestrate_tasks_input(self, plan_json, st_memory_json, lt_memory_json):
        if not all([plan_json, st_memory_json, lt_memory_json]):
            print("Missing required inputs for AI Conductor.")
            return

        prompt_content = f"""You are the AI Conductor, responsible for orchestrating a team of specialized AI agents to achieve the user's goals effectively.

            ### Instructions:
            1. **Plan Execution**: 
                - Receive a plan with tasks and subtasks, specifying the agent and function for each.
                - Track the output and status of each task and subtask. Must be Successful, Unsuccessful, or In Progress.
                - When all subtasks are Completed or Successful, update the 'Task', 'Task_Output', 'Task_Output_Observation', 'Task_Status' to Successful.
                - The subtask being executed must remain In Progress.
                - Manage communication between agents.

            2. **Memory Utilization**:
                - **Short-Term Memory**: Orchestrate and execute the current plan, recording thoughts, actions, and observations.
                - **Long-Term Memory**: Maintain overall orchestration details and learnings from past plans to optimize future executions.

            ### JSON Formatting:
            - Enclose all JSON content within triple backticks and specify as `json`.
            - Start each section with `##` followed by the section name.
            - Ensure all JSON objects and arrays are properly closed with matching braces and commas.
            - Use double quotes for all keys and string values.
            - Do not include extra text outside the JSON sections.
            - Keep responses concise to avoid exceeding token limits.
            - Do not add unnecessary carriage returns.

            ### Critical JSON Formatting Rules:
            - All JSON objects and arrays must have matching braces.
            - Separate all key-value pairs with commas.
            - Use double quotes for both keys and string values.
            - Avoid trailing commas after the last key-value pair.
            - Validate JSON formatting before outputting.

            ### INSTRUCTION
            - Always output the Current Task, Agent Input, Plan, Short-Term Memory and Long-Term Memory

            ##Current Task
            ```json
            {{
                "Task": {{  
                    "Task": "Start with the first task in the plan",  
                    "Subtask": "Start with the first task in the plan" 
                }}  
            }}
            ```
            ##Plan
            ```json
            {plan_json}
            ```

            ##Short-Term Memory
            ```json
            {st_memory_json}
            ```

            ##Long-Term Memory
            ```json
            {lt_memory_json}
            ```

            #OUTPUTS:

            ##Current Task
            ```json
            {{
                "Task": {{
                    "Task": "The current task",
                    "Subtask": "The current subtask"
                    }}
            }}
            ```

            ##Agent Input
            ```json
            {{
                "Agent_Input": {{
                    "agent_input": "The task for the agent to execute.",
                    "Agent": "The agent that will execute the task",
                    "Agent_Function": "The function that the agent will execute for the task"
                    }}
            }}
            ```
            ##Plan (the plan to be executed)
                ```json
                {{
                    "Tasks": [
                        {{
                            "Task": "Description of Task 1",
                            "Task_Output": "The overall output if the task was successful or not, this may be blank if the task hasn't been executed yet.",
                            "Task_Output_Observation": "The thought and observation of the overall success of the tasks",
                            "Task_Status": "Successful, Unsuccessful, or In Progress; this may be blank if the task hasn't been executed yet. Must be In Progress if a sub-task is In Progress, can only change to Sucessful if all sub-task are sucessful",
                            "Sub_Tasks": [
                                {{
                                    "Sub_Task": "Description of Subtask 1",
                                    "Agent": "Agent Name",
                                    "Agent_Function": "The agent function to be used to execute the task",
                                    "Sub_Task_Output": "The overall output of the subtask if it was successful or not, this may be blank if the task hasn't been executed yet",
                                    "Sub_Task_Output_Observation": "The thought and observation of the overall success of the subtask, this may be blank if the task hasn't been executed yet",
                                    "Subtask_Status": "Successful or Unsuccessful; this may be blank if the task hasn't been executed yet"
                                }},
                                {{
                                    "Sub_Task": "Description of Subtask 2",
                                    "Agent": "Agent Name",
                                    "Agent_Function": "The agent function to be used to execute the task",
                                    "Sub_Task_Output": "The overall output of the subtask if it was successful or not, this may be blank if the task hasn't been executed yet",
                                    "Sub_Task_Output_Observation": "The thought and observation of the overall success of the subtask, this may be blank if the task hasn't been executed yet",
                                    "Subtask_Status": "Successful or Unsuccessful; this may be blank if the task hasn't been executed yet"
                                }}
                                // all other subtasks for Task 1
                            ]
                        }},
                        {{
                            "Task": "Description of Task 2",
                            "Task_Output": "The overall output if the task was successful or not, this may be blank if the task hasn't been executed yet.",
                            "Task_Output_Observation": "The thought and observation of the overall success of the tasks",
                            "Task_Status": "Successful, Unsuccessful, or In Progress; this may be blank if the task hasn't been executed yet. Must be In Progress if a sub-task is In Progress, can only change to Sucessful if all sub-task are sucessful",
                            "Sub_Tasks": [
                                // all other Subtasks for Task 2
                            ]
                        }}
                        // All other Tasks 
                    ],
                    "Overall_execution_of_the_plan": "In-Progress or Completed. When all sub-tasks have been executed, either successful or not successful, you must change this to Completed"
                }}
                ```

                ##Short-Term Memory
                ```json
                {{
                "st_memory": {{
                    "Thought": "The initial idea",
                    "Action": "The action taken",
                    "Observation": "The observed output"
                }}
                }}
                ```

                ##Long-Term Memory
                ```json
                {{
                "lt_memory": {{
                    "Thought": "The overall idea",
                    "Action": "The overall action taken",
                    "Observation": "The overall observed output"
                }}
                }}
                ```
                """
        try:
            loading_placeholder = self.st.empty()
            with self.st.spinner("Processing your query and generating initial agent composition and plan..."):
                completion = self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt_content}
                    ],
                    response_format=self.pydantic_models.OverallResponse1,  # Adjust if AI Conductor has a different response structure
                )

            loading_placeholder.empty()
            event = completion.choices[0].message.parsed

            # Debug: Print the AI Conductor's response
            print("----- Phase 2: AI Conductor Input-----")
            #print(event)
            plan = event.Plan
            current_task = event.Current_Task
            agent_input = event.Agent_Input
            st_memory = event.Short_Term_Memory
            lt_memory = event.Long_Term_Memory

            # Serialize the extracted data to JSON strings
            current_task_json = current_task.model_dump_json(indent=2)
            agent_input_json = agent_input.model_dump_json(indent=2)

            plan_json = plan.model_dump_json(indent=2)
            st_memory_json = st_memory.model_dump_json(indent=2)
            lt_memory_json = lt_memory.model_dump_json(indent=2)

            return current_task_json, agent_input_json, plan_json, st_memory_json, lt_memory_json

        except BadRequestError as e:
            print(f"API Request Failed: {e}")
        except Exception as e: 
            print(f"An unexpected error occurred: {e}")

    # ------------------- Message output from Phase 1
    def orchestrate_tasks_input_message(self, agent_input_json, plan_json, st_memory_json, lt_memory_json, st_tools):
        print("Inside 1.22 --------") 
        user_message = f"""Summarize the query and action of the agent and provide it as a meaningful response back to the user on what the agent is about to do. Provide the response like it was the agent speaking back to the user on what it's going to do. Always start with the Agent name. Agent Input: {agent_input_json}

                            ### HTML Formatting:
                            - Provide a header using a `<span>` with specific styles.
                            - Ensure all HTML tags are properly closed.
                            - Do not include HTML within JSON sections.
                            
                            Generate a chatbot message using markdown that includes an agent's message with a formatted example plan similar to the one below:

                            **Important:** Do not include any code blocks or triple backticks in your response. Provide the content as plain markdown. 

                            Example:
                            <span style="color:#4B9CD3; font-size:28px; font-weight:bold;">Planner Agent</span>

                            <span style="color:#DAA520;">Hello! I see you want to integrate product search functionality into the shopping assistant. Here's what I will do:</span>

                            ##### 🎯 Task
                                I will work on integrating a robust product search functionality that allows users to easily find and access products within the shopping assistant. This will include implementing search algorithms, indexing products, and providing relevant search results to enhance the user experience.

                            """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": user_message}
                ],
            )
            
            event = completion.choices[0].message

            self.st.markdown(event.content, unsafe_allow_html=True)

            

            self.st.session_state.plan = plan_json if 'plan_json' in locals() else {}
            self.st.session_state.st_memory = st_memory_json if 'st_memory_json' in locals() else {}  
            self.st.session_state.lt_memory = lt_memory_json if 'lt_memory_json' in locals() else {}

            if 'plan_json' in locals() and plan_json:  
                print("Inside 2 --------") 
                self.st.session_state.plan = plan_json
                st_tools.update_sidebar(plan_json, self.st, self.sidebar_placeholder)
            

            print("----- Phase 2: AI Conductor Input Message -----")

            return event.content

        except BadRequestError as e:
            print(f"API Request Failed: {e}")
            return None, None, None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None, None, None

    # ------------------- Phase 2: AI Conductor -------------------

    def orchestrate_tasks_output(self, current_task_json, agent_input_json, plan_json, st_memory_json, lt_memory_json):
        if not all([current_task_json, agent_input_json, plan_json, st_memory_json, lt_memory_json]):
            print("Missing required inputs for AI Conductor.")
            return

        prompt_content = f"""You are the AI Conductor, responsible for orchestrating a team of specialized AI agents to achieve the user's goals effectively.

                        ### Instructions:
                        1. **Plan Execution**: 
                        - Receive a plan with tasks and subtasks, specifying the agent and function for each.
                        - Track the output and status of each task and subtask. Must be Successful, Unsuccessful, or In Progress.
                        - When all subtasks are Completed or Sucessful, update the  'Task', 'Task_Output', 'Task_Output_Observation', 'Task_Status' to Successful.
                        - Manage communication between agents.
                        - Always output the Agent Output, Plan, Short-Term Memory, Long-Term Memory, Next Task and Next Agent Input
                        - when all task_status are Successfull or Completed, update the 'Overall execution of the plan' to Successful
                        - the agent_output MUST synthetic data that can help with the task being executed. It should contain the RAW synthetic data.
                        - The subtask being executed, must now be Sucessful, unless it failed and the next subtask must be set to In Progress.
                        - For any task that has a subtask as In Progress you must set the task status to In Progress, if all subtasks from that task is sucessful you must change the task status to Sucessful.

                        2. **Memory Utilization**:
                        - **Short-Term Memory**: Orchestrate and execute the current plan, recording thoughts, actions, and observations.
                        - **Long-Term Memory**: Maintain overall orchestration details and learnings from past plans to optimize future executions.

            ### JSON Formatting:
            - Enclose all JSON content within triple backticks and specify as `json`.
            - Start each section with `##` followed by the section name.
            - Ensure all JSON objects and arrays are properly closed with matching braces and commas.
            - Use double quotes for all keys and string values.
            - Do not include extra text outside the JSON sections.
            - Keep responses concise to avoid exceeding token limits.
            - Do not add unnecessary carriage returns.

            ### Critical JSON Formatting Rules:
            - All JSON objects and arrays must have matching braces.
            - Separate all key-value pairs with commas.
            - Use double quotes for both keys and string values.
            - Avoid trailing commas after the last key-value pair.
            - Validate JSON formatting before outputting.

            ### INSTRUCTION
            - Always output the Current Task, Agent Input, Plan, Short-Term Memory and Long-Term Memory

            ##Current Task
            ```json
            {current_task_json}
            ```
            ##Agent Input
            ```json
            {agent_input_json}
            ```
            ##Plan
            ```json
            {plan_json}
            ```

            ##Short-Term Memory
            ```json
            {st_memory_json}
            ```

            ##Long-Term Memory
            ```json
            {lt_memory_json}
            ```

            #OUTPUTS:
            
            ##Agent Output 
            ```json
                {{
                "Agent_Output": {{
                    "agent_output": "Generated very detailed synthetic data that can help with the task being executed. If the query is a database query, the agent_output should be generated synthetic data raw data retrieved from the database",  
                    "Agent": "The agent that executed the task",
                    "Agent Function": "the function executed"
                    }}
                }}
            ```
            ##Plan (the plan to be executed)
                ```json
                {{
                    "Tasks": [
                        {{
                            "Task": "Description of Task 1",
                            "Task_Output": "The agent_output",
                            "Task_Output_Observation": "The thought and observation of the overall success of the tasks",
                            "Task_Status": "Successful, Unsuccessful, or In Progress; this may be blank if the task hasn't been executed yet. Must be In Progress if a sub-task is In Progress, can only change to Sucessful if all sub-task are sucessful",
                            "Sub_Tasks": [
                                {{
                                    "Sub_Task": "Description of Subtask 1",
                                    "Agent": "Agent Name",
                                    "Agent_Function": "The agent function to be used to execute the task",
                                    "Sub_Task_Output": "The overall output of the subtask if it was successful or not, this may be blank if the task hasn't been executed yet",
                                    "Sub_Task_Output_Observation": "The thought and observation of the overall success of the subtask, this may be blank if the task hasn't been executed yet",
                                    "Subtask_Status": "Successful or Unsuccessful; this may be blank if the task hasn't been executed yet"
                                }},
                                {{
                                    "Sub_Task": "Description of Subtask 2",
                                    "Agent": "Agent Name",
                                    "Agent_Function": "The agent function to be used to execute the task",
                                    "Sub_Task_Output": "The overall output of the subtask if it was successful or not, this may be blank if the task hasn't been executed yet",
                                    "Sub_Task_Output_Observation": "The thought and observation of the overall success of the subtask, this may be blank if the task hasn't been executed yet",
                                    "Subtask_Status": "Successful or Unsuccessful; this may be blank if the task hasn't been executed yet"
                                }}
                                // all other subtasks for Task 1
                            ]
                        }},
                        {{
                            "Task": "Description of Task 2",
                            "Task_Output": "The overall output if the task was successful or not, this may be blank if the task hasn't been executed yet.",
                            "Task_Output_Observation": "The thought and observation of the overall success of the tasks",
                            "Task_Status": "Successful, Unsuccessful, or In Progress; this may be blank if the task hasn't been executed yet. Must be In Progress if a sub-task is In Progress, can only change to Sucessful if all sub-task are sucessful",
                            "Sub_Tasks": [
                                // all other Subtasks for Task 2
                            ]
                        }}
                        // All other Tasks 
                    ],
                    "Overall_execution_of_the_plan": "In-Progress or Completed. When all sub-tasks have been executed, either successful or not successful, you must change this to Completed"
                }}
                ```
                ##Short-Term Memory
                ```json
                {{
                "st_memory": {{
                    "Thought": "The initial idea",
                    "Action": "The action taken",
                    "Observation": "The observed output"
                }}
                }}
                ```
                ##Long-Term Memory
                ```json
                {{
                "lt_memory": {{
                    "Thought": "The overall idea",
                    "Action": "The overall action taken",
                    "Observation": "The overall observed output"
                }}
                }}
                ```
                ##Next Task
                ```json
                {{  
                "Task": {{  
                    "Task": "The next task to execute",  
                    "Subtask": "The next subtask to execute"
                    }}  
                }}
                ```
                ##Next Agent Input
                ```json
                {{
                    "Agent_Input": {{
                        "agent_input": "The next task for the agent to execute",
                        "Agent": "The agent that will execute the task",
                        "Agent_Function": "The function that the agent will execute for the task"
                        }}
                }}
                ```
                """
        try:
            loading_placeholder = self.st.empty()
            with self.st.spinner("Processing your query and generating initial agent composition and plan..."):
                completion = self.client.beta.chat.completions.parse(
                    model=self.model,
                messages=[
                    {"role": "user", "content": prompt_content}
                ],
                response_format=self.pydantic_models.OverallResponse2,  # Adjust if AI Conductor has a different response structure
            )
            loading_placeholder.empty()

            event = completion.choices[0].message.parsed

            # Debug: Print the AI Conductor's response
            print("----- Phase 3: AI Conductor Output -----")
            agent_output = event.Agent_Output
            plan = event.Plan
            st_memory = event.Short_Term_Memory
            lt_memory = event.Long_Term_Memory
            next_task = event.Next_Task
            next_agent_input = event.Next_Agent_Input


            # Serialize the extracted data to JSON strings
            agent_output_json = agent_output.model_dump_json(indent=2)
            plan_json = plan.model_dump_json(indent=2)
            st_memory_json = st_memory.model_dump_json(indent=2)
            lt_memory_json = lt_memory.model_dump_json(indent=2)
            next_task_json = next_task.model_dump_json(indent=2)
            next_agent_input_json = next_agent_input.model_dump_json(indent=2)

            print(plan_json)

            return agent_output_json, plan_json, st_memory_json, lt_memory_json, next_task_json, next_agent_input_json

        except BadRequestError as e:
            print(f"API Request Failed: {e}")
        except Exception as e: 
            print(f"An unexpected error occurred: {e}")

    # ------------------- Message output from Phase 3

    def orchestrate_tasks_output_message(self, agent_output_json, plan_json, st_memory_json, lt_memory_json, st_tools):
        user_message = f"""Summarize the output of the agent and provide it as a meaningful response back to the user on what the agent did and the output data. Do not talk about the generation of the synthetic data, instead present it like data that you were able to collect. Provide the response like it was the agent speaking back to the user on what it just did. Always start with the Agent name. Agent Input: {agent_output_json}

                            Use what is in the 

                            ### HTML Formatting:
                                - Provide a header using a `<span>` with specific styles.
                                - Ensure all HTML tags are properly closed.
                                - Do not include HTML within JSON sections.
                            
                            Generate a chatbot message using markdown that includes an agent's message with a formatted example plan similar to the one below make sure to update the information with the content of the agent input:

                            **Important:** Do not include any code blocks or triple backticks in your response. Provide the content as plain markdown. 

                            Example:
                                <span style="color:#DAA520;">Data analysis and retreival completed and successful</span>

                                ##### 📝 Data Used:
                                    - **Current Engagement Metrics:**
                                        - Website Visits: 15,000
                                        - Average Session Duration: 3 minutes 45 seconds
                                        - Bounce Rate: 50%
                                        - Conversion Rate: 2%

                                    - **Customer Feedback:**
                                        - *Customer 101:* "Great selection of products, but the website is a bit slow."
                                        - *Customer 102:* "Love the discounts and promotions!"
                                        - *Customer 103:* "Would like to see more personalized recommendations."

                                    - **Market Trends:**
                                        - Personalization: Yes
                                        - Mobile Optimization: Yes
                                        - Social Media Integration: Yes
                            """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": user_message}
                ],
            )

            event = completion.choices[0].message

            self.st.markdown(event.content, unsafe_allow_html=True)
            
            self.st.session_state.plan = plan_json if 'plan_json' in locals() else {}
            self.st.session_state.st_memory = st_memory_json if 'st_memory_json' in locals() else {}  
            self.st.session_state.lt_memory = lt_memory_json if 'lt_memory_json' in locals() else {}

            if 'plan_json' in locals() and plan_json:  
                self.st.session_state.plan = plan_json  
                st_tools.update_sidebar(plan_json, self.st, self.sidebar_placeholder)

            self.st.markdown(  
                """  
                <hr style="border: none; height: 2px; background-color: white; width: 50%; margin-left: auto; margin-right: auto;">  
                """,  
                unsafe_allow_html=True  
            )  

            print("----- Phase 2: AI Conductor Input Message -----")

            return event.content

        except BadRequestError as e:
            print(f"API Request Failed: {e}")
            return None, None, None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None, None, None

    def orchestrate_tasks_input_loop(self, agent_output_json, plan_json, st_memory_json, lt_memory_json, next_task_json, next_agent_input_json):
        if not all([agent_output_json, plan_json, st_memory_json, lt_memory_json, next_task_json, next_agent_input_json]):
            print("Missing required inputs for AI Conductor.")
            return
        
        prompt_content = f"""You are the AI Conductor, responsible for orchestrating a team of specialized AI agents to achieve the user's goals effectively.

        You are the AI Conductor, responsible for orchestrating a team of specialized AI agents to achieve the user's goals effectively.

                                        ### Instructions:
                                        1. **Plan Execution**: 
                                        - Receive a plan with tasks and subtasks, specifying the agent and function for each.
                                        - Track the output and status of each task and subtask. Must be Successful, Unsuccessful, or In Progress.
                                        - When all subtasks for that task are Completed or Successful, you must update the  'Task', 'Task_Output', 'Task_Output_Observation', 'Task_Status' to Successful.
                                        - when all task_status are Successfull or Completed, update the 'Overall execution of the plan' to Successful. Do not continue or make up a new agent or request.
                                        - Manage communication between agents.
                                        - Always output the Current Task, Agent Input, Plan (including the 'Overall execution of the plan'), Short-Term Memory, Long-Term Memory 
                                        
                                        - The subtask being executed must remain In Progress.
                                        - For any task that has a subtask as In Progress you must set the task status to In Progress, if all subtasks from that task is 'Successful' you must change the task status to 'Successful'.

                                        2. **Memory Utilization**:
                                        - **Short-Term Memory**: Orchestrate and execute the current plan, recording thoughts, actions, and observations.
                                        - **Long-Term Memory**: Maintain overall orchestration details and learnings from past plans to optimize future executions.

            ### JSON Formatting:
            - Enclose all JSON content within triple backticks and specify as `json`.
            - Start each section with `##` followed by the section name.
            - Ensure all JSON objects and arrays are properly closed with matching braces and commas.
            - Use double quotes for all keys and string values.
            - Do not include extra text outside the JSON sections.
            - Keep responses concise to avoid exceeding token limits.
            - Do not add unnecessary carriage returns.

            ### Critical JSON Formatting Rules:
            - All JSON objects and arrays must have matching braces.
            - Separate all key-value pairs with commas.
            - Use double quotes for both keys and string values.
            - Avoid trailing commas after the last key-value pair.
            - Validate JSON formatting before outputting.

            ##Current Task
            ```json
            {next_task_json}
            ```
            ##Next Agent Input
            ```json
            {next_agent_input_json}
            ```
            ##Plan
            ```json
            {plan_json}
            ```
            ##Short-Term Memory
            ```json
            {st_memory_json}
            ```
            ##Long-Term Memory
            ```json
            {lt_memory_json}
            ```

            #OUTPUTS:

            ##Current Task
            ```json
            {{
                "Task": {{
                    "Task": "The current task",
                    "Subtask": "The current subtask"
                    }}
            }}
            ```
            ##Agent Input
            ```json
            {{
                "Agent_Input": {{
                    "agent_input": "The task for the agent to execute.",
                    "Agent": "The agent that will execute the task",
                    "Agent_Function": "The function that the agent will execute for the task"
                    }}
            }}
            ```
            ##Plan (the plan to be executed)
            ```json
                {{
                    "Tasks": [
                        {{
                            "Task": "Description of Task 1",
                            "Task_Output": "The overall output if the task was successful or not, this may be blank if the task hasn't been executed yet.",
                            "Task_Output_Observation": "The thought and observation of the overall success of the tasks",
                            "Task_Status": "Successful, Unsuccessful, or In Progress; this may be blank if the task hasn't been executed yet. Must be In Progress if a sub-task is In Progress, can only change to Sucessful if all sub-task are sucessful",
                            "Sub_Tasks": [
                                {{
                                    "Sub_Task": "Description of Subtask 1",
                                    "Agent": "Agent Name",
                                    "Agent_Function": "The agent function to be used to execute the task",
                                    "Sub_Task_Output": "The overall output of the subtask if it was successful or not, this may be blank if the task hasn't been executed yet",
                                    "Sub_Task_Output_Observation": "The thought and observation of the overall success of the subtask, this may be blank if the task hasn't been executed yet",
                                    "Subtask_Status": "Successful or Unsuccessful; this may be blank if the task hasn't been executed yet"
                                }},
                                {{
                                    "Sub_Task": "Description of Subtask 2",
                                    "Agent": "Agent Name",
                                    "Agent_Function": "The agent function to be used to execute the task",
                                    "Sub_Task_Output": "The overall output of the subtask if it was successful or not, this may be blank if the task hasn't been executed yet",
                                    "Sub_Task_Output_Observation": "The thought and observation of the overall success of the subtask, this may be blank if the task hasn't been executed yet",
                                    "Subtask_Status": "Successful or Unsuccessful; this may be blank if the task hasn't been executed yet"
                                }}
                                // all other subtasks for Task 1
                            ]
                        }},
                        {{
                            "Task": "Description of Task 2",
                            "Task_Output": "The overall output if the task was successful or not, this may be blank if the task hasn't been executed yet.",
                            "Task_Output_Observation": "The thought and observation of the overall success of the tasks",
                            "Task_Status": "Successful, Unsuccessful, or In Progress; this may be blank if the task hasn't been executed yet. Must be In Progress if a sub-task is In Progress, can only change to Sucessful if all sub-task are sucessful",
                            "Sub_Tasks": [
                                // all other Subtasks for Task 2
                            ]
                        }}
                        // All other Tasks 
                    ],
                    "Overall_execution_of_the_plan": "In-Progress or Completed. When all sub-tasks have been executed, either successful or not successful, you must change this to Completed"
                }}
                ```
                ##Short-Term Memory
                ```json
                {{
                "st_memory": {{
                    "Thought": "The initial idea",
                    "Action": "The action taken",
                    "Observation": "The observed output"
                }}
                }}
                ```
                ##Long-Term Memory
                ```json
                {{
                "lt_memory": {{
                    "Thought": "The overall idea",
                    "Action": "The overall action taken",
                    "Observation": "The overall observed output"
                }}
                }}
                ```
                """
        try:
            loading_placeholder = self.st.empty()
            with self.st.spinner("Processing your query and generating initial agent composition and plan..."):  
                completion = self.client.beta.chat.completions.parse(
                    model=self.model,
                messages=[
                        {"role": "user", "content": prompt_content}
                    ],
                    response_format=self.pydantic_models.OverallResponse1,  # Adjust if AI Conductor has a different response structure
                )
            loading_placeholder.empty()

            event = completion.choices[0].message.parsed

            # Debug: Print the AI Conductor's response
            print("----- Phase 4: AI Conductor Input 2 Loop-----")
            #print(event)
            plan = event.Plan
            current_task = event.Current_Task
            agent_input = event.Agent_Input
            st_memory = event.Short_Term_Memory
            lt_memory = event.Long_Term_Memory

            # Serialize the extracted data to JSON strings
            current_task_json = current_task.model_dump_json(indent=2)
            agent_input_json = agent_input.model_dump_json(indent=2)

            plan_json = plan.model_dump_json(indent=2)
            st_memory_json = st_memory.model_dump_json(indent=2)
            lt_memory_json = lt_memory.model_dump_json(indent=2)

            return current_task_json, agent_input_json, plan_json, st_memory_json, lt_memory_json

        except BadRequestError as e:
            print(f"API Request Failed: {e}")
        except Exception as e: 
            print(f"An unexpected error occurred: {e}")

    def orchestrate_tasks_output_loop(self, current_task_json, agent_input_json, plan_json, st_memory_json, lt_memory_json):
        if not all([current_task_json, agent_input_json, plan_json, st_memory_json, lt_memory_json]):
            print("Missing required inputs for AI Conductor.")
            return

        prompt_content = f"""You are the AI Conductor, responsible for orchestrating a team of specialized AI agents to achieve the user's goals effectively.

                                ### Instructions:
                                1. **Plan Execution**: 
                                - Receive a plan with tasks and subtasks, specifying the agent and function for each.
                                - Track the output and status of each task and subtask. Must be Successful, Unsuccessful, or In Progress.
                                - When all subtasks are Completed or Sucessful, update the  'Task', 'Task_Output', 'Task_Output_Observation', 'Task_Status' to Successful.
                                - when all task_status are Successfull or Completed, update the 'Overall execution of the plan' to Successful. Do not continue or make up a new agent or request.
                                - Manage communication between agents.
                                - Always output the Agent Output, Plan (Plan (including the 'Overall execution of the plan'), Short-Term Memory, Long-Term Memory, Next Task and Next Agent Input
                                - If subtask status or task status is Successful or Completed, you may move on the the next agent in the plan and update the next agent and next input agent, if unsuccessful you may call the same task again with another agent_input.
                                - if there are no tasks left or next agent input is none, or all tasks in the current plan have been completed, you must update 'Overall execution of the plan' to Successful
                                - the agent_output MUST generate very detailed synthetic data that can help with the task being executed. It should contain the RAW synthetic data.
                                - The subtask being executed, must now be Sucessful, unless it failed and the next subtask must be set to In Progress.

                        2. **Memory Utilization**:
                        - **Short-Term Memory**: Orchestrate and execute the current plan, recording thoughts, actions, and observations.
                        - **Long-Term Memory**: Maintain overall orchestration details and learnings from past plans to optimize future executions.

            ### JSON Formatting:
            - Enclose all JSON content within triple backticks and specify as `json`.
            - Start each section with `##` followed by the section name.
            - Ensure all JSON objects and arrays are properly closed with matching braces and commas.
            - Use double quotes for all keys and string values.
            - Do not include extra text outside the JSON sections.
            - Keep responses concise to avoid exceeding token limits.
            - Do not add unnecessary carriage returns.

            ### Critical JSON Formatting Rules:
            - All JSON objects and arrays must have matching braces.
            - Separate all key-value pairs with commas.
            - Use double quotes for both keys and string values.
            - Avoid trailing commas after the last key-value pair.
            - Validate JSON formatting before outputting.

            ### INSTRUCTION
            - Always output the Current Task, Agent Input, Plan, Short-Term Memory and Long-Term Memory

            ##Current Task
            ```json
            {current_task_json}
            ```
            ##Agent Input
            ```json
            {agent_input_json}
            ```
            ##Plan
            ```json
            {plan_json}
            ```

            ##Short-Term Memory
            ```json
            {st_memory_json}
            ```

            ##Long-Term Memory
            ```json
            {lt_memory_json}
            ```

            #OUTPUTS:
            
            ##Agent Output 
            ```json
                {{
                "Agent_Output": {{
                    "agent_output": "Always use the Task_Output data from the previous task and  generate detailed synthetic data that can help with the task being executed. If the query is a database query, the agent_output MUST generate synthetic raw data retrieved from a database"  
                    "Agent": "The agent that executed the task",
                    "Agent Function": "the function executed"
                    }}
                }}
            ```
            ##Plan (the plan to be executed)
                ```json
                {{
                    "Tasks": [
                        {{
                            "Task": "Description of Task 1",
                            "Task_Output": "The overall output if the task was successful or not, this may be blank if the task hasn't been executed yet.",
                            "Task_Output_Observation": "The thought and observation of the overall success of the tasks",
                            "Task_Status": "Successful, Unsuccessful, or In Progress; this may be blank if the task hasn't been executed yet. Must be In Progress if a sub-task is In Progress, can only change to Sucessful if all sub-task are sucessful",
                            "Sub_Tasks": [
                                {{
                                    "Sub_Task": "Description of Subtask 1",
                                    "Agent": "Agent Name",
                                    "Agent_Function": "The agent function to be used to execute the task",
                                    "Sub_Task_Output": "The overall output of the subtask if it was successful or not, this may be blank if the task hasn't been executed yet",
                                    "Sub_Task_Output_Observation": "The thought and observation of the overall success of the subtask, this may be blank if the task hasn't been executed yet",
                                    "Subtask_Status": "Successful or Unsuccessful; this may be blank if the task hasn't been executed yet"
                                }},
                                {{
                                    "Sub_Task": "Description of Subtask 2",
                                    "Agent": "Agent Name",
                                    "Agent_Function": "The agent function to be used to execute the task",
                                    "Sub_Task_Output": "The overall output of the subtask if it was successful or not, this may be blank if the task hasn't been executed yet",
                                    "Sub_Task_Output_Observation": "The thought and observation of the overall success of the subtask, this may be blank if the task hasn't been executed yet",
                                    "Subtask_Status": "Successful or Unsuccessful; this may be blank if the task hasn't been executed yet"
                                }}
                                // all other subtasks for Task 1
                            ]
                        }},
                        {{
                            "Task": "Description of Task 2",
                            "Task_Output": "The overall output if the task was successful or not, this may be blank if the task hasn't been executed yet.",
                            "Task_Output_Observation": "The thought and observation of the overall success of the tasks",
                            "Task_Status": "Successful, Unsuccessful, or In Progress; this may be blank if the task hasn't been executed yet. Must be In Progress if a sub-task is In Progress, can only change to Sucessful if all sub-task are sucessful",
                            "Sub_Tasks": [
                                // all other Subtasks for Task 2
                            ]
                        }}
                        // All other Tasks 
                    ],
                    "Overall_execution_of_the_plan": "In-Progress or Completed. When all sub-tasks have been executed, either successful or not successful, you must change this to Completed"
                }}
                ```
                ##Short-Term Memory
                ```json
                {{
                "st_memory": {{
                    "Thought": "The initial idea",
                    "Action": "The action taken",
                    "Observation": "The observed output"
                }}
                }}
                ```
                ##Long-Term Memory
                ```json
                {{
                "lt_memory": {{
                    "Thought": "The overall idea",
                    "Action": "The overall action taken",
                    "Observation": "The overall observed output"
                }}
                }}
                ```
                ##Next Task
                ```json
                {{  
                "Task": {{  
                    "Task": "The next task to execute",  
                    "Subtask": "The next subtask to execute"
                    }}  
                }}
                ```
                ##Next Agent Input
                ```json
                {{
                    "Agent_Input": {{
                        "agent_input": "The next task for the agent to execute",
                        "Agent": "The agent that will execute the task",
                        "Agent_Function": "The function that the agent will execute for the task"
                        }}
                }}
                ```
                """
        try:
            loading_placeholder = self.st.empty()
            loading_placeholder = self.st.empty()
            with self.st.spinner("Processing your query and generating initial agent composition and plan..."):
                completion = self.client.beta.chat.completions.parse(
                    model=self.model,
                messages=[
                    {"role": "user", "content": prompt_content}
                ],
                response_format=self.pydantic_models.OverallResponse2,  # Adjust if AI Conductor has a different response structure
            )
            loading_placeholder.empty()

            event = completion.choices[0].message.parsed

            # Debug: Print the AI Conductor's response
            print("----- Phase 3: AI Conductor Output -----")
            #print(event)
            agent_output = event.Agent_Output
            plan = event.Plan
            st_memory = event.Short_Term_Memory
            lt_memory = event.Long_Term_Memory
            next_task = event.Next_Task
            next_agent_input = event.Next_Agent_Input

            # Serialize the extracted data to JSON strings
            agent_output_json = agent_output.model_dump_json(indent=2)
            plan_json = plan.model_dump_json(indent=2)
            st_memory_json = st_memory.model_dump_json(indent=2)
            lt_memory_json = lt_memory.model_dump_json(indent=2)
            next_task_json = next_task.model_dump_json(indent=2)
            next_agent_input_json = next_agent_input.model_dump_json(indent=2)

            return agent_output_json, plan_json, st_memory_json, lt_memory_json, next_task_json, next_agent_input_json

        except BadRequestError as e:
            print(f"API Request Failed: {e}")
        except Exception as e: 
            print(f"An unexpected error occurred: {e}")


    def summarize_final_output(self, plan_json, st_memory_json, lt_memory_json, st_tools):
        user_message = f""""Summarize the output of the entire plan and explain everything that you did to generate a final response and solution. Provide the response like it was the planner agent speaking back to the user. Agent Input: {plan_json}
                        
                        ### HTML Formatting:
                        - Provide a header using a `<span>` with specific styles.
                        - Ensure all HTML tags are properly closed.
                        - Do not include HTML within JSON sections.
                        
                        Generate a chatbot message using markdown that includes an agent's message with a formatted example plan similar to the one below:

                        **Important:** Do not include any code blocks or triple backticks in your response. Provide the content as plain markdown. 

                        Example:

                        The goal was to find the lowest price for an Xbox. The approach included identifying popular e-commerce websites, fetching and comparing prices, finding discounts, and re-evaluating to arrive at the lowest price after applying discounts. The expected outcome was to determine the best possible price across the identified websites.

                        🛠️ Agents and Task Execution Summary

                        Task	Agent	Function	Status	Output
                        🔍 Identify popular e-commerce websites	WebsiteIdentifierAgent	identifyWebsites	✅ Successful	Successfully identified popular e-commerce websites: Amazon, eBay, Walmart, Best Buy, Target.
                        🛒 Search for Xbox on identified websites	PriceFetcherAgent	fetchPrices	✅ Successful	Fetched prices from Amazon (349.99), eBay (340.0), Walmart (342.5), Best Buy (345.99), Target (348.0).
                        📊 Compare the prices fetched	PriceComparerAgent	comparePrices	✅ Successful	eBay has the lowest price: 340.0.
                        🏷️ Find discount codes or offers on websites	DiscountFinderAgent	findDiscounts	✅ Successful	Found discount codes on Amazon (SAVE10 for $10 off).
                        💸 Apply discounts and re-evaluate the lowest price	PriceReevaluationAgent	reevaluatePricesWithDiscounts	✅ Successful	After applying the discount, Amazon has the lowest price: 339.99.
                        📋 Generate final report of the lowest price for Xbox	ReportGeneratorAgent	generateReport	✅ Successful	The lowest price for Xbox, after applying discounts, is 339.99 at Amazon.

                                        
                        🏁 Overall Execution Summary

                        The process began by identifying major e-commerce platforms where an Xbox could be purchased. Prices were gathered for the Xbox from each site, revealing that eBay initially offered the lowest price. However, a discount code found for Amazon changed the dynamics. By applying the SAVE10 discount on Amazon, the price dropped below eBay's offer.
                        By re-evaluating the prices with available discounts, it was concluded that Amazon provides the best deal at $339.99. The final report encapsulates this finding, advising that purchasing the Xbox from Amazon after applying the discount code yields the lowest price.
                        This systematic approach ensured all potential savings were considered, guiding the consumer to make an informed purchasing decision.
                        """
        try:
            completion = self.client.chat.completions.create(
                model="GPT4o",  # Replace with your actual model deployment name
                messages=[
                    {"role": "user", "content": user_message}
                ],
            )

            event = completion.choices[0].message
            self.st.markdown(event.content, unsafe_allow_html=True)

            self.st.session_state.plan = plan_json if 'plan_json' in locals() else {}
            self.st.session_state.st_memory = st_memory_json if 'st_memory_json' in locals() else {}  
            self.st.session_state.lt_memory = lt_memory_json if 'lt_memory_json' in locals() else {} 

            if 'plan_json' in locals() and plan_json:  
                self.st.session_state.plan = plan_json   
                st_tools.update_sidebar(plan_json, self.st, self.sidebar_placeholder) 


            self.st.markdown(  
                """  
                <hr style="border: none; height: 2px; background-color: white; width: 50%; margin-left: auto; margin-right: auto;">  
                """,  
                unsafe_allow_html=True  
            )  
    
            return event.content

        except BadRequestError as e:
            print(f"API Request Failed: {e}")
            return None, None, None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None, None, None
