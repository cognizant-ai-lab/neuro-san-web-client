# Neuro SAN Web Client

A basic web client for [Neuro SAN](https://github.com/cognizant-ai-lab/neuro-san) agent-networks integrated with [Neuro SAN Studio](https://github.com/cognizant-ai-lab/neuro-san-studio). This is a simple example showing how to connect to
a neuro-san server and interact with it.

## Installation

```bash
# Installs neuro-san and its dependencies. Assumes you have credentials.
pip install -r requirements.txt
```


## Start the web client

Start the application with:

```bash
python -m neuro_san_web_client.app
```

Then go to http://127.0.0.1:5001 in your browser.

## Usage

1. Expand the `Configuration` tab at the bottom of the interface to connect to the neuro-san server host and port
2. Choose an Agent Network Name, e.g. `industry/telco_network_support.hocon` 
   This Agent Network Name **MUST** match the name of an agent network served by the neuro-san server, i.e. it is activated in its `registries/manifest.hocon` file.
    > **Warning:** `app.py` assumes the neuro-san server serves files from a `neuro-san-studio` folder at the same level as this folder. If that's not the case, please update the `PATH_TO_NEURO_SAN_REGISTRIES` variable in `app.py` accordingly.
3. Click `Update`. A html diagram of the agent network will be automatically generated in the `neuro_san_web_client/static` directory.
4. Type your message in the chat box and press 'Send' to interact with the agent network.
5. Optional: open the `Agent Network Diagram` tab to visualize the interactions between the agents.
6. Optional: open the `Agent Communications` tab to see the messages exchanged between the agents.

## Manually generating an HTML agent network diagram

Generate an HTML diagram of agents based on a .hocon file containing an agent network configuration:

```bash
python -m neuro_san_web_client.agents_diagram_builder --input_file <path_to_hocon_file>
````

There is also an optional `--output_file <path_to_output_file>` argument to specify the output file. 
By default, if no --output_file argument is specified,
the .html file is automatically generated in the web client's static directory.

For example, for a `industry/telco_network_support.hocon` file:

```bash
python -m neuro_san_web_client.agents_diagram_builder --input_file /Users/username/workspace/neuro-san-studio/registries/industry/telco_network_support.hocon
````

is equivalent to:

```bash
python -m neuro_san_web_client.agents_diagram_builder --input_file /Users/username/workspace/neuro-san-studio/registries/industry/telco_network_support.hocon --output_file ./neuro_san_web_client/static/industry/telco_network_support.html
````
