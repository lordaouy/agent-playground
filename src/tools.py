import json, base64
import streamlit as st
import streamlit.components.v1 as components

class StreamlitTools:
    def __init__(self, plan_json, st_memory):
        self.plan_json = plan_json
        self.st_memory = st_memory
        self.status_colors = {
            "": "#FFC107",               # Pending - Yellow
            "Pending": "#FFC107",
            "In Progress": "#FFC107",    # In Progress - Yellow
            "Successful": "#28B463",     # Successful - Green
            "Unsuccessful": "#C0392B",   # Unsuccessful - Red
            "Failed": "#C0392B",         # Failed - Red
            "Completed": "#28B463"       # Completed - Green
        }
        self.spinning_wheel_gif = "https://cdn.pixabay.com/animation/2023/10/10/13/27/13-27-45-28_512.gif"

    def generate_sidebar(self):
        html = self._generate_html_header()
        tasks = self._load_tasks()
        sorted_tasks = self._sort_tasks(tasks)
        task_counter = 1

        for task_key in sorted_tasks:
            task = self._find_task(tasks, task_key)
            task_name = task.get("Task", "Unnamed Task")
            subtasks = task.get("Sub_Tasks", [])
            subtasks_statuses = [subtask.get("Subtask_Status", "") for subtask in subtasks]
            task_status = task.get("Task_Status", "Pending")
            task_banner_color = self._determine_task_banner_color(task_status)
            task_status_color = self._determine_task_status_color(subtasks_statuses)

            html += self._generate_task_card(task_counter, task_banner_color, task_status_color, task_name, subtasks)
            task_counter += 1

        html += "</div>"
        return html

    def _generate_html_header(self):
        return """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap">
        <style>
        .sidebar { width: 300px; height: 100vh; padding: 20px; box-sizing: border-box; overflow-y: auto; font-family: 'Inter', sans-serif; background-color: transparent; }
        .sidebar-title { font-size: 24px; font-weight: bold; text-align: center; margin-bottom: 20px; background-color: transparent; }
        .task-card { background-color: #FFFFFF; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; transition: transform 0.3s; display: flex; flex-direction: column; }
        .task-card:hover { transform: translateY(-5px); }
        .task-banner { padding: 8px; text-align: center; font-size: 14px; font-weight: bold; border-radius: 8px 8px 0 0; }
        .task-content { padding: 15px; flex: 1; display: flex; flex-direction: column; }
        .task-header { display: flex; align-items: center; margin-bottom: 8px; }
        .task-name { flex: 1; font-size: 13px; font-weight: bold; }
        .subtasks { list-style: none; padding: 0; margin: 0; }
        .subtask { margin-bottom: 8px; position: relative; }
        .subtask:last-child { margin-bottom: 0; }
        .subtask .status-and-agent { display: flex; align-items: center; }
        .subtask .agent-name { font-size: 12px; color: #1E90FF; font-weight: bold; }
        .subtask .subtask-name { font-size: 12px; margin-left: 20px; margin-top: 2px; }
        .status { width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
        .status-gif { width: 24px; height: 24px; margin-right: 8px; }
        .tooltip { position: relative; display: block; }
        .tooltip .tooltiptext { visibility: hidden; width: 220px; background-color: #555; color: #fff; text-align: left; border-radius: 6px; padding: 8px; position: absolute; z-index: 1; left: 105%; top: 50%; transform: translateY(-50%); opacity: 0; transition: opacity 0.3s; }
        .tooltip:hover .tooltiptext { visibility: visible; opacity: 1; }
        .sidebar::-webkit-scrollbar { width: 8px; }
        .sidebar::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
        .sidebar::-webkit-scrollbar-thumb { background: #1B4F72; border-radius: 4px; }
        .task-footer { font-size: 10px; text-align: center; padding: 8px; background-color: #90EE90; border-radius: 0 0 8px 8px; }
        </style>
        <div class="sidebar">
        """

    def _load_tasks(self):
        plan_json1 = json.loads(self.plan_json)
        return plan_json1.get("Tasks", [])

    def _sort_tasks(self, tasks):
        return [task['Task'] for task in tasks if 'Task' in task]

    def _find_task(self, tasks, task_key):
        return next((task for task in tasks if task['Task'] == task_key), {})

    def _determine_task_banner_color(self, task_status):
        if task_status == "Successful":
            return "#28B463"  # Green
        elif task_status == "In Progress":
            return "#FFC107"  # Yellow
        else:
            return "#F5F5DC"  # Beige Yellow

    def _determine_task_status_color(self, subtasks_statuses):
        if all(status == "Successful" for status in subtasks_statuses) and subtasks_statuses:
            return self.status_colors.get("Successful", "#28B463")  # Green
        elif any(status in ["Failed", "Unsuccessful"] for status in subtasks_statuses):
            return self.status_colors.get("Failed", "#C0392B")  # Red
        elif any(status == "In Progress" for status in subtasks_statuses):
            return self.status_colors.get("In Progress", "#FFC107")  # Yellow
        else:
            return self.status_colors.get("Pending", "#FFC107")  # Yellow

    def _generate_task_card(self, task_counter, task_banner_color, task_status_color, task_name, subtasks):
        html = f"""
            <div class="task-card">
                <div class="task-banner" style="background-color: {task_banner_color};">Task {task_counter}</div>
                <div class="task-content">
                    <div class="task-header">
                        <span class="status" style="background-color: {task_status_color};"></span>
                        <div class="task-name">{task_name}</div>
                    </div>
                    <ul class="subtasks">
        """
        for subtask in subtasks:
            subtask_name = subtask.get("Sub_Task", "Unnamed Subtask")
            agent_name = subtask.get("Agent", "No Agent")
            function = subtask.get("Agent_Function", "No Function")
            subtask_status = subtask.get("Subtask_Status", "")
            status_html = self._determine_status_html(subtask_status)
            tooltip_content = self._generate_tooltip_content(subtask, agent_name, function)

            html += f"""
                    <li class="subtask tooltip">
                        <div class="status-and-agent">
                            {status_html}
                            <div class="agent-name">{agent_name}:</div>
                        </div>
                        <div class="subtask-name">{subtask_name}</div>
                        <span class="tooltiptext">{tooltip_content}</span>
                    </li>
            """
        html += """
                </ul>
        """
        html += f"""
                    </div>
                        <div class="task-footer"><strong>Memory</strong><br>{subtask.get('Sub_Task_Output_Observation', 'N/A')}</div>
                    </div>
        """
        return html

    def _determine_status_html(self, subtask_status):
        if subtask_status == "In Progress":
            return f'<img src="{self.spinning_wheel_gif}" alt="In Progress" class="status-gif">'
        elif subtask_status == "Successful":
            return f'<span class="status" style="background-color: {self.status_colors.get("Successful", "#28B463")};"></span>'
        elif subtask_status in ["Failed", "Unsuccessful"]:
            return f'<span class="status" style="background-color: {self.status_colors.get("Failed", "#C0392B")};"></span>'
        else:
            return f'<span class="status" style="background-color: {self.status_colors.get("Pending", "#FFC107")};"></span>'

    def _generate_tooltip_content(self, subtask, agent_name, function):
        return f"""
            <strong>Agent:</strong> {agent_name}<br>
            <strong>Function:</strong> {function}<br>
            <strong>Output:</strong> {subtask.get('Sub_Task_Output', 'N/A')}<br>
            <strong>Observation:</strong> {subtask.get('Sub_Task_Output_Observation', 'N/A')}
        """
    
class GeneralTools:
    def __init__(self):
        pass

    # Function to convert GIF to base64 string  
    def get_gif_as_base64(file_path):  
        with open(file_path, "rb") as gif_file:  
            gif_base64 = base64.b64encode(gif_file.read()).decode("utf-8")  
        return gif_base64  
