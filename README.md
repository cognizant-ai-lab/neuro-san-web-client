# agent_network_web_client
A web client for agent-networks built using the Neuro AI agent framework

This client currently depends on the leaf-common and unileaf libraries.
Make sure unileaf is in the PYTHONPATH

## Installation
```bash
pip install -r requirements.txt

# pip install leaf-common from your local checkout
pip install -e ../leaf-common
# Or install a specific version:
# pip install git+https://${LEAF_SOURCE_CREDENTIALS}@github.com/leaf-ai/leaf-common.git@1.2.10

# Add unileaf to your PYTHONPATH
export PYTHONPATH=$PYTHONPATH:../unileaf
```
## Usage
Start the application with:
```bash
python ./web_client/app.py
```
Then go to http://127.0.0.1:5432 in your browser.

In the Configuration tab, choose an Agent Network Name, e.g. "intranet_agents".
This agent network name should match
- the name of the `.html` file in the `web_client/static` directory
- the name of the `.hocon` file
in the `backend/agents/registries` directory of the `unileaf repo.
Then click "update" button to update the Agent Network Diagram.

The .html file must match the .hocon file network. If not, regenerate the .html file. TODO

You can now type your message in the chat box and press 'Send' to interact with the agent network.