from typing import Any
from typing import Dict

from flask import Flask, render_template, request, session
from flask import redirect
from flask import url_for
from flask_socketio import SocketIO
from neuro_san.client.streaming_input_processor import StreamingInputProcessor
from neuro_san.session.service_agent_session import ServiceAgentSession
import threading
import argparse
import os

# Initialize a lock
user_sessions_lock = threading.Lock()
user_sessions = {}

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key
socketio = SocketIO(app, async_mode='eventlet')

# Default configuration
DEFAULT_CONFIG = {
    'server_host': 'localhost',
    'server_port': 30011,
    'web_client_port': 5001,
    'agent_name': 'telco_network_support',
    'thinking_file': '/tmp/agent_thinking.txt',
    'thinking_dir': '/tmp'
}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Update configuration based on user input
        session['server_host'] = request.form.get('host', app.config.get('server_host'))
        session['server_port'] = int(request.form.get('port', app.config.get('server_port')))
        session['agent_name'] = request.form.get('agent_name', app.config.get('agent_name'))
        # Initialize agent session with new config
        session['agent_session'] = None
        # Redirect to the index page to avoid form resubmission messages on refresh
        return redirect(url_for('index'))

    return render_template('index.html',
                           agent_name=session.get('agent_name', app.config['agent_name']),
                           host=session.get('server_host', app.config['server_host']),
                           port=session.get('server_port', app.config['server_port']))


# noinspection PyUnresolvedReferences
@socketio.on('user_input')
def handle_user_input(data):
    user_input = data.get('message')
    sly_data = data.get('sly_data')

    # Get the Socket.IO session ID
    sid = request.sid

    # Retrieve or initialize user-specific data
    with user_sessions_lock:
        user_data = user_sessions.get(sid)
        if not user_data:
            # Use the current session values for agent configuration
            host = session.get('server_host', app.config['server_host'])
            port = session.get('server_port', app.config['server_port'])
            agent_name = session.get('agent_name', app.config['agent_name'])
            agent_session = ServiceAgentSession(
                host=host,
                port=port,
                agent_name=agent_name
            )
            input_processor = StreamingInputProcessor(default_input = "",
                                                      thinking_file = DEFAULT_CONFIG['thinking_file'],
                                                      session = agent_session,
                                                      thinking_dir = DEFAULT_CONFIG['thinking_dir'])
            state: Dict[str, Any] = {
                "last_logs": [],
                "last_chat_response": None,
                "prompt": "Default prompt",
                "timeout": None,  # No input time out - users can take their time
                "num_input": 0,
                "user_input": user_input,
                "sly_data": sly_data,
            }
            user_data = {
                'input_processor': input_processor,
                'state': state
            }
            user_sessions[sid] = user_data
        else:
            input_processor = user_data['input_processor']
            state = user_data['state']
            # Update user input in state
            state["user_input"] = user_input

    state = input_processor.process_once(state)
    user_data['state'] = state
    last_chat_response = state.get("last_chat_response")

    # Start a background task and pass necessary data
    socketio.start_background_task(target=background_response_handler, chat_response=last_chat_response, sid=sid)


# noinspection PyUnresolvedReferences
@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    with user_sessions_lock:
        if sid in user_sessions:
            del user_sessions[sid]
    print(f"Client disconnected: {sid}")


def background_response_handler(chat_response: str, sid):
        socketio.emit('agent_response', {'message': chat_response}, room=sid)


def clear_thinking_file():
    # Clear out the previous thinking file
    #
    # Incorrectly flagged as destination of Path Traversal 5
    #   Reason: thinking_file was previously checked with FileOfClass.check_file()
    #           which actually does the path traversal check. CheckMarx does not
    #           recognize pathlib as a valid library with which to resolve these kinds
    #           of issues.  Furthermore, this is a client command line tool that is never
    #           used inside servers which just happens to be part of a library offering.
    with open(DEFAULT_CONFIG['thinking_file'], "w", encoding="utf-8") as thinking:
        thinking.write("\n")


def parse_args():
    """
    Parses command-line arguments for server and agent configuration.
    Priority order:
    1. Command-line arguments (highest priority)
    2. Environment or local variables (medium priority)
    3. Default values from `DEFAULT_CONFIG` (fallback)
    """
    parser = argparse.ArgumentParser(description="Configure the Neuro SAN web client and server.")

    parser.add_argument('--server-host', type=str,
                        default=os.getenv("NEURO_SAN_SERVER_HOST", DEFAULT_CONFIG['server_host']),
                        help="Host address for the Neuro SAN server")
    parser.add_argument('--server-port', type=int,
                        default=int(os.getenv("NEURO_SAN_SERVER_PORT", DEFAULT_CONFIG['server_port'])),
                        help="Port number for the Neuro SAN server")
    parser.add_argument('--web-client-port', type=int,
                        default=int(os.getenv("NEURO_SAN_WEB_CLIENT_PORT", DEFAULT_CONFIG['web_client_port'])),
                        help="Port number for the web client")
    parser.add_argument('--agent-name', type=str,
                        default=os.getenv("NEURO_SAN_AGENT_NAME", DEFAULT_CONFIG['agent_name']),
                        help="Agent name for the session")

    args, _ = parser.parse_known_args()

    config = vars(args)

    print(f"Starting app with Configuration: {config}")
    return config

if __name__ == '__main__':
    config = parse_args()
    # Store config in Flask app for later use
    # Items can be accessed anywhere in Flask routes e.g. using app.config['agent_name']
    app.config.update(config)
    clear_thinking_file()
    # Start the app with the parsed configuration
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=config['web_client_port'])
