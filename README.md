# 🎮 Multi-Agent Playground

Welcome to the **Multi-Agent Playground**! This project showcases sophisticated multi-agent systems utilizing any LLM model to demonstrate dynamic planning, orchestration, and adaptability across industries and use cases.

The diagram below shows the multi-agent process:

![multi-agent process](agent_anim_v2.gif)

The repository has learning purposes. Feel free to adapt to your own needs.

## 🛠️ Key Features

- 🔄 **Dynamic Agent Creation**: Automatically creates agents based on industry and use case (Agent Swarm).
- 📡 **Function Calling & RAG Simulation**: Simulates function calling and Retrieval-Augmented Generation (RAG), dynamically generating synthetic data for each agent.
- ⚙️ **Advanced Agentic Capabilities**: Exhibits multi-agent system features such as:
  - Multi-step logic
  - Dynamic planning & orchestration
  - Task decomposition
  - Short-term & long-term memory usage
  - Error recovery
  - Inter-agent communication
  - Domain adaptability

  ## 📝 Instructions</span>

1. 🔑 **Enter your Azure API key, model name, and endpoint**: You can use the provided key for testing if needed.
2. 🏢 **Input industry and use case**: Enter an industry, a use case and the overall query from the user and click **Submit** to begin the process.
3. 📊 **Monitor the orchestration**: 
   - The **right sidebar** displays the orchestration and planning in action, showing the agents involved in completing the task.
   - The **middle section** visualizes agent communication and information exchange.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Streamlit
- Azure OpenAI API key

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Azure-Samples/agent-playground
    cd agent-playground
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

### Quickstart

1. Run the application:
    ```sh
    streamlit run main.py
    ```

2. Enter your Azure API key, model name, and endpoint. You can also define the environment variables in the [.env](.env.sample) file (Replace .env.sample to .env).

3. Input industry and use case, then enter the overall query from the user and click **Submit** to begin the process.

## Usage

### Monitoring the Orchestration

- The **right sidebar** displays the orchestration and planning in action, showing the agents involved in completing the task.
- The **middle section** visualizes agent communication and information exchange.

## Demo

A demo app is included to show how to use the project.

To run the demo, follow these steps:

1. Ensure you have completed the installation steps.
2. Run the application using `streamlit run main.py`.
3. Follow the instructions provided in the **Quickstart** section.

## Contributing

This project welcomes contributions and suggestions. Please read the [CONTRIBUTING.md](http://_vscodecontentref_/0) file for guidelines on how to contribute.

## License

This project is licensed under the MIT License. See the [LICENSE.md](http://_vscodecontentref_/1) file for more details.

## Resources

- [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- [Microsoft Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
- Contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with questions or concerns.

Thank you for using the Multi-Agent Playground! We hope you find it useful and engaging.
