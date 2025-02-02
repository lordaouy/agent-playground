import json, os, streamlit as st
from openai import AzureOpenAI

from src.tools import StreamlitTools, GeneralTools
from src.mas import MAS_orchestrator
import src.pydantic_models as pydantic_models
import src.templates as templates

# Render the top bar
sidebar_placeholder = st.sidebar.empty() 

# Sidebar Configuration  
config_container = st.sidebar.container()  # Create the container and assign it to a variable  

with config_container:  
    st.header("Azure OpenAI Configuration")  
    api_key = st.text_input("API Key", type="password", key="api_key")  
    endpoint = st.text_input("Endpoint URL", placeholder="https://your-endpoint.openai.azure.com/", key="endpoint_url")  
    deployment_name = st.text_input("Model Name", value="gpt-4o-global", key="model_name")  
    use_environment_key = st.checkbox("Use Environment Key", key="use_environment_key", value=True) 
    client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_deployment=deployment_name,
            api_key=api_key,
            api_version="2024-08-01-preview"
        )    
  
    # API Key Input or Use Environment Key (.env file)
    if use_environment_key:  
        client = AzureOpenAI(
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_key=os.getenv('AZURE_OPENAI_KEY'),
            azure_deployment=os.getenv('AZURE_OPENAI_MODEL'),
            api_version="2024-08-01-preview"
        ) 

scenario_container = st.sidebar.container()  # Create the container and assign it to a variable
model_name = deployment_name if deployment_name else os.getenv('AZURE_OPENAI_MODEL')  
with scenario_container:  
    st.header("Scenario")  
    industry = st.text_input("Industry", placeholder="e.g., Healthcare, Finance", key="industry")  
    use_case = st.text_input("Use Case", placeholder="e.g., Chatbot, Data Analysis", key="use_case")  

# Initialize session state for plan and plan history
if 'plan' not in st.session_state:
    st.session_state.plan = {}
    st.session_state.plan_history = []
    st.session_state.st_memory = {}
    st.session_state.lt_memory = {}
    st_tools = StreamlitTools().update_sidebar(st.session_state.plan, st, sidebar_placeholder)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Create placeholders for the UI elements
title_placeholder = st.empty()
input_placeholder = st.empty()
button_placeholder = st.empty()

title_placeholder.title("Azure Multi-Agent Playground")
# Create a text input for the user's query
user_query = input_placeholder.text_input("Enter your query:", "", key="user_query")

# Load the GIF once and store it in session state  
if 'gif_base64' not in st.session_state:  
    st.session_state['gif_base64'] = GeneralTools().get_gif_as_base64("agent_anim_v2.gif")  
  
gif_base64 = st.session_state['gif_base64']  
  
# Display the GIF  
gif_placeholder = st.empty()  
gif_placeholder.markdown(  
    f"""  
    <div style="text-align: center;">  
        <img src="data:image/gif;base64,{gif_base64}" alt="Agent Animation" style="width:100%; max-width:800px;" loop autoplay/>  
    </div>  
    """,  
    unsafe_allow_html=True  
)  
instructions_placeholder = st.empty()
instructions_placeholder.markdown(
    templates.instructions_placeholder,
    unsafe_allow_html=True
)

# Create a Submit button  
submit_clicked = button_placeholder.button("Submit")  

# Create a placeholder for the warning message  
warning_placeholder = st.empty()  

# Create a Submit button
if __name__ == "__main__":   # Phase 1: Get the initial plan 
    if submit_clicked:
        if user_query and (use_environment_key or (api_key.strip() and deployment_name.strip() and endpoint.strip())):
            # Clear placeholders
            title_placeholder.empty()
            input_placeholder.empty()
            button_placeholder.empty()
            gif_placeholder.empty()
            instructions_placeholder.empty()

            # Setup the MAS orchestrator

            mas_orchestrator = MAS_orchestrator(client, model_name, pydantic_models, st, sidebar_placeholder)

            plan_json, st_memory_json, lt_memory_json = mas_orchestrator.get_initial_plan(industry, use_case, user_query)
            st.session_state.plan = plan_json

            st_tools = StreamlitTools()
            st_tools.update_sidebar(plan_json, st, sidebar_placeholder)
            
            user_message = mas_orchestrator.get_initial_plan_message(plan_json, st_memory_json, lt_memory_json, st_tools)
            print(user_message)

            current_task_json, agent_input_json, plan_json, st_memory_json, lt_memory_json = mas_orchestrator.orchestrate_tasks_input(plan_json, st_memory_json, lt_memory_json)
            user_message = mas_orchestrator.orchestrate_tasks_input_message(agent_input_json, plan_json, st_memory_json, lt_memory_json, st_tools)
            print("--------- inside 5")
            print(user_message)

            agent_output_json, plan_json, st_memory_json, lt_memory_json, next_task_json, next_agent_input_json = mas_orchestrator.orchestrate_tasks_output(current_task_json, agent_input_json, plan_json, st_memory_json, lt_memory_json)
            user_message = mas_orchestrator.orchestrate_tasks_output_message(agent_output_json, plan_json, st_memory_json, lt_memory_json, st_tools)
            print(user_message)

            while True:
                current_task_json, agent_input_json, plan_json, st_memory_json, lt_memory_json = mas_orchestrator.orchestrate_tasks_input_loop(agent_output_json, plan_json, st_memory_json, lt_memory_json, next_task_json, next_agent_input_json)
                user_message = mas_orchestrator.orchestrate_tasks_input_message(agent_input_json, plan_json, st_memory_json, lt_memory_json, st_tools)
                print(user_message) 
                agent_output_json, plan_json, st_memory_json, lt_memory_json, next_task_json, next_agent_input_json = mas_orchestrator.orchestrate_tasks_output_loop(current_task_json, agent_input_json, plan_json, st_memory_json, lt_memory_json)
                user_message = mas_orchestrator.orchestrate_tasks_output_message(agent_output_json, plan_json, st_memory_json, lt_memory_json, st_tools)
                print(user_message)
                completion_keys = ["Overall_execution_of_the_plan", "Overall execution of the plan"]
                completion_statuses = ["complete", "completed", "successful"]

                # Initialize plan_status
                plan_status = ""
                
                plan_json1 = json.loads(plan_json)

                # Check for 'Overall execution of the plan' at the top level of plan3
                for key in completion_keys:
                    if key in plan_json1:
                        plan_status = plan_json1[key].lower()
                        break
                if plan_status in completion_statuses:
                    print("Plan execution completed.")
                    final_output = mas_orchestrator.summarize_final_output(plan_json, st_memory_json, lt_memory_json, st_tools)
                    print(final_output)
                    break
        #-------------- Input selection - industry, use case, user_query -------------
