from flask import Flask, render_template, request, session
from flask_socketio import SocketIO
from neuro_san.session.service_agent_session import ServiceAgentSession
import json
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
    'neuro_san_server_host': 'localhost',
    'neuro_san_server_port': 30011,
    'neuro_san_web_client_port': 5001,
    'neuro_san_agent_name': 'telco_network_support',
    'thinking_file': '/tmp/agent_thinking.txt'
}


# Use this method to ensure session persistence
def get_agent_session():
    """Retrieves or initializes the agent session with the correct configuration values."""
    if 'agent_session' not in session:
        # Use session variables only within request context
        host = session.get('server_host', app.config['server_host'])
        port = session.get('server_port', app.config['server_port'])
        agent_name = session.get('agent_name', app.config['agent_name'])
        session['agent_session'] = ServiceAgentSession(
            host=host,
            port=port,
            agent_name=agent_name
        )
    return session['agent_session']


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Update configuration based on user input
        session['server_host'] = request.form.get('host', app.config.get('server_host'))
        session['server_port'] = int(request.form.get('port', app.config.get('server_port')))
        session['agent_name'] = request.form.get('agent_name', app.config.get('agent_name'))
        # Initialize agent session with new config
        session['agent_session'] = None

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
            session_id = None
            user_data = {
                'agent_session': agent_session,
                'session_id': session_id,
                'last_logs_length': 0  # Initialize logs length
            }
            user_sessions[sid] = user_data
        else:
            agent_session = user_data['agent_session']
            session_id = user_data['session_id']

    chat_request = {
        'session_id': session_id,
        'user_input': user_input
    }

    if sly_data:
        chat_request['sly_data'] = json.loads(sly_data)

    chat_response = agent_session.chat(chat_request)
    print(f"chat_response: {chat_response}")

    if not session_id:
        session_id = chat_response.get('session_id')
        user_data['session_id'] = session_id

    # Start a background task and pass necessary data
    socketio.start_background_task(target=background_response_handler, sid=sid)


# noinspection PyUnresolvedReferences
@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    with user_sessions_lock:
        if sid in user_sessions:
            del user_sessions[sid]
    print(f"Client disconnected: {sid}")


def background_response_handler(sid):
    while True:
        # Retrieve user-specific data
        with user_sessions_lock:
            user_data = user_sessions.get(sid)
        if not user_data:
            print(f"No user data found for sid {sid}")
            return

        agent_session = user_data['agent_session']
        session_id = user_data['session_id']
        last_logs_length = user_data.get('last_logs_length', 0)

        logs_request = {'session_id': session_id}
        logs_response = agent_session.logs(logs_request)

        # Get logs and chat response
        logs = logs_response.get('logs', [])
        chat_response = logs_response.get('chat_response')

        # Emit new logs to the client
        new_logs = logs[last_logs_length:]
        for log in new_logs:
            socketio.emit('agent_log', {'log': log}, room=sid)
        last_logs_length = len(logs)

        # Update last_logs_length in user_data
        with user_sessions_lock:
            user_data['last_logs_length'] = last_logs_length

        # **Print chat_response for debugging**
        print(f"chat_response: {chat_response}")

        # Check if assistant's response is available
        if chat_response:
            # Extract the part after the last 'assistant: ' keyword
            last_response = chat_response.rsplit('assistant: ', 1)[-1]
            socketio.emit('agent_response', {'message': last_response}, room=sid)
            break  # Exit the loop after sending the response

        # Sleep before the next poll to prevent excessive requests
        socketio.sleep(1)

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
                        default=os.getenv("NEURO_SAN_SERVER_HOST", DEFAULT_CONFIG['neuro_san_server_host']),
                        help="Host address for the Neuro SAN server")
    parser.add_argument('--server-port', type=int,
                        default=int(os.getenv("NEURO_SAN_SERVER_PORT", DEFAULT_CONFIG['neuro_san_server_port'])),
                        help="Port number for the Neuro SAN server")
    parser.add_argument('--web-client-port', type=int,
                        default=int(os.getenv("NEURO_SAN_WEB_CLIENT_PORT", DEFAULT_CONFIG['neuro_san_web_client_port'])),
                        help="Port number for the web client")
    parser.add_argument('--agent-name', type=str,
                        default=os.getenv("NEURO_SAN_AGENT_NAME", DEFAULT_CONFIG['neuro_san_agent_name']),
                        help="Agent name for the session")

    args, _ = parser.parse_known_args()

    config = vars(args)

    print(f"Starting app with Configuration: {config}")
    return config

if __name__ == '__main__':
    config = parse_args()
    # Store config in Flask app for later use
    # Items can be accessed anywhere in Flask routes e.g. using app.config['neuro_san_agent_name']
    app.config.update(config)
    # Start the app with the parsed configuration
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=config['web_client_port'])
