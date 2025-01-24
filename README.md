# Neuro SAN Web Client
A web client for agent-networks built using the Neuro AI agent framework (neuro-san)

## Installation

```bash
# Installs neuro-san and its dependencies. Assumes you have credentials.
pip install -r requirements.txt
```

## Generate an HTML agent network diagram
Generate an HTML diagram of agents based on a .hocon file containing an agent network configuration:

```bash
python -m neuro_san_web_client.agents_diagram_builder --input_file <path_to_hocon_file>
````
There is also an optional `--output_file <path_to_output_file>` argument to specify the output file. 
By default, if no --output_file argument is specified,
the .html file is automatically generated in the web client's static directory.

For example, for a `intranet_agents.hocon` file:

```bash
python -m neuro_san_web_client.agents_diagram_builder --input_file /Users/754337/workspace/neuro-san/registries/intranet_agents.hocon
````

is equivalent to:

```bash
python -m neuro_san_web_client.agents_diagram_builder --input_file /Users/754337/workspace/neuro-san/registries/intranet_agents.hocon --output_file ./neuro_san_web_client/static/intranet_agents.html
````

## Start the web client
Start the application with:
```bash
python -m neuro_san_web_client.app
```
Then go to http://127.0.0.1:5432 in your browser.

In the Configuration tab, choose an Agent Network Name, e.g. "intranet_agents".
This agent network name should match
- the name of a `.html` file in the `neuro_san_web_client/static` directory
- the name of the `.hocon` file used when starting the `neuro-san` server. 
Then click the "update" button to update the Agent Network Diagram.

The .html file must match the .hocon file network used by the `neuro-san` server.

You can now type your message in the chat box and press 'Send' to interact with the agent network.
