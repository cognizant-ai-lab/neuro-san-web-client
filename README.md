# agent_network_web_client
A web client for agent-networks built using the Neuro AI agent framework (neuro-san)

## Installation

```bash
# Installs neuro-san and its dependencies. Assumes you have credentials.
pip install -r requirements.txt
```

## Generate an HTML agent network diagram
Generate an HTML diagram of agents based on a .hocon file containing an agent network configuration:

```bash
python -m utils.agents_diagram_builder --input_file <path_to_hocon_file> --output_file <path_to_output_file>
````

For example, for a `onec_assistant.hocon` file:
```bash
python -m utils.agents_diagram_builder --input_file /Users/754337/workspace/neuro-san-1c/registries/onec_assistant.hocon --output_file ./web_client/static/onec_assistant.html
````

## Start the web client
Start the application with:
```bash
python -m web_client.app
```
Then go to http://127.0.0.1:5432 in your browser.

In the Configuration tab, choose an Agent Network Name, e.g. "onec_assistant".
This agent network name should match
- the name of a `.html` file in the `web_client/static` directory
- the name of the `.hocon` file used when starting the `neuro-san` server. 
Then click the "update" button to update the Agent Network Diagram.

The .html file must match the .hocon file network used by the `neuro-san` server.

You can now type your message in the chat box and press 'Send' to interact with the agent network.